// Synthetic screenshot inside a disposable runner; never attach to a user browser.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const req = createRequire(path.join(process.env.PW_ROOT, 'package.json'));
const {chromium} = req('playwright-core');
const browser=await chromium.launch({headless:true,timeout:20000});
try {
  const context=await browser.newContext({offline:true,viewport:{width:1000,height:650}});
  const page=await context.newPage();
  await page.setContent('<html><body style="font:24px sans-serif;padding:48px"><h1>Cron Master Sandbox</h1><p>Isolated browser smoke test</p><p>No personal data. No real scheduler access.</p><p id="result">Browser render: PASS</p></body></html>',{timeout:10000});
  if(await page.locator('#result').textContent() !== 'Browser render: PASS') throw new Error('Render mismatch');
  fs.mkdirSync('reports',{recursive:true});
  await page.screenshot({path:'reports/sandbox-browser.png'});
  console.log(JSON.stringify({scope:'isolated-browser-smoke',passed:true,user_browser_attached:false}));
} finally { await browser.close(); }
