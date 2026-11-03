import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {scopedFacts} from '../src/archive-rules.mjs';
import {dependenciesAt} from '../src/relationships.mjs';
import {warsAtYear} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../public/data/'+n,import.meta.url),'utf8'));
const facts=read('polity-facts.json').entities,cur=read('curated-facts.json'),cache=new Map();
const world=y=>{const c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`temporal/${c}.geojson`));return activePolities(cache.get(c),y);};
const entity=(name,y)=>{const p=world(y).features.find(f=>f.properties.NAME===name)?.properties;assert.ok(p,`${y} ${name} absent`);return facts[cur.identities[name]||p.qid];};

test('pre-Yuan Chinese states and dynasties have named reigns in their own dated archives',()=>{
 for(const [year,name]of [[-462,'Jin'],[-462,'Qin'],[-462,'Chu'],[-462,'Qi'],[-462,'Lu'],[-462,'Song'],[-462,'Zheng'],[-462,'Cai'],[-462,'Eastern Zhou'],[-250,'Han'],[-250,'Wei'],[-250,'Zhao'],[100,'Han Dynasty'],[400,'Eastern Jin'],[400,'Northern Wei'],[450,'Liu Song Dynasty'],[490,'Southern Qi'],[530,'Liang Dynasty'],[560,'Northern Qi'],[600,'Sui Dynasty'],[750,'Tang Dynasty'],[950,'Later Han'],[1060,'Northern Song'],[1060,'Liao Dynasty'],[1060,'Western Xia'],[1200,'Great Jin']]){
  const e=entity(name,year),rows=scopedFacts(e,'ruler',year).rows;
  assert.ok(rows.length,`${year} ${name} lacks a named ruler`);
  assert.ok(rows.every(r=>r.kind==='person'||String(r.value).startsWith('Q')),`${name} office substituted for person`);
  for(const key of ['government','religion'])assert.ok(scopedFacts(e,key,year).rows.length,`${year} ${name} ${key}`);
 }
 assert.notEqual(cur.identities['Liang Dynasty'],cur.identities['Southern Liang']);
 assert.notEqual(cur.identities['Eastern Zhou'],cur.identities['Later Zhou']);
 const yue=world(-462).features.find(f=>f.properties.NAME==='Yue');assert.equal(yue.properties.displayName,'越国');assert.notEqual(yue.properties.qid,'Q1936158');
 assert.ok(scopedFacts(entity('Jin',-462),'capital',-462).rows.some(r=>r.label.includes('新田')));
 assert.ok(scopedFacts(entity('Qin',-462),'capital',-462).rows.some(r=>r.label==='雍'));
 assert.ok(scopedFacts(entity('Wei',-250),'capital',-250).rows.some(r=>r.label==='大梁'));
});

test('period catalogues never become diplomatic superiors; explicit Zhou nominal allegiance remains distinct',()=>{
 const w=world(-462);const rel=dependenciesAt(w,[], -462,cur.relations);
 assert.ok(!rel.some(r=>/Spring and Autumn|Warring States/.test(r.parent)));
 assert.ok(rel.some(r=>r.child==='Jin'&&r.parent==='Eastern Zhou'&&r.kind==='allegiance'));
 assert.ok(!rel.some(r=>r.child==='Jin'&&r.kind==='colony'));
 const meeting=cur.relations.find(r=>r.id==='chinese-wars-2026-11-01:kuiqiu');assert.ok(!meeting.members.includes('Jin'));
});

test('Chinese campaigns are matched to contemporary map names and their actual years',()=>{
 const db=read('conflicts.json'),details=read('war-details.json');
 for(const [year,name,fragment]of [[-632,'Jin','城濮'],[-260,'Zhao','长平'],[-154,'Han Dynasty','七国'],[383,'Eastern Jin','淝水'],[612,'Sui Dynasty','高句丽'],[621,'Tang Dynasty','虎牢'],[1126,'Northern Song','靖康'],[1126,'Great Jin','靖康']]){
  assert.ok(warsAtYear(db,details,year).some(w=>w.name.includes(fragment)&&warInvolvesPolity(w,name,year)),`${year} ${name} ${fragment}`);
 }
 assert.ok(!warsAtYear(db,details,627).some(w=>w.id==='historic-cn-tang-east-turks'));
});

test('imported records retain Chinese person labels, dated reigns and citations',()=>{
 const review=read('chinese-archives-review.json');assert.ok(review.summary.reignRecords>=600);assert.ok(review.summary.polities>=70);
 for(const r of review.records){assert.ok(r.from<=r.to);assert.ok(r.citation.length);assert.match(r.label,/[\u3400-\u9fff]/);assert.doesNotMatch(r.label,/[A-Za-z]/);}
 assert.ok(review.sources.some(s=>s.includes('moe.edu.tw')));
});
