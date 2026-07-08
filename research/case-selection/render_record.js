const { chromium } = require('playwright');
(async () => {
  const htmlPath = process.argv[2];
  const pdfPath = htmlPath.replace(/\.html$/, '.pdf');
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage();
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' });
  await page.pdf({ path: pdfPath, format: 'A4', printBackground: true });
  await browser.close();
  console.log('wrote', pdfPath);
})();
