import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {referenceSitesAtYear} from '../src/reference-sites.mjs';
import {scopedFacts,leadershipFor} from '../src/archive-rules.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../public/data/'+n,import.meta.url),'utf8'));
const shard=read('temporal/18.geojson');
const frame=y=>activePolities(shard,y).features;
const owners=(y,p)=>frame(y).filter(f=>pointInGeometry(p,f.geometry)).map(f=>f.properties.NAME);

test('1856 northern Qing omission is restored while existing Taiping territory remains intact',()=>{
 for(const point of [[116.99,36.67],[116.4,39.9],[113.63,34.75],[114.48,38.03]]){
  for(const year of [1855,1856,1857])assert.ok(owners(year,point).includes('Qing Dynasty'),`${year} ${point}`);
 }
 assert.deepEqual(owners(1856,[118.79,32.06]),['Taiping Heavenly Kingdom']);
 assert.deepEqual(owners(1856,[116.99,36.67]),['Qing Dynasty']);
});

test('1823 source symbols become dated point references rather than angular territorial enclaves',()=>{
 const sites=referenceSitesAtYear(read('colonial-reference-sites.geojson'),1823);
 assert.ok(sites.features.length>=25);
 const west=sites.features.filter(f=>f.geometry.coordinates[0]<-105&&f.geometry.coordinates[1]>45);
 assert.ok(west.length>=8);
 for(const f of west){
  assert.equal(f.geometry.type,'Point');assert.equal(f.properties.inferred,true);
  assert.match(f.properties.accuracy,/具体站名/);
  assert.ok(!owners(1823,f.geometry.coordinates).some(n=>n.startsWith('United Kingdom Colony')||n==='British Colonial Empire'));
 }
 assert.equal(referenceSitesAtYear(read('colonial-reference-sites.geojson'),2024).features.length,0);
});

test('actual islands and territorial regions survive fragment cleanup',()=>{
 for(const [point,name] of [[[ -77.25,18.1],'United Kingdom Colony - Jamaica'],[[-79.5,22.1],'Spain Colony - Cuba'],[[-51.7,64.2],'Greenland'],[[-73.5,45.5],'United Kingdom Colony - Canada'],[[-99.13,19.43],'First Mexican Empire']]){
  assert.ok(owners(1823,point).includes(name),`${name} ${point}`);
 }
 const report=read('qing-american-fragments-review.json');
 assert.ok(report.partitionResidualsReattached>0);
 assert.ok(report.records.every(r=>r.unexplainedAreaChange<1e-6));
});

test('reference sites filter dates inclusively and deduplicate operator-position pairs',()=>{
 const f={type:'Feature',geometry:{type:'Point',coordinates:[-110,55]},properties:{validFrom:1800,validTo:1823,operator:'British Colonial Empire',ownerName:'United Kingdom Colony - Canada'}};
 const c={type:'FeatureCollection',features:[f,structuredClone(f)]};
 for(const y of [1800,1823])assert.equal(referenceSitesAtYear(c,y).features.length,1);
 for(const y of [1799,1824])assert.equal(referenceSitesAtYear(c,y).features.length,0);
});

test('British colonial leadership uses the contemporary sovereign archive rather than modern UK claims',()=>{
 const facts=read('polity-facts.json').entities;
 for(const [year,sovereign,person]of [[1750,'Q161885','Q131981'],[1823,'Q174193','Q130586'],[1925,'Q145','Q269412']]){
  const w=activePolities({type:'FeatureCollection',features:[{type:'Feature',properties:{NAME:'Example colony',validFrom:1600,validTo:2000,sovereignName:'United Kingdom',sovereignQid:'Q145'},geometry:{type:'Polygon',coordinates:[]}}]},year);
  const p=w.features[0].properties;assert.equal(p.sovereignQid,sovereign);
  assert.ok(leadershipFor(undefined,facts[p.sovereignQid],year).rows.some(r=>r.value===person),`${year} wrong monarch`);
 }
 assert.ok(leadershipFor(undefined,facts.Q174193,1823).governmentRows.some(r=>r.value==='Q312569'));
});

test('a leadership claim with only an end date cannot apply to every earlier century',()=>{
 const e={fields:{ruler:[{value:'later-king',from:null,to:1936,at:null}]}};
 assert.equal(scopedFacts(e,'ruler',1823).rows.length,0);
 assert.ok(scopedFacts(read('polity-facts.json').entities.Q145,'ruler',1915).rows.some(r=>r.value==='Q269412'));
});
