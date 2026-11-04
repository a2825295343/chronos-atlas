import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {regionsAtYear} from '../src/regions.mjs';
import {baseColor, colorDistance} from '../src/colors.mjs';
import {buildAtlasFrame} from '../src/atlas-render.mjs';
import {GeoJSONVT} from '@maplibre/geojson-vt';
import {classifyRings} from '@maplibre/maplibre-gl-style-spec';

const read = file => JSON.parse(readFileSync(new URL('../public/data/' + file, import.meta.url), 'utf8'));

test('Italian province geography and regional affiliation switch at the documented years', () => {
 const italian = {type:'FeatureCollection', features:read('historical-provinces.geojson').features.filter(f => f.properties.country === 'Italy')};
 const province = (year, name) => regionsAtYear(undefined, italian, undefined, year).features.filter(f => f.properties.native === name);
 assert.equal(province(1963, 'Campobasso')[0].properties.parentRegion, '阿布鲁齐和莫利塞');
 assert.equal(province(1964, 'Campobasso')[0].properties.parentRegion, '莫利塞');
 assert.equal(province(1964, "L'Aquila")[0].properties.label, '拉奎拉');
 assert.equal(province(1969, 'Isernia').length, 0);
 assert.equal(province(1970, 'Isernia').length, 1);
 assert.equal(province(1970, 'Campobasso').length, 1);
 assert.equal(province(1970, 'Isernia')[0].properties.sourceYear, 1971);
});

test('Portuguese archive additions attach to the active map identities and a single war record', () => {
 const facts = read('curated-facts.json');
 const frame = (century, year) => activePolities(read(`temporal/${century}.geojson`), year).features;
 const union = frame(16, 1600).find(f => f.properties.NAME === 'Iberian Union');
 assert.match(facts.polities[union.properties.qid].rulers.find(([a,b]) => a <= 1600 && b >= 1600)[2], /菲利佩二世/);
 const marriage = facts.relations.find(r => r.id === 'braganza-stuart-1662');
 for (const name of marriage.members) assert.ok(frame(16, 1670).some(f => f.properties.NAME === name));
 assert.deepEqual([marriage.from, marriage.to], [1662, 1685]);
 assert.equal(read('historical-population.json')['Kingdom of Portugal']['1864'].population, 4286995);
 const wars = read('conflicts.json').wars.filter(w => w.id === 'historic-portuguese-restoration');
 assert.equal(wars.length, 1);
 assert.ok(wars[0].participants[1].polityNames.includes('Kingdom of Spain'));
});

test('1903 land gaps are covered without replacing nearby known Himalayan territories', () => {
 const shard = read('temporal/19.geojson');
 for (const year of [1902, 1903, 1904, 1905]) {
  const frame = activePolities(shard, year).features;
  const owners = point => frame.filter(f => pointInGeometry(point, f.geometry)).map(f => f.properties.NAME);
  assert.deepEqual(owners([117.414,39.034]), ['Qing Dynasty']);
  assert.deepEqual(owners([79.276,34.261]), ['Western Himalayan Frontier Communities']);
  assert.deepEqual(owners([93.286,27.479]), ['Eastern Himalayan Frontier Communities']);
  assert.deepEqual(owners([89.64,27.47]), ['Kingdom of Bhutan']);
 }
});

test('the eight former provinces appear before their respective mergers and use reference outlines', () => {
 const provinces = {type:'FeatureCollection',features:read('historical-provinces.geojson').features.filter(f => f.properties.supplement === 'discontinued-chinese-provinces')};
 const labels = year => regionsAtYear(undefined, provinces, undefined, year).features.map(f => f.properties.label);
 assert.equal(labels(1951).length, 8);
 assert.deepEqual(labels(1952), ['绥远省','松江省','辽东省','辽西省','热河省','西康省']);
 assert.deepEqual(labels(1954), ['热河省','西康省']);
 assert.equal(labels(1955).length, 0);
 assert.ok(provinces.features.every(f => !f.properties.boundaryVisible));
});

