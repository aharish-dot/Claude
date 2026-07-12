// render_summaries_pdf.js — build a print PDF of all case summaries from data/orders.json.
// Run from the ombudsman/ dir:  node pipeline/render_summaries_pdf.js
// Output: report/ombudsman-summaries.pdf   (one case per page, bilingual)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');

const orders = JSON.parse(fs.readFileSync('data/orders.json', 'utf8'))
  .sort((a, b) => a.case_id.localeCompare(b.case_id));

const esc = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const isRelief = d => ['Merits', 'Compliance / execution'].includes(d);
const arr = v => Array.isArray(v) ? v : (v ? [v] : []);
const list = v => arr(v).filter(Boolean).map(esc).join(' · ') || '—';

function scBlock(o) {
  const d = arr(o.supply_code_detail);
  if (d.length) return d.map(x => `<li><b>${esc(x.clause)}</b> — ${esc(x.note)}</li>`).join('');
  return `<li class="none">No specific clause cited (the order refers to the Supply Code only in general terms, or not at all).</li>`;
}

const overview = orders.map(o => `<tr>
  <td class="mono">${esc(o.case_id)}</td>
  <td class="mono">${esc(o.representation_no)}</td>
  <td>${esc(o.primary_subject)}</td>
  <td><span class="chip ${isRelief(o.decided_on) ? 're' : 'th'}">${isRelief(o.decided_on) ? 'relief' : 'threshold'}</span></td>
  <td>${esc(o.disposition)}</td>
</tr>`).join('');

const cases = orders.map((o, i) => `
<section class="case ${isRelief(o.decided_on) ? 're' : 'th'}" style="break-before:page">
  <div class="chead">
    <div class="cid">${esc(o.case_id)}<span>Representation ${esc(o.representation_no)}</span></div>
    <span class="chip ${isRelief(o.decided_on) ? 're' : 'th'}">${isRelief(o.decided_on) ? 'reached relief' : 'threshold'}</span>
  </div>
  <div class="meta">${esc(o.discom)} &middot; ${esc(o.district)} &middot; ${esc(o.order_date)} &middot; before ${esc(o.ombudsman)}</div>
  <div class="consumer"><b>Consumer:</b> ${esc(o.petitioner)} — ${esc(o.consumer_segment)}${o.tariff_category && o.tariff_category !== 'not named' ? ', ' + esc(o.tariff_category) : ''}${o.sanctioned_load && !/not stated/i.test(o.sanctioned_load) ? ', ' + esc(o.sanctioned_load) : ''} · ${esc(o.connection_type)}</div>

  <h3>Summary</h3>
  <p>${esc(o.summary_en)}</p>
  <h3>सारांश <span class="hlabel">(Hindi)</span></h3>
  <p class="hi">${esc(o.summary_hi)}</p>

  <div class="grid">
    <div class="field"><span class="k">Decided on</span><span class="v">${esc(o.decided_on)} → <b>${esc(o.disposition)}</b></span></div>
    <div class="field"><span class="k">Amount</span><span class="v">${esc(o.amount_in_dispute) || '—'}</span></div>
  </div>

  <div class="sc">
    <span class="k">U.P. Electricity Supply Code, 2005</span>
    <ul>${scBlock(o)}</ul>
  </div>

  <div class="field"><span class="k">Also cited</span><span class="v">EA 2003 §${list(o.act_sections)} &nbsp;·&nbsp; Regs ${list(o.regulations_cited)} &nbsp;·&nbsp; Precedent ${list(o.precedents_cited)}</span></div>
  <div class="field"><span class="k">Ratio</span><span class="v">${esc(o.ratio_short)}</span></div>
  <div class="tags">${arr(o.tags).map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>
  ${o.ocr_confidence && o.ocr_confidence.length > 40 ? `<div class="prov"><b>Provenance:</b> ${esc(o.ocr_confidence)}</div>` : ''}
</section>`).join('');

