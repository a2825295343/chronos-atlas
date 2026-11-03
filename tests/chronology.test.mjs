import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {baseColor} from '../src/colors.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const cache=new Map();
function at(year){const c=Math.floor(year/100);if(!cache.has(c))cache.set(c,read(`public/data/temporal/${c}.geojson`));return activePolities(cache.get(c),year);}
const owners=(year,point)=>at(year).features.filter(f=>pointInGeometry(point,f.geometry)).map(f=>f.properties.NAME);

test('1371 separates Ming, Northern Yuan and Yunnan remnants, with annual conquest transitions',()=>{
 for(let y=1368;y<=1401;y++){
  const fs=at(y).features;
  assert.ok(!fs.some(f=>f.properties.NAME==='Yuan Dynasty'||f.properties.qid==='Q7313'),String(y));
  assert.deepEqual(owners(y,[116.4,39.9]),['Ming Dynasty'],`${y} Beijing`);
  assert.deepEqual(owners(y,[118.8,32]),['Ming Dynasty'],`${y} Nanjing`);
  assert.deepEqual(owners(y,[106.9,47.9]),['Northern Yuan'],`${y} Mongolian plateau`);
 }
 for(const [y,point,name]of [[1368,[104.1,30.6],'Ming Xia'],[1370,[104.1,30.6],'Ming Xia'],[1371,[104.1,30.6],'Ming Dynasty'],[1381,[102.7,25],'Yuan remnants in Yunnan'],[1382,[102.7,25],'Ming Dynasty'],[1368,[108.9,34.3],'Northern Yuan'],[1369,[108.9,34.3],'Ming Dynasty']])assert.deepEqual(owners(y,point),[name],`${y}: ${point}`);
 const index=read('public/data/temporal/index.json');for(const y of [1368,1369,1370,1371,1382,1387,1911,1915,1919,1921,1924])assert.ok(index.changeYears.includes(y),String(y));
});

test('modern Mongolia never becomes Yuan, and China is a state rather than a party',()=>{
 for(let y=1911;y<=1925;y++){
  const fs=at(y).features;
  assert.ok(!fs.some(f=>f.properties.qid==='Q7313'),`${y} Yuan identity`);
  assert.deepEqual(owners(y,[106.9,47.9]),[y>=1924?"Mongolian People's Republic":y>=1919&&y<=1920?'Chinese administration in Outer Mongolia':'Bogd Khanate of Mongolia']);
 }
 assert.deepEqual(owners(1923,[116.4,39.9]),['Republic of China']);
 for(const point of [[123.43,41.8],[126.63,45.75],[121,49],[123,50]])assert.deepEqual(owners(1923,point),['Republic of China'],'northeastern China is not unrecorded land');
 const china=at(1923).features.find(f=>f.properties.NAME==='Republic of China');assert.equal(china.properties.qid,'Q13426199');assert.match(china.properties.accuracy,/军阀/);
 for(const name of ['Bogd Khanate of Mongolia',"Mongolian People's Republic",'Mongolia'])assert.equal(baseColor(name),baseColor('Mongolia'));
});

test('global reviewed identities respect their own dates, including Europe, Americas and West Asia',()=>{
 const cases=[[-100,'Roman Republic','Q17167'],[2000,'Syria','Q858'],[2000,'Luxembourg','Q32'],[900,'Strathclyde','Q225890'],[1500,'Michoacán','Q2605410'],[1500,'Tahirid Sultanate','Q2342941'],[1444,'Joseon','Q28179'],[-100,'Great Yuan','Q1179260'],[700,'Kingdom of Italy','Q854415'],[950,'Kingdom of Italy','Q838931'],[1900,'Kingdom of Italy','Q172579'],[1100,'Ly Dynasty','Q878309'],[1371,'Tran Dynasty','Q3111454'],[1401,'Ho Dynasty','Q1209047']];
 for(const [year,name,qid]of cases){const f=at(year).features.find(f=>f.properties.NAME===name);assert.ok(f,`${year}: ${name} exists`);assert.equal(f.properties.qid,qid,`${year}: ${name}`);}
 const curated=read('public/data/curated-facts.json');assert.equal(curated.identities['Khmer Empire'],undefined,'period-specific identities must not override all years');
 assert.equal(at(-300).features.find(f=>f.properties.NAME==='Han').properties.qid,'Q1574130');
 const facts=read('public/data/polity-facts.json').entities;
 for(const rule of read('public/data/chronology-corrections.json').identityCorrections){if(!rule.qid.startsWith('Q'))continue;assert.ok(facts[rule.qid],rule.qid);assert.ok(!facts[rule.qid].fields.instanceOf?.some(r=>r.value==='Q4167410'),`${rule.name} cannot resolve to a disambiguation page`);}
 assert.equal(at(1200).features.find(f=>f.properties.NAME==='Khmer Empire').properties.qid,'Q201705');assert.equal(at(1500).features.find(f=>f.properties.NAME==='Khmer Empire').properties.qid,'Q4919413');
});

