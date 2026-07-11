// Memo / interpretive-note renderer (sibling of render2.js).
// Header reads "<eyebrow> · <scope>" so an analytical note is not mislabelled a "Judgment Digest".
// Usage: node tools/render_note.js <in.html> <out.pdf> <footerTag> <eyebrow> <scope>
const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const [,, inPath, outPath, footerTag, eyebrowArg, scopeArg] = process.argv;
  const eyebrow = eyebrowArg || 'Interpretive Note';
  const scope = scopeArg || '';
  const tag = footerTag || 'Interpretive Note';
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(inPath), { waitUntil: 'networkidle' });
  const header = `
    <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;width:100%;padding:0 17mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
      <div style="text-align:center;letter-spacing:.16em;text-transform:uppercase;border-bottom:.5px solid #c9d3df;padding-bottom:4px;">
        ${eyebrow}${scope ? ' &nbsp;&middot;&nbsp; ' + scope : ''}
      </div></div>`;
  const footer = `
    <div style="font-family:Arial,'Liberation Sans',sans-serif;font-size:7.6px;color:#6b7787;width:100%;padding:0 17mm;box-sizing:border-box;-webkit-print-color-adjust:exact;">
      <div style="display:flex;justify-content:space-between;border-top:.5px solid #c9d3df;padding-top:4px;">
        <span>${tag}</span>
        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
      </div></div>`;
  await page.pdf({ path: outPath, format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: header, footerTemplate: footer,
    margin: { top: '23mm', bottom: '17mm', left: '17mm', right: '17mm' } });
  await browser.close();
  console.log('WROTE', outPath);
})().catch(e => { console.error(e); process.exit(1); });
