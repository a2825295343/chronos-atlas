import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {scopedFacts,selectFlag} from '../src/archive-rules.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const facts=read('public/data/polity-facts.json').entities,flags=read('public/data/flags.json').entities;
const heads=(q,y)=>scopedFacts(facts[q],'ruler',y).rows;

test('modern identity corrections are year-scoped and identify the actual states',()=>{
 const rows=activePolities(read('public/data/temporal/20.geojson'),2024).features;
 for(const [name,qid]of [['Second Republic of Austria','Q40'],['Hungary','Q28'],['Denmark','Q35'],['Guinea','Q1006']]){
  const f=rows.find(f=>f.properties.NAME===name);assert.ok(f,name);assert.equal(f.properties.qid,qid);
 }
 const rules=read('public/data/modern-identity-corrections.json').identityCorrections;
 assert.ok(rules.every(r=>Number.isInteger(r.from)&&Number.isInteger(r.to)&&r.from<=r.to));
});

test('all existing modern state records have real flags and dated leadership in both review years',()=>{
 const report=read('public/data/modern-archive-audit.json');
 for(const year of report.years){
  const states=year.rows.filter(r=>r.category==='state');assert.equal(states.length,187);
  for(const r of states){
   const flag=selectFlag(flags[r.qid]||[],year.year).flag;
   assert.ok(flag?.path&&existsSync(new URL('../public'+flag.path,import.meta.url)),r.name+' flag');
   const active=heads(r.qid,year.year);assert.ok(active.length,r.name+' dated head');
   assert.equal(new Set(active.map(r=>r.value)).size,active.length,r.name+' duplicate person');
   assert.ok(scopedFacts(facts[r.qid],'headOfGovernment',year.year).rows.length,r.name+' government head');
  }
  assert.equal(year.summary.territoryFlags,5);assert.equal(year.summary.territoryHeadStates,5);
 }
});

test('named modern flags and leaders do not use other historical entities',()=>{
 for(const [q,file]of [['Q40','Flag of Austria.svg'],['Q28','Flag of Hungary.svg'],['Q35','Flag of Denmark.svg'],['Q1006','Flag of Guinea.svg']])assert.equal(selectFlag(flags[q],2024).flag.file,file);
 assert.deepEqual(heads('Q40',2024).map(r=>r.value),['Q78869']);
 assert.deepEqual(heads('Q35',2023).map(r=>r.value),['Q102139']);
 assert.deepEqual(new Set(heads('Q35',2024).map(r=>r.value)),new Set(['Q102139','Q1004037']));
 assert.deepEqual(heads('Q35',2026).map(r=>r.value),['Q1004037']);
 assert.ok(heads('Q28',2024).some(r=>r.value==='Q21995345'));assert.ok(heads('Q28',2024).some(r=>r.value==='Q465476'));
 assert.equal(heads('Q39',2024)[0].kind,'collective');assert.equal(heads('Q822',2024)[0].kind,'vacancy');
 assert.ok(heads('Q822',2026).some(r=>r.value==='Q29033962'));
 assert.deepEqual(heads('Q1007',2024).map(r=>r.value),['Q16855164']);
});

test('leadership supplements respect the role, evidence date and review boundary',()=>{
 const gov=(q,y)=>scopedFacts(facts[q],'headOfGovernment',y).rows.map(r=>r.value);
 assert.ok(!gov('Q757',2024).includes('Q28319076'),'an opposition term is not a PM term');
 assert.ok(gov('Q757',2026).includes('Q28319076'));
 assert.ok(!gov('Q686',2024).includes('Q16190741'));assert.ok(!gov('Q851',2026).includes('Q367825'));
 assert.ok(heads('Q1007',2026).some(r=>r.at===2026));assert.ok(!heads('Q1007',2024).some(r=>r.at===2026));
 const e={fields:{ruler:[{value:'a',from:2020,to:null,verifiedThrough:2026},{value:'a',at:2026,derived:true,verifiedThrough:2026}]}};
 assert.equal(scopedFacts(e,'ruler',2026).rows.length,1);assert.equal(scopedFacts(e,'ruler',2027).rows.length,0);
});
