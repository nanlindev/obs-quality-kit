<?php
/**
 * Plugin Name: OBS Quality Kit — correlation header (WP SME pilot)
 * Description: Adds X-Correlation-Id on HTML responses after WP is installed. /obs-health is a standalone path (../obs-health).
 * Version: 0.1.1
 *
 * Note: wp_not_installed() runs before mu-plugins, so health cannot live only here.
 */

if (!defined('ABSPATH')) {
    exit;
}

function obs_kit_ensure_correlation_id(): string
{
    $incoming = $_SERVER['HTTP_X_CORRELATION_ID'] ?? $_SERVER['HTTP_CORRELATION_ID'] ?? '';
    $incoming = is_string($incoming) ? trim($incoming) : '';
    if ($incoming !== '' && preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i', $incoming)) {
        return strtolower($incoming);
    }
    $data = random_bytes(16);
    $data[6] = chr((ord($data[6]) & 0x0f) | 0x40);
    $data[8] = chr((ord($data[8]) & 0x3f) | 0x80);
    return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
}

function obs_kit_send_correlation_header(): void
{
    if (headers_sent()) {
        return;
    }
    header('X-Correlation-Id: ' . obs_kit_ensure_correlation_id());
}

add_action('send_headers', 'obs_kit_send_correlation_header', 0);
