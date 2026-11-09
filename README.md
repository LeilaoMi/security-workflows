# security-workflows

Reusable GitHub Actions security scans shared by all LeilaoMi repos.

| Workflow | What it does | Caller permissions |
|---|---|---|
| `gitleaks.yml` | Secret scan: PR/push range + full history + working tree, SARIF to code scanning | `contents: read`, `pull-requests: read`, `security-events: write` |
| `semgrep.yml` | SAST (`--config auto`), report-only, SARIF to code scanning | `contents: read`, `security-events: write` |
| `trivy.yml` | Dependency vulns (fs) + Dockerfile/IaC misconfig (config), report-only | `contents: read`, `security-events: write` |

## Usage

```yaml
# .github/workflows/security.yml in a caller repo
name: Security
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read
jobs:
  gitleaks:
    permissions: { contents: read, pull-requests: read, security-events: write }
    uses: LeilaoMi/security-workflows/.github/workflows/gitleaks.yml@<sha> # v1
  semgrep:
    permissions: { contents: read, security-events: write }
    uses: LeilaoMi/security-workflows/.github/workflows/semgrep.yml@<sha> # v1
```

Pin to a commit SHA; Dependabot (`github-actions` ecosystem) bumps it.
Per-repo gitleaks allowlists go in the caller's `.gitleaks.toml` and must keep `[extend] useDefault = true`.
