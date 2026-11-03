import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {baseColor,colorDistance} from '../src/colors.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../public/data/'+p,import.meta.url),'utf8'));
const cache=new Map(),frame=y=>{const c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`temporal/${c}.geojson`));return activePolities(cache.get(c),y).features;};
const owners=(y,p)=>frame(y).filter(f=>pointInGeometry(p,f.geometry));

test('Qing interior omissions are filled annually without erasing named Hui military cores or Xinjiang phases',()=>{
 for(let y=1864;y<=1876;y++)for(const p of [[103.83,36.06],[94.66,40.14],[101.78,36.62]])assert.ok(owners(y,p).length,`${y} ${p}`);
 assert.deepEqual(owners(1870,[106.1,37.9]).map(f=>f.properties.NAME),['Jinjipu Hui Forces']);
 assert.deepEqual(owners(1870,[98.49,39.74]).map(f=>f.properties.NAME),['Suzhou Hui Forces']);
 for(const p of [[106.1,37.9],[98.49,39.74]])assert.deepEqual(owners(1876,p).map(f=>f.properties.NAME),['Qing Dynasty']);
 assert.ok(frame(1870).some(f=>f.properties.NAME==='Yettishar'));assert.ok(frame(1872).some(f=>f.properties.NAME==='Control area - russian-ili'));
});

test('1917–1927 provincial omissions have dated local administrations and preserve other territorial owners',()=>{
 for(let y=1917;y<=1927;y++)for(const p of [[102.71,25.04],[110.29,25.27],[116.4,39.9],[108.94,34.34],[117,36.65]])assert.ok(owners(y,p).length,`${y} ${p}`);
 assert.ok(owners(1917,[102.71,25.04]).some(f=>f.properties.NAME==='Yunnan Military Authorities'));
 const beijing=owners(1927,[116.4,39.9]);assert.ok(beijing.some(f=>f.properties.NAME==='Beijing Tianjin Military Authorities'));
 assert.ok(beijing.every(f=>f.properties.sovereignName==='Republic of China'));
 assert.ok(!owners(1927,[91.13,29.65]).some(f=>f.properties.NAME.includes('Military Authorities')));
});

test('1930 coalition is a military coalition, not the war entity, and dissolves into later administrations in 1931',()=>{
 const f=frame(1930).find(f=>f.properties.NAME==='Anti-Kuomintang Coalition');assert.ok(f);assert.equal(f.properties.displayName,'反蒋联军');assert.notEqual(f.properties.qid,'Q717809');assert.equal(f.properties.validTo,1930);
 for(const p of [[112.55,37.87],[108.94,34.34],[110.29,25.27]])assert.equal(owners(1930,p).length,1,`${p} overlapping central and coalition owners`);
 assert.ok(!frame(1931).some(f=>f.properties.NAME==='Anti-Kuomintang Coalition'));
 for(const p of [[112.55,37.87],[108.94,34.34],[110.29,25.27]]){const fs=owners(1931,p);assert.equal(fs.length,1);assert.ok(fs[0].properties.regionalCollection);assert.equal(fs[0].properties.sovereignName,'Republic of China');}
});

test('1946 former Mengjiang omissions have regional successors without expanding the Mongolian state',()=>{
 for(const p of [[109.84,40.66],[111.98,43.65],[114.97,44.02],[116.07,43.93]]){
  const fs=owners(1946,p);assert.ok(fs.length);assert.ok(!fs.some(f=>f.properties.NAME==="Mongolian People's Republic"));
 }
 const group=frame(1946).find(f=>f.properties.NAME==='Suiyuan Chahar Local Authorities');assert.ok(group);assert.equal(group.properties.sovereignName,'Republic of China');assert.match(group.properties.representationNote,/全年控制线/);
 for(const name of ['Suiyuan Chahar Local Authorities','Inner Mongolian Autonomy Movement Areas'])for(const neighbor of ["Mongolian People's Republic",'Union of Soviet Socialist Republics','Republic of China'])assert.ok(colorDistance(baseColor(name),baseColor(neighbor))>=85,`${name} contrasts with ${neighbor}`);
});

test('Norse is a geographic community grouping rather than a language or unified Norway',()=>{
 for(const y of [200,300,400,499]){
  const f=frame(y).find(f=>f.properties.NAME==='Norse');assert.ok(f);assert.equal(f.properties.displayName,'北欧诸部');assert.equal(f.properties.qid,'local:norse-communities');assert.equal(f.properties.regionalCollection,true);
 }
 const facts=read('polity-facts.json').entities['local:norse-communities'];assert.ok(facts.fields.ruler.every(r=>r.kind==='collective'));assert.match(facts.description,/不是挪威语/);
});
