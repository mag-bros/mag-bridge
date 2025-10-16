# 📄 Open-Source License Attribution — Implementation Guide

## 🎯 Purpose  
> [!NOTE] Ensure compliance with all open-source licenses for components distributed or installed by our setup.  
This covers **GNU Make**, **Chocolatey**, **Node.js**, **npm**, and **Electron**, meeting MIT, Apache 2.0, GPLv3, and Artistic 2.0 obligations.

Only clear **attribution** and **license availability** are required.

## 💡 Why It’s Important
Proper attribution:

- Satisfies MIT, Apache, GPL, and Artistic 2.0 license requirements.
- Protects us from license violations and legal exposure.
- Keeps the project transparent and audit-ready.

> [!NOTE] This satisfies MIT, Apache, GPL, and Artistic 2.0 requirements — all of which only demand clear attribution and availability.

## 🧾 TODO: Check Licenses of All Dependencies
> [!NOTE] Run a license audit for every dependency before packaging.

```bash
npm install -g license-checker
license-checker --summary --production
```

---

### 🧩 Fragment 4 — License Manifest Template
## 📚 Third-Party Licenses
> [!NOTE] Include the following verified license statements in  
`Windows/THIRD_PARTY_LICENSES.txt`.

```markdown
────────────────────────────────────────────────
Chocolatey Community Edition
───────────────────────────────────────────────────────────────
Licensed under the Apache License, Version 2.0
© Chocolatey Software, Inc.
https://community.chocolatey.org/

───────────────────────────────────────────────────────────────
Node.js
───────────────────────────────────────────────────────────────
Licensed under the MIT License
© Node.js contributors
https://nodejs.org/

───────────────────────────────────────────────────────────────
npm CLI
───────────────────────────────────────────────────────────────
Licensed under the Artistic License 2.0
© npm, Inc. and Contributors
https://www.npmjs.com/

───────────────────────────────────────────────────────────────
Electron
───────────────────────────────────────────────────────────────
Licensed under the MIT License
© OpenJS Foundation and Contributors
https://www.electronjs.org/
```

---
## 📦 Distribution Rule
- Every distributed package must include the full license manifest.

> [!NOTE] Full third-party license texts are available in:
> <install_dir>\Windows\THIRD_PARTY_LICENSES.txt. 
> If packaged as a self-extracting installer, ensure this file is extracted  
> and remains visible or accessible post-installation.


## ⚙️ Add License Reference to Installer
> [!NOTE] Reference the license file in the PowerShell installer.

```powershell
$licensePath = Join-Path $PSScriptRoot "Windows\THIRD_PARTY_LICENSES.txt"
```

---

### 🧩 Fragment 7 — Final Compliance Checklist
## ✅ Compliance Checklist

| Task | Status | Notes |
|------|---------|-------|
| Verify all dependencies with `license-checker` | ☐ | |
| Update `Windows/THIRD_PARTY_LICENSES.txt` | ☐ | |
| Reference license file in installer UI | ☐ | |
| Test that file is accessible post-install | ☐ | |
| Add new dependencies with verified license info | ☐ | |

> [!NOTE] Once all boxes are checked, the installer is compliant.
