/**
 * Totaux fournée — private live totals page for Jill and Michel.
 *
 * Google Apps Script web app (script.google.com, owned by Jill). Each view:
 *   1. asks Notion for the Current fournée (Status = Current),
 *   2. reads its Orders sheet (Michel's Sheet) with Jill's Google access,
 *   3. counts orders and products with the same rules as Make 🔥 4
 *      (product names = the Sheet's column headings, not Notion),
 *   4. shows counts only: no names, no emails.
 *
 * Costs nothing in Make. The Notion token lives in Script properties
 * (NOTION_TOKEN), never in this file. The web app URL is not in the repo.
 * Setup and update steps: scripts/totaux-fournee/README.md.
 */

// ─── ONE-TIME SETUP ──────────────────────────────────────────────────────
// 1. Replace COLLER_LE_JETON_ICI below with the Notion token (keep the quotes).
// 2. At the top of the editor, choose « saveNotionToken » and click Run.
// It stores the token in Script properties and shows the totals in the log.
// Claude then puts the placeholder back (clasp push), so the token never stays here.
var NOTION_TOKEN_TO_SAVE = 'COLLER_LE_JETON_ICI';

function saveNotionToken() {
  var t = NOTION_TOKEN_TO_SAVE.trim();
  if (t === 'COLLER_LE_JETON_ICI' || t === '') throw new Error('Collez d’abord le jeton Notion entre les guillemets.');
  PropertiesService.getScriptProperties().setProperty('NOTION_TOKEN', t);
  Logger.log('Jeton enregistré.');
  testTotals();
}
// ─────────────────────────────────────────────────────────────────────────

var FOURNEES_DS ='a8371f42-bc05-443e-9548-77f29e0387a4';
var NOTION_VERSION = '2025-09-03';
// Columns that are not products (🔥 4 counts them as 0).
var FIXED_COLUMNS = ['Date', 'Source', 'Nom', 'Prénom', 'Email', 'Téléphone', 'Total', 'Remarques'];
var COLUMNS_READ = 16; // 🔥 4 reads A–P only.

function doGet() {
  var data;
  try {
    data = loadTotals_();
  } catch (e) {
    data = { error: String(e && e.message || e) };
  }
  var t = HtmlService.createTemplateFromFile('Index');
  t.d = data;
  t.url = ScriptApp.getService().getUrl();
  return t.evaluate()
    .setTitle('Totaux fournée')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .addMetaTag('apple-mobile-web-app-capable', 'yes')
    .addMetaTag('mobile-web-app-capable', 'yes')
    .setFaviconUrl('https://www.fourdebottens.ch/apple-touch-icon.png');
}

function loadTotals_() {
  var fournees = currentFournees_();
  if (fournees.length === 0) return { error: 'Aucune fournée « Current » dans Notion.' };
  var p = fournees[0].properties;
  var sheetUrl = p['Orders sheet'] && p['Orders sheet'].url;
  if (!sheetUrl) return { error: 'La fournée Current n’a pas encore de tableau de commandes.' };
  var id = sheetUrl.split('/d/')[1].split('/')[0];
  var sheet = SpreadsheetApp.openById(id).getSheetByName('Sheet1');
  var last = Math.max(sheet.getLastRow(), 3);
  var top = sheet.getRange(1, 1, 2, 26).getValues();
  var rows = sheet.getRange(3, 1, last - 2, 26).getValues();

  var result = computeTotals(top[0], top[1], rows);
  result.date = plain_(p['date_fournée']);
  result.deadline = p['Order deadline'] && p['Order deadline'].date && p['Order deadline'].date.start;
  result.twoCurrent = fournees.length > 1;
  result.updated = Utilities.formatDate(new Date(), 'Europe/Zurich', 'dd.MM.yyyy HH:mm');
  return result;
}

/**
 * Pure: same rules as Make 🔥 4 « Daily summary to Michel ».
 * headers = row 1, totalRow = row 2 (TOTAL formulas), rows = rows 3+.
 */
function computeTotals(headers, totalRow, rows) {
  var cols = headers.slice(0, COLUMNS_READ).map(function (h) { return String(h).trim(); });
  var orders = 0, site = 0, sums = {};
  rows.forEach(function (row) {
    var cells = row.slice(0, COLUMNS_READ);
    if (cells.every(function (c) { return String(c).trim() === ''; })) return; // empty row
    orders++;
    cols.forEach(function (h, i) {
      if (h === 'Source') {
        if (String(cells[i]).trim().toLowerCase() === 'tally') site++;
      } else if (FIXED_COLUMNS.indexOf(h) === -1) {
        sums[h] = (sums[h] || 0) + num_(cells[i]);
      }
    });
  });
  // Products = the Sheet's own column headings (A–P) that aren't fixed columns, in Sheet order.
  var products = cols.map(function (h, i) { return { name: h, i: i }; })
    .filter(function (c) { return c.name !== '' && FIXED_COLUMNS.indexOf(c.name) === -1; })
    .map(function (c) {
      return { name: c.name, qty: sums[c.name] || 0, sheetTotal: num_(totalRow[c.i]) };
    });
  return {
    orders: orders,
    site: site,
    phone: orders - site,
    products: products,
    mismatch: products.some(function (x) { return x.sheetTotal !== x.qty; })
  };
}

// A number cell counts; text counts only if it is just a number (« 2 pains » = 0).
function num_(v) {
  if (typeof v === 'number') return v;
  var s = String(v).trim().replace(/^CHF\s*/i, '').replace(/'/g, '');
  if (!/^-?\d+([.,]\d+)?$/.test(s)) return 0;
  return Number(s.replace(',', '.'));
}

function currentFournees_() {
  var token = PropertiesService.getScriptProperties().getProperty('NOTION_TOKEN');
  if (!token) throw new Error('NOTION_TOKEN manque dans les propriétés du script.');
  var res = UrlFetchApp.fetch('https://api.notion.com/v1/data_sources/' + FOURNEES_DS + '/query', {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token, 'Notion-Version': NOTION_VERSION },
    payload: JSON.stringify({ filter: { property: 'Status', status: { equals: 'Current' } }, page_size: 2 }),
    muteHttpExceptions: true
  });
  if (res.getResponseCode() !== 200) throw new Error('Notion a répondu ' + res.getResponseCode());
  return JSON.parse(res.getContentText()).results;
}

function prop_(p) {
  if (!p) return '';
  if (p.type === 'formula') return p.formula.string || '';
  return plain_(p);
}

function plain_(p) {
  if (!p || !p[p.type] || !p[p.type].map) return '';
  return p[p.type].map(function (t) { return t.plain_text; }).join('');
}

function formatDeadline_(iso) {
  if (!iso) return '';
  var d = iso.slice(0, 10).split('-');
  return d[2] + '.' + d[1] + '.' + d[0];
}

/** Run once from the editor to check setup: logs the totals (counts only). */
function testTotals() {
  Logger.log(JSON.stringify(loadTotals_(), null, 2));
}

if (typeof module !== 'undefined') module.exports = { computeTotals: computeTotals, num_: num_ };
