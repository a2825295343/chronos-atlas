import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {baseColor,colorPolities,colorDistance} from '../src/colors.mjs';
import {activePolities} from '../src/temporal.mjs';
import {buildAtlasFrame} from '../src/atlas-render.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../'+name,import.meta.url),'utf8'));
const box=(name,x=0,size=1)=>({type:'Feature',properties:{NAME:name},geometry:{type:'Polygon',coordinates:[[[x,0],[x+size,0],[x+size,size],[x,size],[x,0]]]}});
const paint=features=>new Map(colorPolities({type:'FeatureCollection',features}).features.map(f=>[f.properties.NAME,f.properties.thematicColor]));
test('colors do not depend on geometry size, feature order, or neighbors appearing and disappearing',()=>{
 const before=paint([box('France'),box('Germany',1),box('A new neighboring power',2)]);
 const after=paint([box('A new neighboring power',0,40),box('Germany',-2,6),box('France',4,.1),box('Another power',5)]);
 for(const name of before.keys()){assert.equal(before.get(name),after.get(name));assert.equal(before.get(name),paint([box(name)]).get(name));}
 assert.equal(baseColor('Uncatalogued new polity'),paint([box('Uncatalogued new polity')]).get('Uncatalogued new polity'));
});
test('country aliases and overseas occupation stripes share the same fixed identity color',()=>{
 for(const aliases of [['France','Kingdom of France','French Third Republic','French Fifth Republic'],['Germany','German Empire','Weimar Republic','Nazi Germany'],['United Kingdom','Kingdom of Great Britain','United Kingdom of Great Britain and Ireland'],['Portugal','Estado Novo'],['Spain','Francoist Spain']])assert.equal(new Set(aliases.map(baseColor)).size,1,aliases.join(', '));
 const raw=read('public/data/temporal/19.geojson'),frame=buildAtlasFrame(activePolities(raw,1941));
 const germany=frame.features.find(f=>f.properties.NAME==='Nazi Germany');
 assert.equal(germany.properties.color,baseColor('Germany'));
 for(const f of frame.features.filter(f=>f.properties.controlArea&&f.properties.controller==='Nazi Germany')){
  assert.equal(f.properties.thematicColor,germany.properties.color);
  assert.equal(f.properties.color,baseColor(f.properties.sovereignName));
 }
});
test('every recurring polity keeps its color while querying historical years in both directions',()=>{
 const seen=new Map();
 for(const century of [14,19,20]){
  const raw=read(`public/data/temporal/${century}.geojson`),years=[0,1,20,39,40,41,42,44,45,46,47,48,49,50,60,61,62,70,80,90,99].map(y=>century*100+y).filter(y=>y<=2024);
  for(const year of [...years,...years.toReversed()])for(const f of activePolities(raw,year).features){
   const p=f.properties,name=p.NAME,key=p.controlArea?p.controller:name;
   if(seen.has(name))assert.equal(p.thematicColor,seen.get(name),`${name} changed in ${year}`);
   seen.set(name,p.thematicColor);assert.equal(p.thematicColor,baseColor(key));
  }
 }
 assert.ok(seen.size>300);
});
test('fixed colors retain key neighbor contrasts and remain distinct from unmapped land',()=>{
 for(const [a,b] of [['France','Germany'],['France','United Kingdom'],['Spain','Portugal']])assert.ok(colorDistance(baseColor(a),baseColor(b))>=85,`${a}/${b}`);
 for(const name of ['France','Germany','United Kingdom','Spain','Portugal','Ming Dynasty','Roman Empire','Unknown polity'])assert.ok(colorDistance(baseColor(name),'#5b665f')>65,name);
});
