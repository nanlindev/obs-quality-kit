#!/usr/bin/env bash
# One-shot WP install for the SME pilot (title = local service marketing site).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "→  ensuring wp-sme containers are up"
docker compose -f compose.yml up -d

echo "→  waiting for WordPress HTTP"
for _ in $(seq 1 60); do
  code="$(curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:8087/obs-health/ || true)"
  if [[ "$code" == "200" ]]; then
    break
  fi
  sleep 2
done

echo "→  wp core is-installed?"
if docker compose -f compose.yml run --rm --entrypoint bash wordpress -c \
  'curl -sS -o /tmp/wp-cli.phar https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && php /tmp/wp-cli.phar --allow-root --path=/var/www/html core is-installed'; then
  echo "OK  already installed"
  exit 0
fi

echo "→  wp core install (Acme Local Services)"
docker compose -f compose.yml run --rm --entrypoint bash wordpress -c '
  set -e
  curl -sS -o /tmp/wp-cli.phar https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
  php /tmp/wp-cli.phar --allow-root --path=/var/www/html core install \
    --url="http://127.0.0.1:8087" \
    --title="Acme Local Services" \
    --admin_user="admin" \
    --admin_password="admin_local_only" \
    --admin_email="admin@example.local" \
    --skip-email
'
echo "OK  WP SME installed — UI http://127.0.0.1:8087 (admin / admin_local_only)"
