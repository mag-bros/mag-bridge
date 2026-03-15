const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  try {
    // Connect to the running Electron app via CDP
    const browser = await chromium.connectOverCDP('http://localhost:9222');
    const defaultContext = browser.contexts()[0];
    const page = defaultContext.pages()[0];
    
    // Wait for Angular to attach to the DOM to prevent blank white screens
    await page.waitForSelector('app-root', { state: 'attached', timeout: 10000 });
    
    // Ensure the output directory exists
    if (!fs.existsSync('.claude/tmp')) {
      fs.mkdirSync('.claude/tmp', { recursive: true });
    }
    
    await page.screenshot({ path: '.claude/tmp/latest_ui.png', fullPage: true });
    await browser.close();
    
    console.log('SUCCESS: Screenshot saved to .claude/tmp/latest_ui.png');
  } catch (err) {
    console.error('ERROR capturing screenshot:', err.message);
    process.exit(1);
  }
})();