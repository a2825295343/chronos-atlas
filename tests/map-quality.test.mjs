import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync,statSync} from 'node:fs';
import {politicalBorders} from '../src/cartography.ts';
const read=name=>JSON.parse(readFileSync(new URL(name,import.meta.url),'utf8'));
test('every bundled historical polity and cultural label has a Chinese translation',()=>{
 const labels=read('../src/localization/names.zh.json'),sources=read('../src/localization/provenance.json');
 const all=new Set();
 for(const entry of read('../public/data/manifest.json'))for(const f of read('../public/data/'+entry.filename).features)for(const key of ['NAME','SUBJECTO']){
  const name=(f.properties[key]||'').trim().replace(/\s+/g,' ');if(!name)continue;all.add(name);assert.match(labels[name]||'',/[\u3400-\u9fff]/u);assert.ok(sources[name]);
 }
 assert.ok(all.size>=3000);assert.equal(labels['Pomeranian culture'],'波美拉尼亚文化');assert.equal(labels['Han'],'汉朝');
});
test('high-resolution global elevation pyramid and detailed geography are complete',()=>{
 for(let z=0;z<=5;z++)for(let x=0;x<2**z;x++)for(let y=0;y<2**z;y++){
  const bytes=readFileSync(new URL(`../public/data/dem/${z}/${x}/${y}.png`,import.meta.url));assert.equal(bytes.subarray(1,4).toString(),'PNG');
 }
 for(const name of ['land','ocean','lakes','rivers_lake_centerlines'])assert.equal(read(`../public/data/ne_10m_${name}.geojson`).type,'FeatureCollection');
 assert.ok(read('../public/data/ocean-mask-hd.geojson').features.length>=60);
 assert.ok(statSync(new URL('../public/data/atlas-cjk.ttf',import.meta.url)).size>1e7);
});
test('neighboring subregions draw one national border and hide same-owner subdivisions',()=>{
 const feature=(name,owner,x)=>({type:'Feature',properties:{NAME:name,SUBJECTO:owner},geometry:{type:'Polygon',coordinates:[[[x,0],[x+1,0],[x+1,1],[x,1],[x,0]]]}});
 const countShared=collection=>collection.features.flatMap(f=>f.geometry.coordinates).reduce((sum,line)=>sum+line.slice(1).filter((p,i)=>p[0]===1&&line[i][0]===1).length,0);
 assert.equal(countShared(politicalBorders({type:'FeatureCollection',features:[feature('a','one',0),feature('b','one',1)]})),0);
 assert.equal(countShared(politicalBorders({type:'FeatureCollection',features:[feature('a','one',0),feature('b','two',1)]})),1);
});
