import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {regionsAtYear} from '../src/regions.mjs';
import {baseColor, colorDistance} from '../src/colors.mjs';

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
