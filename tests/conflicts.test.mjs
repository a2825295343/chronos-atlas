import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {warsAtYear,participantsAt,interpolateStrength} from '../src/conflicts.mjs';
import {activePolities} from '../src/temporal.mjs';
import {countryGlyphs,buildAtlasFrame} from '../src/atlas-render.mjs';
import {pointInGeometry} from '../src/history.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const database=read('public/data/conflicts.json'),details=read('public/data/war-details.json');
test('conflicts preserve annual activity gaps and never extend a closed dataset into 2026',()=>{
 const war=database.wars.find(w=>w.annual&&w.periods.length>1),year=war.periods[0][1]+1;
 assert.ok(!warsAtYear({wars:[war]},details,year).length);
 assert.ok(warsAtYear(database,details,2025).length>0);
 assert.equal(warsAtYear(database,details,2026).length,0);
 assert.ok(warsAtYear(database,details,1444).some(w=>w.id==='historic-varna'));
});
test('current participants respect actual entry dates and Korea merges matching dataset definitions',()=>{
 const ww=database.wars.find(w=>w.id==='cow-inter-139');
 assert.ok(!participantsAt(ww,1939).some(p=>p.name==='United States of America'));
 assert.ok(participantsAt(ww,1942).some(p=>p.name==='United States of America'));
 const detailed=warsAtYear(database,details,1941).find(w=>w.id==='cow-inter-139');
 assert.ok(participantsAt(detailed,1941).some(p=>p.name.includes('波兰流亡政府')));
 assert.ok(participantsAt(detailed,1941).some(p=>p.name.includes('自由法国')));
 const wars=warsAtYear(database,details,1952),korea=wars.find(w=>w.id==='ucdp-235');
 assert.ok(korea.also.some(w=>w.id==='cow-inter-151'));assert.ok(!wars.some(w=>w.id==='cow-inter-151'));
 assert.ok(participantsAt(korea,1952).some(p=>p.role==='直接军事介入'));
});
test('missing strength codes are not troops, and interpolation has strict temporal bounds',()=>{
 for(const w of database.wars)for(const p of w.participants)for(const key of ['peakTheaterForces','peakNationalForces','battleDeaths'])if(p[key]!=null)assert.ok(p[key]>=0,w.id);
 assert.deepEqual(interpolateStrength({2000:{military:10000},2004:{military:20000}},2002),{value:15000,estimated:true,years:[2000,2004]});
 assert.equal(interpolateStrength({2000:{military:10000},2009:{military:20000}},2002),null);
 assert.equal(interpolateStrength({2000:{military:10000}},2005),null);
 assert.equal(interpolateStrength({2000:{military:-9}},2000),null);
 const caucasus=database.wars.find(w=>w.id==='cow-intra-500');
 assert.equal(participantsAt(caucasus,1820).find(p=>p.side==='1').peakTheaterForces,70300);
 assert.equal(participantsAt(caucasus,1820).find(p=>p.side==='2').peakTheaterForces,46000);
});
test('Belgium control is filled, explicitly occupied, partitioned from other owners, and dated',()=>{
 for(const f of read('public/data/control-areas.geojson').features)assert.ok(['Polygon','MultiPolygon'].includes(f.geometry.type),f.properties.id);
 const raw=read('public/data/temporal/19.geojson'),world=activePolities(raw,1941),point=[4.35,50.85];
 const owners=world.features.filter(f=>pointInGeometry(point,f.geometry));
 assert.equal(owners.length,1);assert.equal(owners[0].properties.controller,'Nazi Germany');assert.equal(owners[0].properties.SUBJECTO,'Nazi Germany');
 assert.ok(!activePolities(raw,1938).features.some(f=>f.properties.controlArea&&f.properties.controller==='Nazi Germany'));
 assert.ok(!activePolities(raw,1949).features.some(f=>f.properties.NAME==='Control area - germany-soviet'));
 for(const [point,controller] of [[[21.01,52.23],'Nazi Germany'],[[118.79,32.06],'Empire of Japan']]){
  const records=world.features.filter(f=>pointInGeometry(point,f.geometry));
  assert.equal(records.length,1);assert.equal(records[0].properties.controller,controller);
 }
});
test('country glyphs follow a curved interior path and compact countries retain a complete label',()=>{
 const feature={type:'Feature',properties:{NAME:'Example',displayName:'大测试国'},geometry:{type:'Polygon',coordinates:[[[0,0],[20,0],[20,8],[0,8],[0,0]]]}};
 const labels=countryGlyphs([feature]);assert.equal(labels.features.map(f=>f.properties.name).join(''),'大测试国');
 assert.ok(new Set(labels.features.map(f=>f.geometry.coordinates[1])).size>1);
 for(const f of labels.features)assert.ok(pointInGeometry(f.geometry.coordinates,feature.geometry));
 const small={...feature,geometry:{type:'Polygon',coordinates:[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}};
 const compact=countryGlyphs([small]);assert.equal(compact.features[0].properties.name,'大测试国');assert.equal(compact.features[0].properties.compact,true);
 const frame=buildAtlasFrame({type:'FeatureCollection',features:[feature]});assert.ok(frame.atlas.borders);assert.ok(frame.features[0].properties.atlasArea>0);
});
test('extended reigns cover Tang, Song, Yuan and add only dated office-matched people',()=>{
 const facts=read('public/data/polity-facts.json'),curated=read('public/data/curated-facts.json');
 assert.ok(Object.values(curated.polities).some(p=>p.rulers?.some(r=>r[0]<=755&&755<=r[1]&&r[2].includes('李隆基'))));
 assert.ok(Object.values(facts.entities).flatMap(e=>[...(e.fields.ruler||[]),...(e.fields.headOfGovernment||[])]).filter(r=>r.dateSource?.startsWith('office-matched')&&r.from!=null).length>700);
});
test('NMC counts are converted from thousands to people and tied to their historical code',()=>{
 const nmc=read('public/data/national-strength.json');
 assert.equal(nmc.countries['255'].observations['1941'].military,7100000);
 assert.equal(nmc.countries['365'].observations['1941'].military,4207000);
 assert.equal(nmc.countries['2'].observations['1941'].population,133402000);
 assert.ok(!nmc.countries['255'].observations['2026']);
});
