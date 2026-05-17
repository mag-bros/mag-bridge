---
name: electron-qa
description: Visually verifies the running Electron application. Use this after ANY edit to Angular HTML, CSS, or TS files to ensure zero-code developer experience.
---

# Remote Debugging UI Verification
        
The Electron application is running in the background on port 9222 (CDP). To verify your UI changes:
1. Execute the command: `node scripts/claude-screenshot.js`
2. Use your native image/file reading capabilities to analyze `.claude/tmp/latest_ui.png`.
3. Verify that the Angular layout rendered correctly inside the Electron window and no visual regressions occurred.
4. If the script returns an error, ensure the `dev` script is currently running.
