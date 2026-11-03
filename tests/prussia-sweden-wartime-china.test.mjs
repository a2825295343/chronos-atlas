import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {mapName} from '../src/map-names.mjs';
import {leadershipFor} from '../src/archive-rules.mjs';

const read = name => JSON.parse(readFileSync(new URL('../public/data/'+name, import.meta.url),'utf8'));
const {entities}=read('polity-facts.json');
const shards=new Map();
function frame(year) {
 const century=Math.floor(year/100);
 if(!shards.has(century))shards.set(century,read('temporal/'+century+'.geojson'));
 return activePolities(shards.get(century),year).features;
}

test('royal Prussia supersedes the composite Brandenburg-Prussia label from 1701',()=>{
 assert.ok(frame(1700).some(f=>f.properties.NAME==='Brandenburg-Prussia'));
 for(let year=1701;year<=1721;year++){
  const prussia=frame(year).filter(f=>['Kingdom of Prussia','Brandenburg-Prussia'].includes(f.properties.NAME));
  assert.deepEqual(prussia.map(f=>f.properties.NAME),['Kingdom of Prussia']);
  assert.equal(prussia[0].properties.qid,'Q27306');
 }
});

test('wartime CCP record selects Yan’an and leaves Xinjiang with its historical administrations',()=>{
 for(let year=1938;year<=1945;year++){
  const world=frame(year);
  const owners=point=>world.filter(f=>!f.properties.controlArea&&pointInGeometry(point,f.geometry)).map(f=>f.properties.NAME);
  assert.deepEqual(owners([109.49,36.59]),['Communist Party of China'],String(year));
  assert.deepEqual(owners([87.62,43.82]),['Republic of China'],String(year));
  const base=world.find(f=>f.properties.NAME==='Communist Party of China');
  assert.equal(mapName(base.properties),'中共抗日根据地');
  assert.ok(leadershipFor(entities[base.properties.qid],undefined,year).rows.length);
 }
});

test('the Swedish Empire archive has a dated monarch throughout the imperial era',()=>{
 for(let year=1611;year<=1721;year++)assert.ok(leadershipFor(entities.Q215443,undefined,year).rows.length,String(year));
 assert.ok(leadershipFor(entities.Q215443,undefined,1709).rows.some(r=>r.label==='卡尔十二世'));
});
