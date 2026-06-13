"""Shared helpers for AICC plugin hooks.

Hooks receive a JSON event on stdin and may reply with a JSON object on
stdout. All hooks must never crash the session: callers wrap entry points
and fall back to the per-event robustness contract (see BUILD_NOTES.md).
"""

import json
import os
import sys

DEFAULT_SETTINGS = {
    "documentLanguage": "en",
    "enableMutualReview": True,
    "enforceDesignThinking": False,
    "git_safety": {
        "mode": "standard",
        "commit_gate": "ask",
        "protected_branches": ["main", "master", "production"],
    },
    "planReview": {
        "gate": "ask",
        "complexityThreshold": "medium",
        "highRiskSurfaces": [
            "auth", "payment", "data-schema", "migration",
            "external-API", "privacy-secrets", "concurrency", "breaking-change",
        ],
    },
}


def plugin_root():
    """Resolve the plugin root (env in real sessions, path-relative in tests)."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if root:
        return root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_event():
    """Parse the hook event JSON from stdin; return {} on malformed input."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _deep_merge(base, override):
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _read_aicc_block(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        block = data.get("aicc", {})
        return block if isinstance(block, dict) else {}
    except (OSError, json.JSONDecodeError, AttributeError):
        return {}


def load_settings(cwd=None):
    """Effective settings: defaults < plugin settings.json < project .claude/settings.json < env.

    Env overrides (for tests and one-off runs):
      AICC_COMMIT_GATE=ask|deny|off, AICC_GIT_SAFETY_MODE=standard|strict|permissive
    """
    settings = dict(DEFAULT_SETTINGS)
    settings = _deep_merge(settings, _read_aicc_block(os.path.join(plugin_root(), "settings.json")))
    project_dir = cwd or os.getcwd()
    settings = _deep_merge(settings, _read_aicc_block(os.path.join(project_dir, ".claude", "settings.json")))
    settings = _deep_merge(settings, _read_aicc_block(os.path.join(project_dir, ".claude", "settings.local.json")))

    gate = os.environ.get("AICC_COMMIT_GATE")
    if gate in ("ask", "deny", "off"):
        settings["git_safety"]["commit_gate"] = gate
    mode = os.environ.get("AICC_GIT_SAFETY_MODE")
    if mode in ("standard", "strict", "permissive"):
        settings["git_safety"]["mode"] = mode
    return settings


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=True))
    sys.stdout.flush()


def pretooluse_decision(decision, reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