test('1918 and 1919 restore the missing Soviet Russian core without annexing existing neighboring owners',()=>{
 const name='Russian Socialist Federative Soviet Republic';
 const report=read('public/data/russian-civil-war-gap-review.json');
 assert.deepEqual(report.records.map(r=>r.year),[1918,1919]);
 for(const year of [1918,1919]){
  for(const city of [[37.62,55.75],[30.32,59.93],[32.05,54.78],[34.37,53.24],[36.19,51.73],[39.2,51.67],[39.9,59.22],[46.03,51.54]])assert.deepEqual(owners(year,city),[name],`${year}: ${city}`);
  for(const city of [[33.08,68.97],[40.54,64.54],[73.37,54.99],[39.7,47.2]])assert.deepEqual(owners(year,city),['Russian Republic'],`${year}: preserve existing non-Soviet footprint`);
  assert.deepEqual(owners(year,[23.76,61.5]),['Republic of Finland']);
  assert.deepEqual(owners(year,[30.52,50.45]),[year===1918?'German Empire':"Ukrainian People's Republic"]);
  const f=at(year).features.find(f=>f.properties.NAME===name);
  assert.equal(f.properties.qid,'Q2305208');assert.equal(f.properties.validFrom,year);assert.equal(f.properties.validTo,year);
  assert.match(f.properties.accuracy,/概化/);assert.ok(f.properties.sourceUrl.startsWith('https://wwws.loc.gov/'));
  assert.equal(report.records.find(r=>r.year===year).overlapWithExisting,0);
 }
 assert.notDeepEqual(at(1918).features.find(f=>f.properties.NAME===name).geometry,at(1919).features.find(f=>f.properties.NAME===name).geometry);
 for(const year of [1917,1920])assert.ok(!at(year).features.some(f=>f.properties.NAME===name),'patch never leaks into other years');
 const facts=read('public/data/polity-facts.json').entities.Q2305208;
 assert.ok(facts.fields.headOfGovernment.some(r=>r.value==='Q1394'&&r.from===1917&&r.to===1924));
 const flag=read('public/data/flags.json').entities.Q2305208.find(r=>r.from===1918&&r.to===1919);
 assert.match(flag.file,/1918–1925/);assert.ok(flag.periodNote&&flag.periodSource);
});

test('global audit covers all shards, all annual queries and exposes unresolved leads',()=>{
 const audit=read('public/data/chronology-audit.json'),index=read('public/data/temporal/index.json');
 assert.equal(audit.summary.shards,index.centuries.length);assert.equal(audit.summary.sourceRecords,index.counts.polityRecords);assert.equal(audit.summary.structuralErrors,0);
 assert.equal(audit.annualQueryCoverage.length,index.to-index.from);assert.equal(audit.annualQueryCoverage[0].year,index.from);assert.equal(audit.annualQueryCoverage.at(-1).year,index.to);
 assert.ok(audit.summary.reviewedCorrectionRules>=37);assert.ok(audit.metadataReviewQueue.length>0);for(const region of ['欧洲','亚洲','非洲','美洲','大洋洲'])assert.ok(audit.regions[region]>0);
});
