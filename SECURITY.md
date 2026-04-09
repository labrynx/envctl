# Security Policy

## Supported Versions

envctl is an actively maintained project. Security updates are only provided
for the latest stable release.

| Version | Supported |
| ------- | --------- |
| 2.x     | ✅        |
| < 2.0   | ❌        |

If you are using an older version, please upgrade to the latest release before
reporting a vulnerability.

---

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### 📩 How to report

- Open a **private security advisory** on GitHub (preferred), or
- Contact the maintainer directly via GitHub

Please include:

- A clear description of the issue
- Steps to reproduce (if applicable)
- Potential impact
- Suggested mitigation (if known)

---

## 🔒 What to expect

- You will receive an acknowledgment within **48 hours**
- The issue will be triaged and assessed
- If confirmed, a fix will be developed and released as soon as possible
- You may be credited in the release notes (unless you prefer to stay anonymous)

---

## ⚠️ Responsible disclosure

Please **do not** open public issues for security vulnerabilities.

This helps protect users until a fix is available.

---

## 🧠 Scope

This policy covers:

- envctl CLI
- contract resolution logic
- vault and encryption features

Out of scope:

- user misconfiguration
- issues caused by third-party tools or environments

---

## 🔐 Security philosophy

envctl is designed around a contract-first and local-first model.

- No implicit environment variable usage
- No silent fallbacks
- Explicit handling of sensitive values
- Optional encryption at rest for vault profiles

Security issues related to these guarantees are treated with high priority.

---

## Explicit limits and non-goals

The current security model is intentionally narrower than a remote secrets platform.

What envctl aims to protect against:

- accidental commitment of envctl-specific vault payloads or keys
- confusion between contract data and real secret values
- silent projection of invalid environments
- casual leakage through normal user-facing output

What envctl does not try to guarantee:

- protection against a compromised local machine or user account
- centralized access control, rotation policy, or remote audit trails
- automatic protection of generated projection artifacts like synced env files
- complete prevention of every possible secret-shaped string in Git history

Operational assumptions:

- the local machine is trusted
- contributors use the documented workflow and local hooks where expected
- encryption at rest protects vault files, not every artifact derived from them

Threats outside the current intended scope:

- host compromise
- malicious local administrator access
- remote secrets governance and approval workflows
- organization-wide incident response tooling