test('the calibrated historical footprints replace seats and cut only overlapping reference areas', () => {
 const onlyChina = collection => ({...collection,features:collection.features.filter(f => f.properties.country === 'China')});
 const modern = onlyChina(read('provinces.geojson'));
 const historical = onlyChina(read('historical-provinces.geojson'));
 const at = year => regionsAtYear(modern,historical,undefined,year).features;
 const snapshots = year => at(year).filter(f => f.properties.supplement === 'chinese-province-snapshots');
 for (const [year,count] of [[1949,0],[1950,27],[1951,27],[1952,22],[1953,20],[1954,3],[1955,0]]) {
  assert.equal(snapshots(year).length,count);
 }
 const features = at(1951);
 const former = snapshots(1951);
 assert.ok(!features.some(f => f.properties.locatorOnly));
 assert.ok(former.every(f => ['Polygon','MultiPolygon'].includes(f.geometry.type) && f.properties.boundaryVisible));
 const checks = [
  ['察哈尔省',[113.30,40.08]], ['平原省',[115.48,35.24]],
  ['绥远省',[109.84,40.66]], ['松江省',[130.35,46.80]],
  ['辽东省',[124.39,40.13]], ['辽西省',[121.15,41.12]],
  ['热河省',[117.94,40.97]], ['西康省',[101.96,30.05]],
 ];
 for (const [label,point] of checks) {
  const hits = features.filter(f => pointInGeometry(point,f.geometry));
  assert.deepEqual(hits.map(f => f.properties.label),[label]);
 }
 assert.ok(!features.some(f => f.properties.id === 'CHN-1813'));
 const shandong = features.filter(f => pointInGeometry([117.0,36.65],f.geometry));
 assert.deepEqual(shandong.map(f=>f.properties.label),['山东省']);
 assert.ok(shandong.every(f=>f.properties.sourceYear===1950));
});

test('early PRC snapshots separate the four Sichuan administrations and municipal enclaves', () => {
 const china=collection=>({...collection,features:collection.features.filter(f=>f.properties.country==='China')});
 const modern=china(read('provinces.geojson')),historical=china(read('historical-provinces.geojson'));
 const frames=new Map();
 const at=(year,point)=>{
  if(!frames.has(year))frames.set(year,regionsAtYear(modern,historical,undefined,year).features);
  return frames.get(year).filter(f=>pointInGeometry(point,f.geometry)).map(f=>f.properties.label);
 };
 for(const [point,name] of [
  [[102.71,25.05],'云南省'],[[104.06,30.67],'川西行署区'],[[106.11,30.80],'川北行署区'],
  [[105.44,28.88],'川南行署区'],[[108.39,30.81],'川东行署区'],[[106.55,29.56],'重庆市'],
  [[116.40,39.91],'北京市'],[[117.20,39.13],'天津市'],[[121.47,31.23],'上海市'],
  [[119.02,33.60],'苏北行署区'],[[120.62,31.30],'苏南行署区'],
 ])assert.deepEqual(at(1951,point),[name]);
 assert.deepEqual(at(1952,[104.06,30.67]),['四川省']);
 assert.deepEqual(at(1953,[120.62,31.30]),['江苏省']);
 assert.deepEqual(at(1954,[106.55,29.56]),['四川省']);
 assert.deepEqual(at(1980,[106.55,29.56]),['四川省']);
 assert.ok(!at(1926,[121.47,31.23]).includes('上海市'));
 const labels=year=>regionsAtYear(modern,historical,undefined,year).features.filter(f=>f.properties.locatorOnly).map(f=>f.properties.label);
 assert.ok(labels(1926).includes('上海县'));
 assert.ok(labels(1927).includes('上海特别市'));
});

