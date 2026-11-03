import test from'node:test';
import assert from'node:assert/strict';
import{readFileSync}from'node:fs';
import{activePolities}from'../src/temporal.mjs';
import{pointInGeometry}from'../src/history.mjs';
import{scopedFacts,leadershipFor}from'../src/archive-rules.mjs';
import{dependenciesAt}from'../src/relationships.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const atlas=read('public/data/temporal/19.geojson'),facts=read('public/data/polity-facts.json').entities,curated=read('public/data/curated-facts.json');
const at=y=>activePolities(atlas,y),owners=(y,p)=>at(y).features.filter(f=>pointInGeometry(p,f.geometry)).map(f=>f.properties.NAME);
const heads=(q,y)=>scopedFacts(facts[q],'ruler',y).rows;

test('Libya changes from separate postwar administrations to independence in 1951',()=>{
 for(const y of [1945,1948,1949,1950]){
  assert.deepEqual(owners(y,[13.19,32.89]),['British Tripolitania']);
  assert.deepEqual(owners(y,[14.43,27.04]),['French Fezzan']);
  assert.deepEqual(owners(y,[20.07,32.12]),[y<1949?'British Cyrenaica':'Emirate of Cyrenaica']);
 }
 for(const y of [1951,1952,1953,1955])for(const p of [[13.19,32.89],[14.43,27.04],[20.07,32.12]])assert.deepEqual(owners(y,p),['Kingdom of Libya'],`${y}: ${p}`);
 assert.ok(heads('Q31454',1951).some(r=>r.value==='Q116430'));
});

test('Eritrea, Somaliland, Timor, disputed islands and Chukotka no longer form unowned holes',()=>{
 for(let y=1945;y<=1955;y++){
  assert.deepEqual(owners(y,[44.06,9.56]),['British Somaliland Protectorate']);
  assert.deepEqual(owners(y,[-58.44,-51.82]),['Falkland Islands Dependency']);
  assert.deepEqual(owners(y,[-173.2,66.3]),['Union of Soviet Socialist Republics']);
  if(y>=1946)assert.deepEqual(owners(y,[125.58,-8.56]),['Portuguese Timor']);
  const eritrea=owners(y,[38.93,15.33]);
  assert.ok(eritrea.includes(y<1952?'British Administration of Eritrea':'Ethiopia'),`${y}: ${eritrea}`);
 }
 const report=read('public/data/postwar-territory-review.json');
 assert.ok(report.records.length>=77);
 for(const r of report.records){assert.ok(r.year>=1945&&r.year<=1955);assert.ok(r.overlapWithExisting<1e-7,'existing owners are protected');assert.ok(r.source.startsWith('https://'));}
});

test('1949 armistice-era Gaza is Egyptian administration, while Israeli coastal cities remain Israel',()=>{
 for(const y of [1949,1950,1952,1955]){
  assert.deepEqual(owners(y,[34.45,31.5]),['Gaza Strip under Egyptian Administration']);
  for(const p of [[34.78,32.08],[34.99,32.8]])assert.deepEqual(owners(y,p),['State of Israel']);
  assert.deepEqual(owners(y,[35.1,31.53]),['Kingdom of Jordan'],'existing West Bank control is not annexed by gap filling');
 }
});

test('postwar monarchs, republican heads and collective government retain the right roles and years',()=>{
 assert.ok(heads('Q713750',1950).some(r=>r.value==='Q2594'),'Heuss, not a former German regime');
 assert.ok(heads('Q69829',1950).some(r=>r.value==='Q158772'),'Auriol in 1950');
 assert.ok(!heads('Q142',1945).some(r=>r.value==='Q158772'),'Auriol must not replace the provisional government in 1945');
 assert.ok(heads('Q142',1945).some(r=>r.value==='Q2042'));
 assert.ok(heads('Q837',1950).some(r=>r.value==='Q381928'));
 assert.ok(heads('Q837',1950).some(r=>r.value==='Q201327'),'the short first Gyanendra reign, not his later reign');
 assert.ok(heads('Q77',1955).some(r=>r.kind==='collective'),'Uruguay has a collegial executive');
 assert.ok(!heads('Q804',1955).some(r=>r.value==='Q16625294'),'a disambiguation page cannot be a Panamanian president');
 assert.ok(heads('Q804',1955).some(r=>r.value==='Q176091'));
 assert.ok(heads('Q521263',1950).some(r=>r.value==='Q17293'&&r.roleLabel.includes('11月')));
 const turkeyGovernment=scopedFacts(facts.Q43,'headOfGovernment',1950).rows;
 assert.ok(turkeyGovernment.some(r=>r.value==='Q238745'));assert.ok(!turkeyGovernment.some(r=>['Q151735','Q183297'].includes(r.value)),'a parliamentary president is not the PM');
 const indonesiaGovernment=scopedFacts(facts.Q252,'headOfGovernment',1950).rows;
 assert.ok(indonesiaGovernment.some(r=>r.value==='Q2327343'));assert.ok(!indonesiaGovernment.some(r=>r.value==='Q76127'),'Natsir and Hatta are not replaced by the later executive presidency');
});

test('colonial and occupation archives explicitly inherit central leadership without replacing local rulers',()=>{
 const uk=facts.Q145,territory={fields:{}};
 const lead=leadershipFor(territory,uk,1950);
 assert.equal(lead.fromSovereign,true);assert.ok(lead.rows.some(r=>r.value==='Q280856'));assert.ok(!lead.rows.some(r=>r.value==='Q9682'));
 assert.ok(lead.governmentRows.some(r=>r.label.includes('艾德礼')||r.label.includes('艾德里')));
 const qatar=leadershipFor(facts['local:qatar-protectorate'],uk,1950);assert.equal(qatar.fromSovereign,false);assert.ok(qatar.rows.some(r=>r.value==='Q2470332'));
 assert.deepEqual(heads('Q944391',1950),[],'a history-topic article is not a state archive');
 assert.deepEqual(leadershipFor(territory,{fields:{ruler:[{value:'future',from:2000,to:2020}]}},1950).rows,[]);
 const world=at(1950),relation=dependenciesAt(world,[],1950,curated.relations).find(r=>r.child==='British Administration of Eritrea');
 assert.equal(relation.kind,'administration');assert.equal(relation.parent,'United Kingdom');
});

test('all 1945–1955 mapped records disclose a dated head, institution or explicitly inherited central head',()=>{
 const audit=read('public/data/postwar-archive-audit.json');assert.deepEqual(audit.years.map(r=>r.year),Array.from({length:11},(_,i)=>1945+i));
 for(const year of audit.years){assert.equal(year.rows.length,at(year.year).features.length);assert.equal(year.summary.headRecords,year.summary.records);assert.deepEqual(year.summary.missingHeads,[]);}
 const y=audit.years.find(r=>r.year===1950);assert.ok(y.summary.records>=160);assert.ok(y.summary.centralHeadRecords>50);
 const review=read('public/data/postwar-leadership-review.json');assert.ok(review.records.length>=500);
 for(const r of review.records){assert.ok(r.citation?.length);assert.ok(r.from<=1955&&r.to>=1945);assert.ok(r.from<=r.to);}
 assert.ok(at(1947).features.every(f=>f.properties.NAME!=='Kingdom of Bulgaria'));
 assert.ok(at(1948).features.every(f=>f.properties.qid!=='Q201190'),'a national/ethnic group is not a unified government');
 assert.ok(at(1950).features.every(f=>f.properties.NAME!=='Sultanate of Aceh'));
});
