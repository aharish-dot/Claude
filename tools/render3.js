const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const [,, inPath, outPath, headerLabel, orientation, footerSpan] = process.argv;
  const landscape = orientation === 'landscape';
  const fspan = footerSpan || 'Compilation Digest';
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(inPath), { waitUntil: 'networkidle' });
  const header = `
    <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;width:100%;padding:0 14mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
      <div style="text-align:center;letter-spacing:.14em;text-transform:uppercase;border-bottom:.5px solid #c9d3df;padding-bottom:4px;">${headerLabel}</div>
    </div>`;
  const footer = `
    <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;width:100%;padding:0 14mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
      <div style="display:flex;justify-content:space-between;border-top:.5px solid #c9d3df;padding-top:4px;">
        <span>Section 135 Digest &middot; ${fspan}</span>
        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
      </div>
    </div>`;
  await page.pdf({
    path: outPath, format: 'A4', landscape, printBackground: true,
    displayHeaderFooter: true, headerTemplate: header, footerTemplate: footer,
    margin: { top: '20mm', bottom: '15mm', left: '14mm', right: '14mm' }
  });
  await browser.close();
  console.log('WROTE', outPath);
})().catch(e => { console.error(e); process.exit(1); });
