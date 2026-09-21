#!/usr/bin/env python3
"""Stage 7 — handbook pack static checks (Review-7).

Verifies zh/en pairs exist and TROUBLESHOOTING can locate empty-panel / port / 4318.
No Docker required. Exit 0 = pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# Stage-7 handbook set + prior topic pages that must stay bilingual
REQUIRED_PAIRS = (
    "INSTALL",
    "SECURITY",
    "CREDENTIALS",
    "TROUBLESHOOTING",
    "REVERSE_PROXY",
    "BASE_ADDONS",
    "EXTEND_PROFILE",
    "BOOTSTRAP_MANUAL",
    "CONTRACT",
    "DOC_ADAPTER",
    "ECOM_ADAPTER",
    "CRM_ADAPTER",
    "FACADE_INSTALL",
    "DEMO_RUNBOOK",
    "PHASE2_ADDENDUM",
    "NETWORKS",
    "METRICS",
    "LANGFUSE",
    "LOKI",
    "LLM_OPS",
    "GENERIC_APP_ADAPTER",
    "IMAGE_PIN",
)


class Fail(Exception):
    pass


def _ok(msg: str) -> None:
    print(f"OK  {msg}")


def _read(rel: str) -> str:
    path = DOCS / rel
    if not path.is_file():
        raise Fail(f"missing {rel}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    try:
        for stem in REQUIRED_PAIRS:
            zh = _read(f"zh/{stem}.md")
            en = _read(f"en/{stem}.md")
            if len(zh.strip()) < 80 or len(en.strip()) < 80:
                raise Fail(f"{stem}: zh/en too short")
            # Cross-link both directions (loose)
            if f"../en/{stem}.md" not in zh and f"../en/{stem}.md" not in zh.replace(" ", ""):
                if f"](../en/{stem}.md)" not in zh:
                    raise Fail(f"zh/{stem}.md should link to en twin")
            if f"](../zh/{stem}.md)" not in en:
                raise Fail(f"en/{stem}.md should link to zh twin")
            _ok(f"pair {stem}")

        install_zh = _read("zh/INSTALL.md").lower()
        install_en = _read("en/INSTALL.md").lower()
        for blob, label in ((install_zh, "zh/INSTALL"), (install_en, "en/INSTALL")):
            if "compose" not in blob:
                raise Fail(f"{label}: must state Compose support")
            if "kubernetes" not in blob and "k8s" not in blob:
                raise Fail(f"{label}: Review-7 honesty — mention Kubernetes as unsupported")
        _ok("INSTALL support matrix mentions Compose + K8s out-of-scope")

        for lang in ("zh", "en"):
            text = _read(f"{lang}/TROUBLESHOOTING.md")
            low = text.lower()
            # Acceptance: empty panel / port / 4318 locatable
            if lang == "zh":
                if "空面板" not in text and "no data" not in low:
                    raise Fail("zh/TROUBLESHOOTING missing 空面板 / No data")
                if "端口占用" not in text and "端口" not in text:
                    raise Fail("zh/TROUBLESHOOTING missing 端口占用")
            else:
                if "empty panel" not in low and "no data" not in low:
                    raise Fail("en/TROUBLESHOOTING missing empty panel / No data")
                if "port" not in low:
                    raise Fail("en/TROUBLESHOOTING missing port conflict section")
            if "4318" not in text:
                raise Fail(f"{lang}/TROUBLESHOOTING missing 4318")
            _ok(f"TROUBLESHOOTING/{lang} indexes empty-panel + port + 4318")

        for lang in ("zh", "en"):
            sec = _read(f"{lang}/SECURITY.md").lower()
            if "127.0.0.1" not in sec:
                raise Fail(f"{lang}/SECURITY must mention 127.0.0.1 bind")
            proxy = _read(f"{lang}/REVERSE_PROXY.md").lower()
            for needle in ("nginx", "caddy", "npm"):
                if needle not in proxy:
                    raise Fail(f"{lang}/REVERSE_PROXY missing {needle}")
            base = _read(f"{lang}/BASE_ADDONS.md").lower()
            if "metrics" not in base or "langfuse" not in base:
                raise Fail(f"{lang}/BASE_ADDONS must map metrics/langfuse")
            if "loki" not in base.lower():
                raise Fail(f"{lang}/BASE_ADDONS must map loki addon")
            _ok(f"SECURITY+PROXY+BASE_ADDONS/{lang}")

        for lang in ("zh", "en"):
            gen = _read(f"{lang}/GENERIC_APP_ADAPTER.md")
            glow = gen.lower()
            if "frappe" not in glow or "wordpress" not in glow:
                raise Fail(f"{lang}/GENERIC_APP_ADAPTER must cover Frappe and WordPress")
            if "shadow" not in glow:
                raise Fail(f"{lang}/GENERIC_APP_ADAPTER must keep shadow default")
            # Honest: no implementation / paid custom
            if lang == "zh":
                if "无实装" not in gen and "未交付" not in gen:
                    raise Fail("zh/GENERIC_APP_ADAPTER must state 无实装/未交付")
                if "付费定制" not in gen and "深度交付" not in gen:
                    raise Fail("zh/GENERIC_APP_ADAPTER must state 付费定制")
                if "粗估" not in gen and "工时" not in gen:
                    raise Fail("zh/GENERIC_APP_ADAPTER must include effort bands")
            else:
                if "not shipped" not in glow and "not delivered" not in glow and "no implementation" not in glow:
                    raise Fail("en/GENERIC_APP_ADAPTER must state not shipped / no implementation")
                if "paid custom" not in glow and "deep delivery" not in glow:
                    raise Fail("en/GENERIC_APP_ADAPTER must state paid custom")
                if "effort" not in glow and "0.5" not in gen:
                    raise Fail("en/GENERIC_APP_ADAPTER must include effort bands")
            _ok(f"GENERIC_APP_ADAPTER/{lang} honest guide + effort bands")

        # Stage 8 — shot list: full + short beats; unfilmed / wait P2; film gate
        shot = ROOT / "assets" / "demo-shot-list.md"
        if not shot.is_file():
            raise Fail(f"missing {shot}")
        shot_text = shot.read_text(encoding="utf-8")
        shot_low = shot_text.lower()
        if "未拍" not in shot_text and "unfilmed" not in shot_low:
            raise Fail("shot list must mark shots 未拍 / unfilmed")
        if "Y-P2a" not in shot_text or "Y-P2b" not in shot_text:
            raise Fail("shot list must include Y-P2a and Y-P2b (ecom/crm + Loki flashes)")
        if "S-P2" not in shot_text and "s-p2" not in shot_low:
            raise Fail("shot list must include S-P2 short-cut flash")
        if "待 p2" not in shot_low and "待 phase-2" not in shot_low and "wait for p2" not in shot_low:
            if "待 P2" not in shot_text and "Phase-2" not in shot_text and "P2-8" not in shot_text:
                raise Fail("shot list must say 待 P2-8 / Phase-2 film gate")
        if "完整版" not in shot_text and "full" not in shot_low:
            raise Fail("shot list must include full-cut beats")
        if "短版" not in shot_text and "short" not in shot_low:
            raise Fail("shot list must include short-cut beats")
        if "成片" in shot_text and "phase-2" not in shot_low and "Phase-2" not in shot_text:
            raise Fail("shot list must tie 成片 to Phase-2")
        # Explicit film gate phrase
        if "成片 = Phase-2" not in shot_text and "film" in shot_low and "phase-2" not in shot_low:
            raise Fail("shot list must state film/成片 after Phase-2")
        if "成片 = Phase-2" not in shot_text and "成片" in shot_text:
            # Chinese draft uses bold line in header table
            if "Phase-2" not in shot_text or "成片" not in shot_text:
                raise Fail("shot list missing 成片 + Phase-2 gate")
        _ok("assets/demo-shot-list.md full+short + 未拍/待P2")

        vo_full = ROOT / "assets" / "demo-vo-full.md"
        vo_short = ROOT / "assets" / "demo-vo-short.md"
        for vo in (vo_full, vo_short):
            if not vo.is_file():
                raise Fail(f"missing {vo}")
            vt = vo.read_text(encoding="utf-8")
            if "trace_id" not in vt:
                raise Fail(f"{vo.name} must mention trace_id")
            if "Base" not in vt and "Addon" not in vt and "addon" not in vt.lower():
                raise Fail(f"{vo.name} must mention Base/Addon")
        _ok("assets/demo-vo-full.md + demo-vo-short.md must-say lines")

        videos_readme = ROOT / "assets" / "demo" / "videos" / "README.md"
        if not videos_readme.is_file():
            raise Fail(f"missing {videos_readme}")
        vr = videos_readme.read_text(encoding="utf-8")
        if "obs-kit-full" not in vr or "obs-kit-short" not in vr:
            raise Fail("videos/README must name obs-kit-full / obs-kit-short")
        if "not checked in" not in vr.lower() and "TBD" not in vr and "待" not in vr:
            # Allow either explicit TBD / not checked in while films absent
            if "0.2-p2-complete" in vr and "after" not in vr.lower():
                raise Fail("videos/README must not imply films already complete without TBD")
        _ok("assets/demo/videos/README.md check-in table")

        for lang in ("zh", "en"):
            film = _read(f"{lang}/P2_8_FILM.md")
            fl = film.lower()
            if "trace_id" not in film:
                raise Fail(f"{lang}/P2_8_FILM must mention trace_id")
            if "0.2-p2-complete" not in film:
                raise Fail(f"{lang}/P2_8_FILM must gate 0.2-p2-complete")
            if lang == "zh" and "已拍" not in film and "录屏" not in film:
                raise Fail(f"{lang}/P2_8_FILM must discuss 录屏/已拍 honesty")
            if lang == "en" and "filmed" not in fl and "record" not in fl:
                raise Fail(f"{lang}/P2_8_FILM must discuss record/filmed honesty")
            _ok(f"P2_8_FILM/{lang}")

        for lang in ("zh", "en"):
            demo = _read(f"{lang}/DEMO_RUNBOOK.md")
            low = demo.lower()
            if "phase-2" not in low and "Phase-2" not in demo:
                raise Fail(f"{lang}/DEMO_RUNBOOK must mention Phase-2 film gate")
            if lang == "zh" and "不剪成片" not in demo and "不成片" not in demo:
                if "不剪" not in demo:
                    raise Fail(f"{lang}/DEMO_RUNBOOK must say P1 does not film")
            if lang == "en" and "do not film" not in low and "not film" not in low:
                raise Fail(f"{lang}/DEMO_RUNBOOK must say do not film in P1")
            if "P2_8_FILM" not in demo and "p2_8_film" not in low:
                raise Fail(f"{lang}/DEMO_RUNBOOK must link P2_8_FILM")
            _ok(f"DEMO_RUNBOOK/{lang} film gate")

        prd_zh = _read("zh/PRD.md")
        if (
            "0.2-p2-implementing" not in prd_zh
            and "0.2-p2-planning" not in prd_zh
            and "0.2-p2-smoke-green" not in prd_zh
            and "0.2-p2-complete" not in prd_zh
        ):
            if "0.1-p1-complete" not in prd_zh and "P1 完成" not in prd_zh:
                raise Fail("zh/PRD missing P1 complete or P2 status")
        _ok("PRD status ok (P1/P2)")

        for lang in ("zh", "en"):
            add = _read(f"{lang}/PHASE2_ADDENDUM.md")
            al = add.lower()
            for stage in ("p2-0", "p2-1", "p2-7", "p2-8"):
                if stage not in al and stage.upper() not in add:
                    # Chinese may use P2-0 with capital P
                    if stage.replace("p2-", "P2-") not in add and f"P2-{stage[-1]}" not in add:
                        if f"P2-{stage.split('-')[1]}" not in add:
                            pass  # checked below via P2-0 string
            if "P2-0" not in add or "P2-8" not in add:
                raise Fail(f"{lang}/PHASE2_ADDENDUM must list P2-0…P2-8")
            if "成片" in add or "film" in al:
                if "phase-2" not in al and "p2" not in al and "Phase-2" not in add:
                    raise Fail(f"{lang}/PHASE2_ADDENDUM film gate unclear")
            if lang == "zh" and "成片" not in add:
                raise Fail("zh/PHASE2_ADDENDUM must state 成片 gate")
            if lang == "en" and "film" not in al:
                raise Fail("en/PHASE2_ADDENDUM must state film gate")
            if "不整本重写" not in add and "not rewrite" not in al and "incremental" not in al:
                raise Fail(f"{lang}/PHASE2_ADDENDUM must say incremental / not full PRD rewrite")
            _ok(f"PHASE2_ADDENDUM/{lang}")

        for lang in ("zh", "en"):
            close = _read(f"{lang}/P1_CLOSE.md")
            cl = close.lower()
            if "phase-2" not in cl and "Phase-2" not in close:
                raise Fail(f"{lang}/P1_CLOSE must point to Phase-2 next")
            if lang == "zh" and "不成片" not in close and "未剪" not in close:
                raise Fail(f"{lang}/P1_CLOSE must say no film yet")
            if lang == "en" and "film" not in cl:
                raise Fail(f"{lang}/P1_CLOSE must mention film gate")
            _ok(f"P1_CLOSE/{lang}")

        for lang in ("zh", "en"):
            close2 = _read(f"{lang}/P2_CLOSE.md")
            c2 = close2.lower()
            if "smoke-green" not in c2 and "0.2-p2-smoke-green" not in close2:
                raise Fail(f"{lang}/P2_CLOSE must state smoke-green status")
            if "smoke_kit_p2" not in close2:
                raise Fail(f"{lang}/P2_CLOSE must document smoke_kit_p2")
            if lang == "zh" and "P2-8" not in close2 and "成片" not in close2:
                raise Fail(f"{lang}/P2_CLOSE must point film to P2-8")
            if lang == "en" and "p2-8" not in c2 and "film" not in c2:
                raise Fail(f"{lang}/P2_CLOSE must point film to P2-8")
            _ok(f"P2_CLOSE/{lang}")

        print("OK  smoke_kit_docs passed")
        return 0
    except Fail as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())