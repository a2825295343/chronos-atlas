import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {activePolities} from '../src/temporal.mjs';
import {countryGlyphs} from '../src/atlas-render.mjs';
import {politicalBorders} from '../src/cartography.mjs';
import {pointInGeometry} from '../src/history.mjs';

const read = name => JSON.parse(readFileSync(new URL('../public/data/'+name, import.meta.url),'utf8'));
const shards = new Map();
function world(year) {
 const c=Math.floor(year/100);
 if(!shards.has(c))shards.set(c,read('temporal/'+c+'.geojson'));
 return activePolities(shards.get(c),year);
}
function at(year,point) {
 return world(year).features.filter(f=>pointInGeometry(point,f.geometry)).map(f=>f.properties.NAME);
}

test('1386 unified Golden Horde and 1919–1925 territorial repairs are present',()=>{
 assert.ok(!world(1386).features.some(f=>f.properties.NAME==='Blue Horde'));
 assert.deepEqual(at(1919,[25.28,54.68]),['Second Polish Republic']);
 for(let year=1919;year<=1923;year++)assert.ok(at(year,[28.976,41.012]).length,String(year));
 for(let year=1913;year<=1919;year++)assert.ok(at(year,[-99.13,19.43]).includes('Mexico'),String(year));
 for(let year=1924;year<=1925;year++)
  for(const p of [[118.8,32],[117.2,31.8]])assert.ok(at(year,p).includes('Republic of China'),String(year));
});

test('the date line has no political border and both halves of Wrangel Island have an owner',()=>{
 const world1950=world(1950);
 const soviet=world1950.features.find(f=>f.properties.NAME==='Union of Soviet Socialist Republics');
 const lines=politicalBorders({features:[soviet]}).features[0].geometry.coordinates;
 assert.ok(!lines.some(line=>line.some((p,i)=>i>0&&Math.abs(p[0])===180&&Math.abs(line[i-1][0])===180)));
 for(const p of [[179.5,71.2],[-179.5,71.2]])assert.ok(pointInGeometry(p,soviet.geometry));
});

test('historical Aral water and modern exposed lakebed have separate geometry',()=>{
 const lake=read('aral-historical-water.geojson').features[0];
 assert.ok(pointInGeometry([60.5,44.5],lake.geometry));
 assert.ok(at(2024,[60.5,44.5]).includes('Republic of Uzbekistan'));
 assert.ok(at(2024,[61,45.5]).includes('Kazakhstan'));
});


test('modern Azerbaijan renders one polity and one label, retaining Nakhchivan',()=>{
 for(let year=1992;year<=2024;year++){
  const rows=world(year).features.filter(f=>['Azerbaijan','Republic of Azerbaijan'].includes(f.properties.NAME));
  assert.deepEqual(rows.map(f=>f.properties.NAME),['Republic of Azerbaijan'],String(year));
  assert.equal(new Set(countryGlyphs(rows).features.map(f=>f.properties.part)).size,1);
  for(const point of [[49.867,40.409],[45.412,39.209]])assert.ok(pointInGeometry(point,rows[0].geometry));
 }
 assert.ok(world(1919).features.some(f=>f.properties.NAME==='Azerbaijan Democratic Republic'));
});


test('shared modern reference restores Adriatic islands and Pearl River estuary coverage',()=>{
 for(const [point,owner] of [
  [[16.17,43.04],'Republic of Croatia'],
  [[16.65,43.15],'Republic of Croatia'],
  [[17.15,42.95],'Republic of Croatia'],
  [[114.17,22.3],"People's Republic of China"],
  [[113.55,22.19],"People's Republic of China"],
 ]) assert.deepEqual(at(2024,point),[owner]);
});

test('dated coastal repairs restore islands without using modern sovereign identities',()=>{
 for(const [year,owner,point] of [
  [100,'Roman Empire',[4.25664752,39.82981422]],
  [1444,'Kingdom of England',[-1.10352053,50.7027245]],
  [1600,'Tokugawa Government',[129.19366599,34.12953091]],
 ]){
  assert.deepEqual(at(year,point),[owner]);
  const f=world(year).features.find(f=>f.properties.NAME===owner);
  assert.equal(f.properties.historicalIslandGeometry,'historical-island-coast-alignment');
 }
});

test('the Second Athenian League has its alliance name and historical coastal coverage',()=>{
 const league=world(-366).features.find(f=>f.properties.NAME==='Second Athenian League');
 assert.equal(league.properties.displayName,'第二次雅典同盟');
 assert.equal(league.properties.mapLabel,'第二次雅典同盟');
 assert.deepEqual(at(-366,[27.25628257,40.78257223]),['Second Athenian League']);
 assert.deepEqual(at(100,[27.79147702,37.100002]),['Roman Empire']);
});

test('1130 Aegean island cores and modern Nauru are visible in the dated atlas',()=>{
 for(const point of [[25.47,37.09],[25.14,37.08],[24.43,37.43],[26.85,37.73]])
  assert.deepEqual(at(1130,point),['Byzantine Empire']);
 for(const year of [1968,1999,2000,2024]){
  const nauru=world(year).features.find(f=>f.properties.NAME==='Nauru');
  assert.equal(nauru?.properties.displayName,'瑙鲁');
  assert.equal(nauru?.properties.qid,'Q697');
  assert.deepEqual(at(year,[166.93,-.52]),['Nauru']);
 }
 assert.ok(!world(1967).features.some(f=>f.properties.NAME==='Nauru'));
});

test('worldwide historical coastline repairs cover distant shores with their dated owners',()=>{
 for(const [year,owner,point] of [
  [100,'Han Dynasty',[121.575008876,31.6413325]],
  [100,'Roman Empire',[-7.276943943,37.209194]],
  [500,'Gupta Empire',[84.224642726,18.549811]],
  [500,'Eastern Roman Empire',[27.743588192,31.133003559]],
 ]){
  const polity=world(year).features.find(f=>f.properties.NAME===owner);
  assert.equal(polity?.properties.worldCoastalGeometry,'world-historical-coast');
  assert.deepEqual(at(year,point),[owner]);
 }
});
