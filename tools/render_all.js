const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');
(async () => {
  const manifest = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const header = `
    <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;width:100%;padding:0 17mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
      <div style="text-align:center;letter-spacing:.16em;text-transform:uppercase;border-bottom:.5px solid #c9d3df;padding-bottom:4px;">
        Delhi District Court &nbsp;&middot;&nbsp; Judgment Digest &nbsp;&middot;&nbsp; Section 135, Electricity Act
      </div></div>`;
  for (const [inPath, outPath, label] of manifest) {
    await page.goto('file://' + path.resolve(inPath), { waitUntil: 'networkidle' });
    const footer = `
      <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;width:100%;padding:0 17mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
        <div style="display:flex;justify-content:space-between;border-top:.5px solid #c9d3df;padding-top:4px;">
          <span>${label} &nbsp;&middot;&nbsp; Delhi District Court</span>
          <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
        </div></div>`;
    await page.pdf({ path: outPath, format: 'A4', printBackground: true, displayHeaderFooter: true,
      headerTemplate: header, footerTemplate: footer,
      margin: { top: '23mm', bottom: '17mm', left: '17mm', right: '17mm' } });
    console.log('WROTE', path.basename(outPath));
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
