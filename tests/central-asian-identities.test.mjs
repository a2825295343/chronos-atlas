import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {baseColor,colorDistance} from '../src/colors.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../public/data/'+n,import.meta.url),'utf8'));
const cache=new Map();
const frame=y=>{const c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`temporal/${c}.geojson`));return activePolities(cache.get(c),y).features;};

test('divided Qarakhanid branches retain separate names, archive identities and stable colors',()=>{
 for(const year of [1046,1056,1060,1070,1084]){
  const e=frame(year).find(f=>f.properties.NAME==='Eastern Kara-Khanids');
  const w=frame(year).find(f=>f.properties.NAME==='Western Karakhanid Khanate');
  assert.ok(e&&w);assert.equal(e.properties.displayName,'东喀喇汗国');assert.equal(w.properties.displayName,'西喀喇汗国');
  assert.notEqual(e.properties.qid,w.properties.qid);
  assert.ok(colorDistance(e.properties.thematicColor,w.properties.thematicColor)>90);
 }
});

test('1566 Tarim, Turpan and Tian Shan labels distinguish successor polities and local communities',()=>{
 const fs=frame(1566),y=fs.find(f=>f.properties.NAME==='Eastern Moghulistan'),t=fs.find(f=>f.properties.NAME==='Turpan Khanate'),k=fs.find(f=>f.properties.NAME==='Kyrgyz Tian Shan Communities');
 assert.ok(y&&t&&k);assert.equal(y.properties.displayName,'叶尔羌汗国');assert.equal(t.properties.displayName,'吐鲁番汗国');
 assert.equal(k.properties.displayName,'天山吉尔吉斯诸部');assert.equal(k.properties.regionalCollection,true);
 assert.equal(new Set([y,t,k].map(f=>f.properties.qid)).size,3);
 assert.ok(pointInGeometry([77.27,38.42],y.geometry));assert.ok(pointInGeometry([89.2,42.9],t.geometry));
 assert.ok(!pointInGeometry([89.2,42.9],y.geometry));
 assert.ok(!fs.some(f=>f.properties.displayName==='蒙兀儿斯坦'));
 assert.ok(!frame(1570).some(f=>f.properties.NAME==='Turpan Khanate'));
 assert.equal(frame(1565).find(f=>f.properties.NAME==='Eastern Moghulistan').properties.thematicColor,baseColor('Eastern Moghulistan'));
 for(const year of [1519,1530,1566,1570,1600,1630,1680]){
  const city=frame(year).filter(f=>pointInGeometry([89.2,42.9],f.geometry));
  assert.equal(city.length,1,`${year} Turpan has overlapping territorial owners`);
 }
});

test('dynastic origin is documented without manufacturing an alliance or a common sovereign',()=>{
 const cur=read('curated-facts.json');
 for(const pair of [['Eastern Kara-Khanids','Western Karakhanid Khanate'],['Eastern Moghulistan','Turpan Khanate']]){
  assert.notEqual(cur.identities[pair[0]],cur.identities[pair[1]]);
  const relation=cur.relations.find(r=>r.kind==='historicalDivision'&&pair.every(n=>r.members.includes(n)));
  assert.ok(relation);assert.match(relation.detail,/不等于|不据此/);
 }
});