test('Tianjin concession tiles have explicit priority across zoom levels', () => {
 const world = activePolities(read('temporal/19.geojson'),1903);
 const names = ['Qing Dynasty','Empire of Japan','French Indochina','Russian Empire'];
 const {atlas} = buildAtlasFrame({...world,features:world.features.filter(f => names.includes(f.properties.NAME))});
 const tiles = new GeoJSONVT(atlas.fills,{maxZoom:14,extent:8192,tolerance:.002*16,buffer:128*16});
 for (const [name,[lon,lat]] of [[names[1],[117.502,38.900]],[names[2],[117.235,39.417]],[names[3],[117.555,39.417]]]) {
  for (const zoom of [3,4,5,6,7,8,10,12,14]) {
   const n = 2**zoom,x = (lon+180)/360*n,y = (1-Math.log(Math.tan(Math.PI/4+lat*Math.PI/360))/Math.PI)/2*n;
   const tx = Math.floor(x),ty = Math.floor(y),local = [(x-tx)*8192,(y-ty)*8192];
   const hit = tiles.getTile(zoom,tx,ty).features.filter(f => classifyRings(f.geometry.map(r => r.map(([x,y]) => ({x,y}))),500)
    .some(p => pointInGeometry(local,{type:'Polygon',coordinates:p.map(r => r.map(({x,y}) => [x,y]))})))
    .sort((a,b) => b.tags.fillOrder-a.tags.fillOrder)[0];
   assert.equal(hit?.tags.NAME,name,`${zoom}: ${name}`);
   assert.equal(hit.tags.fillOrder,1);
  }
 }
});

test('late Qing and Republic-era source divisions are selectable without projecting modern Manchuria', () => {
 const china=collection=>({...collection,features:collection.features.filter(f=>f.properties.country==='China')});
 const modern=china(read('provinces.geojson')),historical=china(read('historical-provinces.geojson'));
 for(const [year,checks] of [
  [1911,[[[123.43,41.8],'奉天省'],[[123.95,47.34],'黑龙江省'],[[126.55,43.83],'吉林省'],[[104.06,30.67],'四川省'],[[116.08,43.94],'内蒙古诸盟']]],
  [1936,[[[104.06,30.67],'四川省'],[[111.67,40.82],'绥远省'],[[114.88,40.82],'察哈尔省']]],
  [1946,[[[104.06,30.67],'四川省'],[[111.67,40.82],'绥远省']]],
 ]){
  const features=regionsAtYear(modern,historical,undefined,year).features;
  for(const [point,label] of checks)assert.deepEqual(features.filter(f=>pointInGeometry(point,f.geometry)).map(f=>f.properties.label),[label]);
  const shanghai=features.find(f=>f.properties.label==='上海县');
  if(year===1911)assert.ok(shanghai?.properties.locatorOnly&&shanghai.geometry.type==='Point'&&shanghai.properties.sourceUrl);
  if(year===1936){
   assert.ok(features.some(f=>f.properties.label==='滨江省'&&f.properties.locatorOnly));
   assert.ok(!features.some(f=>['CHN-1813','CHN-1828','CHN-1839'].includes(f.properties.id)));
  }
 }
});

test('overlapping historical provinces share a single selectable footprint, with the snapshot taking priority', () => {
 const province = (id, west, east, dataKind) => ({
  type:'Feature',
  geometry:{type:'Polygon',coordinates:[[[west,0],[east,0],[east,2],[west,2],[west,0]]]},
  properties:{id,label:id,country:id,validFrom:1900,validTo:1910,dataKind},
 });
 const reference=province('reference',0,3,'historical-reconstruction');
 const snapshot=province('snapshot',2,4,'historical-snapshot');
 const {features}=regionsAtYear(undefined,{type:'FeatureCollection',features:[reference,snapshot]},undefined,1905);
 for(const [point,id] of [[[1,1],'reference'],[[2.5,1],'snapshot'],[[3.5,1],'snapshot']]){
  assert.deepEqual(features.filter(f=>pointInGeometry(point,f.geometry)).map(f=>f.properties.id),[id]);
 }
});

test('Li Zicheng keeps the same archive and war identity as his map name changes', () => {
 const shard = read('temporal/16.geojson');
 const ruler = year => activePolities(shard, year).features.find(f => f.properties.NAME === 'Li Zicheng').properties;
 assert.equal(ruler(1643).displayName, '李自成起义军');
 assert.equal(ruler(1644).displayName, '大顺');
 assert.equal(read('curated-facts.json').polities[ruler(1644).qid].rulers[0][2], '李自成');
});

test('Italian states of the unified lineage use a stable purple distinct from Spain and neighboring states', () => {
 const italy = baseColor('Italy');
 assert.equal(baseColor('Kingdom of Italy'), italy);
 assert.equal(baseColor('Italian Republic'), italy);
 for (const neighbor of ['Spain','France','Switzerland','Austria','Slovenia']) assert.ok(colorDistance(italy,baseColor(neighbor)) > 80, neighbor);
});
