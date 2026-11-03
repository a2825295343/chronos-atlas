import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {activePolities} from '../src/temporal.mjs';
import {mapName} from '../src/map-names.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {capitalsAtYear} from '../src/capitals.mjs';
import {leadershipFor} from '../src/archive-rules.mjs';

const read = name => JSON.parse(readFileSync(new URL('../public/data/'+name, import.meta.url),'utf8'));
const {entities} = read('polity-facts.json');
const shards = new Map();
function world(year) {
 const century = Math.floor(year/100);
 if (!shards.has(century)) shards.set(century, read('temporal/'+century+'.geojson'));
 return activePolities(shards.get(century), year);
}
function polity(year, name) {
 return world(year).features.find(f => f.properties.NAME === name);
}
function names(qid, year) {
 return leadershipFor(entities[qid], undefined, year).rows.map(row=>row.label);
}

test('named map records resolve to their dated historical polities and archives', () => {
 for (const [year, name, label, ruler] of [
  [652,'Frankish Burgundy','法兰克勃艮第王国','克洛维二世'],
  [1073,'Norman England','诺曼英格兰王国','威廉一世'],
  [1859,'Principality of Serbia','塞尔维亚公国','米洛什·奥布雷诺维奇一世'],
  [1900,'Kingdom of Serbia','塞尔维亚王国','亚历山大一世'],
 ]) {
  const {properties:p} = polity(year,name);
  assert.equal(mapName(p),label);
  assert.ok(names(p.qid,year).includes(ruler));
 }
});

test('Norwegian mainland has one map owner in the union and after it', () => {
 const nidaros=[10.395,63.43];
 for (const [year,owner] of [[1027,'Kingdom of Norway'],[1030,'North Sea Empire'],[1036,'Kingdom of Norway']]) {
  const land = world(year).features.filter(f => ['Kingdom of Norway','North Sea Empire'].includes(f.properties.NAME));
  assert.deepEqual(land.filter(f => pointInGeometry(nidaros,f.geometry)).map(f=>f.properties.NAME),[owner]);
 }
 assert.equal(mapName(polity(1030,'Kingdom of Norway').properties),'');
});

test('France has a dated governing body throughout the revolution and the papal capital is located', () => {
 for (let year=1792;year<=1799;year++) {
  const polityName=year<=1795?'French First Republic':'French Directory';
  assert.ok(names(polity(year,polityName).properties.qid,year).includes(year<1795?'国民公会':'五人督政府'));
 }
 assert.ok(names('Q219817',1799).includes('拿破仑·波拿巴'));
 const index=read('map-capitals.json');
 const identities=read('curated-facts.json').identities;
 const rome=capitalsAtYear(world(1859),1859,index,identities).features.find(f=>f.properties.owner==='Papal States');
 assert.equal(rome?.properties.label,'罗马');
 assert.ok(pointInGeometry(rome.geometry.coordinates,polity(1859,'Papal States').geometry));
});
