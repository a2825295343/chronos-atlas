import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {dependenciesAt} from '../src/relationships.mjs';
import {baseColor,colorDistance} from '../src/colors.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const shards=new Map(),frames=new Map();
function at(y){
 if(!frames.has(y)){
  const c=Math.floor(y/100);
  if(!shards.has(c))shards.set(c,read(`public/data/temporal/${c}.geojson`));
  frames.set(y,activePolities(shards.get(c),y));
 }
 return frames.get(y);
}
const owners=(y,p)=>at(y).features.filter(f=>pointInGeometry(p,f.geometry));
const names=(y,p)=>owners(y,p).map(f=>f.properties.NAME);
const expect=(y,p,name)=>assert.deepEqual(names(y,p),[name],`${y}: ${p}`);

test('Scotland survives the Union of the Crowns and civil-war omissions, with dated Commonwealth and 1707 exceptions',()=>{
 for(const y of [1609,1639,1640,1641,1642,1648,1649,1650,1651,1660,1699,1700,1706]){
  for(const p of [[-3.19,55.95],[-4.22,57.48],[-2.1,57.15]])expect(y,p,'Kingdom of Scotland');
 }
 for(const y of [1652,1655,1659])expect(y,[-3.19,55.95],'Commonwealth of England');
 for(const y of [1707,1708]){
  expect(y,[-3.19,55.95],'Kingdom of Great Britain');
  assert.ok(at(y).features.every(f=>f.properties.NAME!=='Kingdom of Scotland'));
 }
 expect(1641,[-1.61,54.97],'Kingdom of England');
 const cur=read('public/data/curated-facts.json');
 assert.ok(dependenciesAt(at(1641),[],1641,cur.relations).some(r=>r.kind==='union'&&[r.child,r.parent].includes('Kingdom of Scotland')));
});

test('Irish omissions are local polities, not an anachronistic united crown or a modern partition',()=>{
 for(const y of [-500,-1,1,400])for(const p of [[-8,53],[-8.5,52],[-7.4,54.7]])expect(y,p,'Irish Iron Age Polities');
 for(const y of [500,800,1000,1100,1168])expect(y,[-8,53],'Gaelic Irish Kingdoms');
 for(const y of [1400,1444,1500,1540])expect(y,[-7.32,55],'Gaelic Irish Lordships');
 expect(1540,[-6.26,53.35],'Lordship of Ireland');
 for(const y of [1541,1599,1600,1603,1609,1610,1641])expect(y,[-6.26,53.35],'Kingdom of Ireland');
 for(const y of [1603,1609,1610])expect(y,[-8.47,51.9],'Kingdom of Ireland');
 assert.ok(names(1000,[-6.26,53.35]).includes('Viking settlements'),'recorded Norse towns remain separate');
 assert.ok(names(1444,[-7.72,52.69]).includes('Earldom of Desmond'),'a separately recorded lordship is not swallowed by the regional aggregate');
 const regional=at(1444).features.find(f=>f.properties.NAME==='Gaelic Irish Lordships');
 assert.equal(regional.properties.regionalCollection,true);
 assert.match(regional.properties.accuracy,/不是统一国家/);
});

test('southern Yemen restores the mainland beside Socotra, separates Aden and protectorates, and respects independence',()=>{
 for(const y of [1948,1950,1953,1955,1959,1960,1961,1962]){
  expect(y,[45.03,12.8],'Colony of Aden');
  for(const p of [[49.13,14.54],[48.79,15.94]])expect(y,p,'Eastern Aden Protectorate States');
  expect(y,[44.88,13.06],'Western Aden Protectorate States');
  expect(y,[44.21,15.35],'North Yemen');
 }
 for(const y of [1963,1966]){
  expect(y,[45.03,12.8],'Western South Arabian States');
  expect(y,[49.13,14.54],'Eastern South Arabian Protectorate');
 }
 for(const y of [1967,1968,1969])for(const p of [[45.03,12.8],[49.13,14.54],[48.79,15.94]])expect(y,p,"People's Republic of Southern Yemen");
 const cur=read('public/data/curated-facts.json');
 assert.ok(dependenciesAt(at(1960),[],1960,cur.relations).some(r=>r.child==='Eastern Aden Protectorate States'&&r.parent==='United Kingdom'&&r.kind==='protectorate'));
});

test('1944 Italy has the southern kingdom, liberated cities, and explicit German military control in the north',()=>{
 for(const p of [[12.5,41.9],[14.27,40.85],[11.25,43.77],[12.2,44.42],[11.88,44.285],[13.36,38.12],[9.12,39.22]])expect(1944,p,'Kingdom of Italy');
 for(const p of [[9.19,45.46],[11.34,44.49]]){
  const rows=owners(1944,p);assert.equal(rows.length,1);assert.equal(rows[0].properties.NAME,'Italian Social Republic');
  assert.equal(rows[0].properties.controlArea,true);assert.equal(rows[0].properties.controller,'Nazi Germany');
 }
 expect(1944,[11.35,46.5],'Control area - de-italy-operations-1944');
 expect(1944,[13.4,52.52],'Nazi Germany');
 expect(1944,[7.45,46.95],'Swiss Confederation');
 for(const p of [[8.78,41.94],[9.15,42.31]])expect(1944,p,'France');
 assert.ok(at(1945).features.every(f=>!['Italian Social Republic','Control area - de-italy-operations-1944'].includes(f.properties.NAME)));
});

test('regional repairs carry dated provenance and do not borrow a unified Irish ruler',()=>{
 const report=read('public/data/regional-gap-review.json');assert.ok(report.records.length>30);
 for(const row of report.records)assert.ok(row.from<=row.to);
 for(const y of [1444,1641,1944,1960])for(const f of at(y).features.filter(f=>f.properties.chronologyPatch===report.revision)){
  assert.ok(f.properties.validFrom<=y&&y<=f.properties.validTo);
  assert.ok(f.properties.geometryMethod&&f.properties.sourceRecord);
 }
 const facts=read('public/data/polity-facts.json').entities;
 assert.equal(facts['local:gaelic-irish-lordships'].fields.ruler[0].kind,'collective');
 assert.match(facts['local:gaelic-irish-lordships'].fields.ruler[0].label,/不适用单一/);
});

test('restored regions retain their fixed colors across name changes and have readable neighbors',()=>{
 for(const [a,b] of [['Gaelic Irish Kingdoms','Gaelic Irish Lordships'],['Lordship of Ireland','Kingdom of Ireland'],['Western Aden Protectorate States','Western South Arabian States'],['Eastern Aden Protectorate States','Eastern South Arabian Protectorate'],["People's Republic of Southern Yemen","People's Democratic Republic of Yemen"]])assert.equal(baseColor(a),baseColor(b));
 for(const [a,b] of [['Gaelic Irish Lordships','Earldom of Desmond'],['Gaelic Irish Lordships','Lordship of Ireland'],['Western Aden Protectorate States','Eastern Aden Protectorate States'],['North Yemen','Colony of Aden']])assert.ok(colorDistance(baseColor(a),baseColor(b))>85,`${a}/${b}`);
});
