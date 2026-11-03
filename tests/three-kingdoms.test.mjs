import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {scopedFacts} from '../src/archive-rules.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../public/data/'+p,import.meta.url),'utf8'));
const shard=read('temporal/2.geojson'),facts=read('polity-facts.json').entities;
const world=y=>activePolities(shard,y).features;
const heads=(q,y)=>scopedFacts(facts[q],'ruler',y).rows;

test('Shu Han exists from 221, including Chengdu and Hanzhong in each missing year',()=>{
 assert.ok(!world(220).some(f=>f.properties.NAME==='Shu Han'));
 for(let y=221;y<=262;y++){
  const f=world(y).find(f=>f.properties.NAME==='Shu Han');assert.ok(f,`${y} Shu`);assert.equal(f.properties.qid,'Q320925');
  for(const p of [[104.07,30.67],[107,33.07]])assert.ok(pointInGeometry(p,f.geometry),`${y}: ${p}`);
 }
 for(const y of [221,222,223]){
  const shu=world(y).find(f=>f.properties.NAME==='Shu Han');assert.match(shu.properties.accuracy,/224年/);
  assert.equal(world(y).filter(f=>pointInGeometry([104.07,30.67],f.geometry)).length,1);
 }
});

test('Cao Cao becomes Cao Wei in 220, while Wei and Wu do not outlive their reviewed annual phases',()=>{
 for(let y=220;y<=265;y++){
  const f=world(y).find(f=>f.properties.NAME==='Cao Wei');assert.ok(f,`${y} Wei`);assert.ok(heads(f.properties.qid,y).length);
  assert.ok(pointInGeometry([112.45,34.62],f.geometry),`${y} Luoyang`);
  assert.ok(!world(y).some(f=>f.properties.NAME==='Cao Cao'));
 }
 assert.ok(!world(265).some(f=>f.properties.NAME==='Western Jin'));
 assert.ok(world(266).some(f=>f.properties.NAME==='Western Jin'));
 for(const y of [281,282]){
  assert.ok(!world(y).some(f=>f.properties.NAME==='Eastern Wu'));
  assert.ok(world(y).some(f=>f.properties.NAME==='Western Jin'&&pointInGeometry([118.8,32.06],f.geometry)));
 }
});

test('all three kingdoms have named monarchs, correctly bounded successions and dated sources',()=>{
 for(const[q,lo,hi]of [['Q320925',221,263],['Q320930',220,266],['Q274488',207,280]])for(let y=lo;y<=hi;y++)assert.ok(heads(q,y).length,`${q} ${y}`);
 assert.deepEqual(heads('Q320925',222).map(r=>r.label),['刘备']);
 assert.deepEqual(heads('Q320925',223).map(r=>r.label),['刘备','刘禅']);
 assert.deepEqual(heads('Q320925',224).map(r=>r.label),['刘禅']);
 assert.deepEqual(heads('Q320930',221).map(r=>r.label),['曹丕']);
 for(const [y,cn]of [[230,'曹叡'],[250,'曹芳'],[255,'曹髦'],[263,'曹奂']])assert.ok(heads('Q320930',y).some(r=>r.label===cn));
 for(const [y,cn]of [[221,'孙权'],[253,'孙亮'],[260,'孙休'],[275,'孙皓']])assert.ok(heads('Q274488',y).some(r=>r.label===cn));
 assert.match(heads('Q274488',221)[0].roleLabel,/吴王/);assert.match(heads('Q274488',230)[0].roleLabel,/吴大帝/);
 for(const r of read('three-kingdoms-review.json').rulers){assert.match(r.value,/^Q\d+$/);assert.ok(r.citation.length>=2);assert.ok(r.roleLabel);}
});
