---
name: security-expert
description: Run security vulnerability scans using Grype. Use when scanning pip dependencies, Dockerfiles, filesystems, or generating security reports.
---

# Security Expert

Security vulnerability scanning powered by [Grype](https://github.com/anchore/grype). Scans dependencies, filesystems, and container images for known CVEs.

## Prerequisites

Grype must be installed at `bin/grype`. If missing, run the setup script:

```bash
.claude/scripts/setup-grype.sh -d ./bin
```

Verify with `bin/grype version`. Do not proceed with any scan if Grype is not installed — offer to run setup first.

## Output Format (REQUIRED)

Before running any scan, ask the user which output format they want. Do NOT assume a default — present this table and wait for their choice:

| Format | `-o` value | Description |
|---|---|---|
| Table | `table` | Human-readable terminal output |
| JSON | `json` | Machine-parsable structured report |
| CycloneDX JSON | `cyclonedx-json` | OWASP CycloneDX standard (JSON) |
| CycloneDX XML | `cyclonedx-xml` | OWASP CycloneDX standard (XML) |
| SARIF | `sarif` | Static Analysis Results Interchange Format |
| Template | `template` | Custom Go template (requires `--output-template-file`) |

Multiple formats can be specified with repeated `-o` flags (e.g. `-o table -o json=report.json`).

## Scan Types

Always use `bin/grype` (project-local binary), never a global install.

### Pip Dependencies

Scan Python requirements files for vulnerable packages:

```bash
bin/grype file:requirements.txt -o <format>
bin/grype file:requirements-dev.txt -o <format>
```

When reporting results:
- Group by severity (Critical > High > Medium > Low)
- For each vulnerability, note if a fixed version exists (`--only-fixed` flag)
- Recommend version bumps that resolve Critical/High CVEs

### Filesystem

Scan the full project directory:

```bash
bin/grype dir:. -o <format>
```

This detects vulnerabilities across all languages and package managers found in the tree.

### Container Image

Scan container images from various sources:

```bash
bin/grype docker:IMAGE_NAME -o <format>              # from Docker daemon
bin/grype podman:IMAGE_NAME -o <format>              # from Podman daemon
bin/grype registry:REPO/IMAGE:TAG -o <format>        # pull directly from registry
bin/grype docker-archive:path/to/image.tar -o <format>  # from docker save tarball
bin/grype oci-archive:path/to/image.tar -o <format>     # from OCI archive
bin/grype oci-dir:path/to/image -o <format>             # from OCI layout directory
bin/grype singularity:path/to/image.sif -o <format>     # from SIF container
```

### SBOM

Scan an existing Software Bill of Materials (Syft JSON, SPDX, or CycloneDX):

```bash
bin/grype sbom:path/to/sbom.json -o <format>
```

### Package Identifiers

Scan individual packages by PURL or from a PURL file:

```bash
bin/grype purl:path/to/purls.txt -o <format>            # newline-separated PURLs
bin/grype pkg:pypi/numpy@2.3.4 -o <format>              # single package PURL
```

## Key Flags

| Flag | Purpose |
|---|---|
| `--only-fixed` | Show only vulnerabilities with available patches |
| `--fail-on critical` | Exit non-zero if critical CVEs found |
| `--by-cve` | Group output by CVE instead of by package |
| `--severity-cutoff high` | Only show high and critical severity |

## Reports

When asked to generate a security report:

1. Run the scan with `--output json` and save to `tests/reports/security/`
2. Also run with `--output table` for the human-readable summary
3. Present a summary table to the user:
   - Total vulnerabilities by severity
   - Packages with Critical/High CVEs and their fixed versions
   - Actionable recommendations (version pins, upgrades)

Report files follow the naming convention: `grype_<target>_<YYYY-MM-DD>.json`

## Updating Requirements

When asked to secure/update requirements files:

1. Scan current requirements with `--only-fixed` to find actionable vulnerabilities
2. Check currently installed versions with `pip list`
3. For each vulnerable package with a fix available:
   - Show: package, current version, vulnerability, fixed version
   - Pin to the minimum version that resolves the CVE
4. Do NOT blindly update to latest — only bump what's needed to clear Critical/High CVEs
5. Ask the user before writing changes to requirements files
