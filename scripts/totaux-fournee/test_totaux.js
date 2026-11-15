// Fake rows only. Run: node scripts/totaux-fournee/test_totaux.js
const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(require("path").join(__dirname,"Code.gs"),'utf8');const m={exports:{}};
vm.runInNewContext(src,{module:m});const {computeTotals}=m.exports;
const H=['Date','Source','Nom','Prénom','Email','Téléphone','Pain Gros-de-Vaud','Grande tresse','Petite tresse','St-Nicolas','Total','Remarques'];
const T=['','','TOTAL','','','',1,5,3,5,'',''];
const rows=[
 [new Date(),'Tally','a','b','c','',1,2,3,4,41.5,''],
 ['','téléphone','x','','','079',0,3,'',1,'',''],
 ['','','','','','','','','','','',''],
 ['','Tally','y','','','','', '2 pains','',0,'CHF 12.00',''],
];
const pl='01|qty_pain_gdv|Pain Gros-de-Vaud|4.5,04|qty_st_nicolas|St-Nicolas|4,03|qty_tresse_petite|Petite tresse|3,02|qty_tresse_grande|Grande tresse|6';
const r=computeTotals(H,T,rows,pl);console.log(JSON.stringify(r));
const ok=r.orders===3&&r.site===2&&r.phone===1&&r.chf===undefined&&r.products.map(p=>p.name+':'+p.qty).join()==='Pain Gros-de-Vaud:1,Grande tresse:5,Petite tresse:3,St-Nicolas:5'&&!r.mismatch;
console.log(ok?'PASS':'FAIL');process.exit(ok?0:1);