const css = `
  :root{ --ink:#1b1a17; --ink2:#4a463e; --muted:#7a756c; --line:#e3ded4;
    --th:#9c6320; --re:#0e7a60; --accent:#3b4aa0;
    --serif:"Liberation Serif","DejaVu Serif",Georgia,"Times New Roman",serif;
    --sans:"DejaVu Sans","Liberation Sans",system-ui,sans-serif;
    --deva:"Lohit Devanagari","Samyak Devanagari","Noto Sans Devanagari",sans-serif;
    --mono:"DejaVu Sans Mono",monospace; }
  *{box-sizing:border-box}
  body{margin:0;color:var(--ink);font-family:var(--serif);font-size:10.5pt;line-height:1.5;}
  .cover{border-bottom:2px solid var(--ink);padding-bottom:12px;margin-bottom:16px;}
  .eyebrow{font-family:var(--mono);font-size:8pt;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 4px;}
  h1{font-family:var(--serif);font-size:22pt;margin:0 0 4px;font-weight:700;}
  .cover .sub{color:var(--ink2);font-size:11pt;margin:0 0 8px;}
  .cover .meta{font-family:var(--mono);font-size:8pt;color:var(--muted);}
  h2{font-family:var(--serif);font-size:12pt;margin:16px 0 6px;font-weight:700;}
  table{width:100%;border-collapse:collapse;font-size:9pt;margin-bottom:4px;}
  th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top;}
  th{font-family:var(--mono);font-size:7.5pt;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--ink2);}
  .mono{font-family:var(--mono);font-size:8.5pt;white-space:nowrap;}
  .chip{display:inline-block;font-family:var(--mono);font-size:7pt;letter-spacing:.05em;text-transform:uppercase;
    padding:2px 7px;border-radius:9px;color:#fff;}
  .chip.th{background:var(--th);} .chip.re{background:var(--re);}
  .case{padding-top:6px;border-left:3px solid var(--th);padding-left:14px;}
  .case.re{border-left-color:var(--re);}
  .chead{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3px;}
  .cid{font-family:var(--mono);font-size:13pt;font-weight:700;}
  .cid span{display:block;font-size:8.5pt;font-weight:400;color:var(--muted);margin-top:1px;}
  .meta{font-family:var(--mono);font-size:8pt;color:var(--muted);margin-bottom:8px;}
  .consumer{font-size:10pt;margin-bottom:6px;}
  h3{font-family:var(--mono);font-size:8pt;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);
    margin:12px 0 3px;font-weight:700;}
  h3 .hlabel{color:var(--muted);text-transform:none;letter-spacing:0;}
  p{margin:0 0 6px;text-align:justify;}
  p.hi{font-family:var(--deva);font-size:11pt;line-height:1.65;background:#faf7f0;border:1px solid var(--line);
    border-radius:6px;padding:8px 10px;text-align:left;}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:4px 18px;margin:8px 0;}
  .field{margin:5px 0;}
  .k{display:block;font-family:var(--mono);font-size:7.5pt;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);}
  .v{display:block;font-size:9.5pt;}
  .sc{margin:8px 0;padding:8px 10px;background:#f6f8fb;border:1px solid var(--line);border-radius:6px;}
  .sc ul{margin:4px 0 0;padding-left:18px;} .sc li{margin:2px 0;font-size:9.5pt;}
  .sc li.none{list-style:none;margin-left:-18px;color:var(--muted);font-style:italic;}
  .tags{margin-top:8px;}
  .tag{display:inline-block;font-family:var(--mono);font-size:7pt;color:var(--ink2);background:#efece5;
    border-radius:8px;padding:2px 7px;margin:0 4px 4px 0;}
  .prov{margin-top:8px;font-size:8pt;color:var(--muted);line-height:1.4;text-align:justify;
    border-top:1px dotted var(--line);padding-top:5px;}
`;

const today = new Date().toISOString().slice(0, 10);
const relief = orders.filter(o => isRelief(o.decided_on)).length;
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><style>${css}</style></head><body>
  <div class="cover">
    <p class="eyebrow">UPERC · Electricity Ombudsman, Uttar Pradesh</p>
    <h1>Case Summaries — ${orders.length} Orders (2026)</h1>
    <p class="sub">Condensed bilingual digests, one order per page, generated from the coded corpus.</p>
    <p class="meta">Generated ${today} · adjudicator: Sanjay Srivastava · outcome split: ${relief} reached relief / ${orders.length - relief} disposed at the threshold · source: OCR of scanned bilingual orders — search-grade, not citation-grade.</p>
  </div>
  <h2>Overview</h2>
  <table><thead><tr><th>ID</th><th>Representation</th><th>Primary subject</th><th>Track</th><th>Disposition</th></tr></thead>
  <tbody>${overview}</tbody></table>
  ${cases}
</body></html>`;

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newContext().then(c => c.newPage());
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.pdf({
    path: 'report/ombudsman-summaries.pdf', format: 'A4', printBackground: true,
    margin: { top: '20mm', bottom: '16mm', left: '15mm', right: '15mm' },
    displayHeaderFooter: true,
    headerTemplate: `<div style="font:7pt 'DejaVu Sans';color:#999;width:100%;padding:0 15mm;text-align:right;">Electricity Ombudsman, U.P. — Case Summaries</div>`,
    footerTemplate: `<div style="font:7pt 'DejaVu Sans';color:#999;width:100%;padding:0 15mm;text-align:center;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>`,
  });
  await browser.close();
  console.log('wrote report/ombudsman-summaries.pdf');
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
