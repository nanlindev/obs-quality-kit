<?php
/**
 * Standalone health endpoint (no WP bootstrap).
 * Served as a real path so Apache does not rewrite through index.php.
 * Needed because wp_not_installed() redirects before mu-plugins load.
 */
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

$raw = getenv('OBS_QUALITY_GATE_MODE');
if ($raw === false || $raw === '') {
    $raw = 'shadow';
}
$key = strtolower(trim((string) $raw));
$mode = in_array($key, ['block', 'hard', 'enforce'], true) ? 'block' : 'shadow';

$incoming = $_SERVER['HTTP_X_CORRELATION_ID'] ?? $_SERVER['HTTP_CORRELATION_ID'] ?? '';
$incoming = is_string($incoming) ? trim($incoming) : '';
if ($incoming !== '' && preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i', $incoming)) {
    $corr = strtolower($incoming);
} else {
    $data = random_bytes(16);
    $data[6] = chr((ord($data[6]) & 0x0f) | 0x40);
    $data[8] = chr((ord($data[8]) & 0x3f) | 0x80);
    $corr = vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
}

header('X-Correlation-Id: ' . $corr);
http_response_code(200);

echo json_encode(
    [
        'status' => 'ok',
        'service' => 'wp-sme-pilot',
        'obs_quality_gate_mode' => $mode,
        'obs_quality_gate_blocks_writes' => ($mode === 'block'),
        'correlation_id' => $corr,
        'trace_id' => null,
        'pilot' => 'obs-kit-wp-sme',
        'notes' => 'Standalone /obs-health (pre-install safe). Logs via Docker→Promtail→Loki. OTLP/Jaeger = custom next step.',
    ],
    JSON_UNESCAPED_SLASHES
);
