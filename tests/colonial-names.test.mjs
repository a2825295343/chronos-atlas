import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {buildAtlasFrame} from '../src/atlas-render.mjs';
import {mapName} from '../src/map-names.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
test('Dutch Formosa is named geographically and is not the Republic of China or the Dutch central state',()=>{
 const atlas=read('public/data/temporal/16.geojson'),cur=read('public/data/curated-facts.json');
 for(const year of [1626,1630,1644,1655,1661]){
  const f=activePolities(atlas,year).features.find(f=>f.properties.NAME==='Netherlands Colony - Taiwan');
  assert.ok(f,year);assert.equal(f.properties.displayName,'荷属台湾');assert.equal(f.properties.qid,'local:dutch-formosa');
  assert.equal(f.properties.sovereignName,'Dutch Republic');assert.equal(f.properties.sovereignQid,'Q170072');
 }
 assert.equal(cur.identities['Netherlands Colony - Taiwan'],'local:dutch-formosa');
 for(const file of ['src/localization/display-names.zh.json','src/localization/temporal.zh.json'])assert.equal(read(file)['Netherlands Colony - Taiwan'],'荷属台湾');
});

test('occupation labels show the geographic country while details retain occupation information',()=>{
 const france=activePolities(read('public/data/temporal/19.geojson'),1943).features.find(f=>f.properties.NAME==='Control area - de-france-full');
 assert.ok(france?.properties.controlArea);const frame=buildAtlasFrame({type:'FeatureCollection',features:[france]});
 assert.equal(frame.features[0].properties.label,'法国');assert.ok(frame.atlas.labels.features.every(f=>f.properties.fullName==='法国'));
 assert.equal(frame.features[0].properties.displayName,'法国（德军占领区概览）');assert.ok(frame.features[0].properties.controller);
 assert.equal(mapName({NAME:'Control area - germany-soviet',displayName:'苏联占领区（德国）'}),'德国');
 assert.equal(mapName({NAME:'British Tripolitania',displayName:'的黎波里塔尼亚（英国管理）'}),'的黎波里塔尼亚');
});
test('European map headings omit article disambiguation dates and English glosses',()=>{
 const labels=read('src/localization/display-names.zh.json');assert.equal(labels['Kingdom of Naples (Napoleonic)'],'那不勒斯王国');assert.equal(labels['Principality of Hohenzollern-Sigmaringen'],'霍亨索伦-西格马林根亲王国');assert.equal(labels.Parma,'帕尔马');
 for(const f of read('public/data/temporal/18.geojson').features){const p=f.properties;if(p.NAME==='Kingdom of Naples (Napoleonic)'){assert.equal(p.displayName,'那不勒斯王国');if(p.validTo<1806)assert.equal(p.qid,'Q173065');}}
 const bad=Object.entries(labels).filter(([,label])=>/[（(][^）)]*[A-Za-z][^）)]*[）)]/.test(label));assert.deepEqual(bad,[]);
});
