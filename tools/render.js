const { chromium } = require('playwright-core');
const fs = require('fs');

(async () => {
  const [,, inPath, outPath, caseNo] = process.argv;
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    args: ['--no-sandbox']
  });
  const page = await browser.newPage();
  const html = fs.readFileSync(inPath, 'utf8');
  await page.setContent(html, { waitUntil: 'networkidle' });

  const header = `
    <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;
                width:100%;padding:0 17mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
      <div style="text-align:center;letter-spacing:.16em;text-transform:uppercase;
                  border-bottom:.5px solid #c9d3df;padding-bottom:4px;">
        Delhi District Court &nbsp;&middot;&nbsp; Judgment Digest &nbsp;&middot;&nbsp; Section 135, Electricity Act
      </div>
    </div>`;

  const footer = `
    <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;
                width:100%;padding:0 17mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
      <div style="display:flex;justify-content:space-between;border-top:.5px solid #c9d3df;padding-top:4px;">
        <span>SC No. ${caseNo} &nbsp;&middot;&nbsp; Delhi District Court</span>
        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
      </div>
    </div>`;

  await page.pdf({
    path: outPath,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: header,
    footerTemplate: footer,
    margin: { top: '23mm', bottom: '17mm', left: '17mm', right: '17mm' }
  });
  await browser.close();
  console.log('WROTE', outPath);
})().catch(e => { console.error(e); process.exit(1); });
