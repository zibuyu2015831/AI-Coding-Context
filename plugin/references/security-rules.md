# Security & Redaction Rules

Generated docs quote real code — these rules keep secrets out of them.
Apply during generation and verify in the acceptance pass.

## Always redact

| sensitive value | replacement |
| --- | --- |
| API keys / tokens | `sk-abc...xyz` (keep first/last 3 chars) or `${API_KEY}` |
| Passwords / DB credentials | `********` or `process.env.DB_PASSWORD` |
| Private keys / certificates | file path + `[REDACTED]`, never the content |
| Real domains | `example.com`, `yourdomain.com`, or `${HOST}` |
| Real IPs | `192.168.x.x` / `10.0.x.x` placeholders or `${SERVER_IP}` |
| PII (names, emails, phones) | `[PII_REDACTED]` or fictional examples |
| JWTs / session tokens | `eyJ...xyz` or `[JWT_TOKEN]` |

## Rules

1. Code examples in docs must use environment variables for every secret —
   if the real code hardcodes one, the doc example shows the env-var form and
   notes the discrepancy as a finding, not a pattern to copy.
2. Deployment/config snippets use `<DB_PASSWORD>`-style placeholders, even
   when the real value is an open-source default.
3. Auto-scan generated text for the obvious patterns before writing:
   `sk-`, `eyJ`, `://user:pass@`, `BEGIN PRIVATE KEY`, AWS `AKIA` keys.
4. Self-check at acceptance: no hardcoded keys, passwords, internal domains,
   IPs, or PII anywhere in `dev_docs/`.
5. Git safety is the other half of this rule set: destructive operations
   (force push, hard reset, branch deletion) are intercepted by the plugin's
   dangerous-git guard; see the incremental-update skill.
