import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {activePolities,perspectiveForZoom} from '../src/temporal.mjs';
import {scopedFacts,applies,selectFlag} from '../src/archive-rules.mjs';
import {pointInGeometry,territoryBounds} from '../src/history.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
test('camera bounds fit all pieces of a polity and cross the dateline by the short arc',()=>{
 const polygon=(west,south,east,north)=>({type:'Polygon',coordinates:[[[west,south],[east,south],[east,north],[west,north],[west,south]]]});
 assert.deepEqual(territoryBounds([polygon(-6,42,8,52),polygon(10,40,12,44)]),[[-6,40],[12,52]]);
 const islands={type:'MultiPolygon',coordinates:[polygon(177,51,179,54).coordinates,polygon(-179,52,-176,55).coordinates]};
 assert.deepEqual(territoryBounds([islands]),[[177,51],[184,55]]);
 assert.equal(territoryBounds([]),undefined);
});
test('1444 Beijing is Ming territory, with Oirat and Golden Horde independent',()=>{
 const data=activePolities(read('public/data/temporal/14.geojson'),1444),byName=new Map(data.features.map(f=>[f.properties.NAME,f]));
 assert.ok(pointInGeometry([116.4,39.9],byName.get('Ming Dynasty').geometry));
 assert.ok(!byName.has('Mongol Empire'));
 for(const name of ['Four Oirats','Golden Horde','Chagatai Khanate']){assert.ok(byName.has(name));assert.ok(!pointInGeometry([116.4,39.9],byName.get(name).geometry));}
 assert.ok(data.features.every(f=>f.properties.SUBJECTO===f.properties.NAME&&!f.properties.NAME.startsWith('(')));
});
test('every temporal shard has valid dates, labels, and polity-only records',()=>{
 const index=read('public/data/temporal/index.json'),labels={...read('src/localization/temporal.zh.json'),...read('src/localization/display-names.zh.json')};let records=new Set();
 for(const century of index.centuries)for(const f of read(`public/data/temporal/${century}.geojson`).features){const p=f.properties;assert.ok(p.validFrom<=p.validTo);assert.ok(p.validFrom<=century*100+99&&p.validTo>=century*100);assert.ok(/[\u3400-\u9fff]/.test(labels[p.NAME]),p.NAME);records.add(p.sourceRecord);}
 assert.equal(records.size,index.counts.polityRecords);assert.ok(index.counts.relationRecordsExcludedFromTerritory>300);
});
test('temporal querying resolves overlapping source periods without duplicating a polity',()=>{const f=(a,b,id)=>({type:'Feature',id,properties:{NAME:'A',validFrom:a,validTo:b},geometry:{type:'Point',coordinates:[0,0]}});const source={type:'FeatureCollection',features:[f(1400,1449,1),f(1440,1459,2),f(1450,1460,3)]};assert.deepEqual(activePolities(source,1444).features.map(f=>f.id),[2]);assert.equal(activePolities(source,1399).features.length,0);assert.equal(activePolities(source,1450).features[0].id,3);});
test('camera pitch and true elevation exaggeration rise smoothly with zoom',()=>{let p=0,h=1;for(let z=0;z<=11;z+=.01){const v=perspectiveForZoom(z);assert.ok(v.pitch>=p&&v.pitch<=72);assert.ok(v.exaggeration>=h&&v.exaggeration<=4.4);assert.ok(v.pitch-p<.3);p=v.pitch;h=v.exaggeration;}assert.equal(perspectiveForZoom(1).pitch,0);assert.ok(perspectiveForZoom(8).pitch>=65);assert.ok(perspectiveForZoom(8).exaggeration>=3.5);});
test('yearly leaders and flags never fall back to future dated or undated officeholders',()=>{
 const entity={fields:{ruler:[{label:'Current',from:2020,to:null},{label:'Unknown reign',from:null,to:null}],government:[{label:'Republic',from:1900,to:1950}]}};
 assert.equal(scopedFacts(entity,'ruler',1444).rows.length,0);assert.equal(scopedFacts(entity,'government',1444).rows.length,0);assert.equal(scopedFacts(entity,'ruler',2024).rows[0].label,'Current');
 assert.equal(selectFlag([{from:1844,to:1922}],1444).flag,undefined);
 const manual=read('public/data/curated-facts.json');assert.ok(manual.polities.Q9903.rulers.filter(r=>r[0]<=1444&&r[1]>=1444).some(r=>r[2].includes('朱祁镇')));assert.equal(manual.polities.Q12560.rulers.filter(r=>r[0]<=1444&&r[1]>=1444).length,2);
});
test('flag assets have individual sources and reconstructions disclose their evidence',()=>{const db=read('public/data/flags.json');assert.ok(db.count>600);for(const rows of Object.values(db.entities))for(const r of rows){assert.ok(existsSync(new URL('../public'+r.path,import.meta.url)),r.path);if(r.reconstructed){assert.ok(r.periodNote&&r.periodSource&&r.license);assert.ok(r.periodSource.startsWith('https://fiav.org/'));assert.ok(r.path.endsWith('ottoman-early-naval-reconstruction.svg'));}else assert.ok(r.commons.startsWith('https://commons.wikimedia.org/'));assert.ok(!/fictit|fiction|imaginary|fantasy/i.test(r.file));}assert.equal(db.entities.Q9903,undefined);});
test('COW wartime opponents are on different sides and restricted to their actual entry year',()=>{const db=read('public/data/diplomacy.json');const worldWar=db.wars.filter(r=>/World War I$|World War 1$/i.test(r.name));assert.ok(db.alliances.length>5000);assert.ok(worldWar.length>0);assert.ok(!worldWar.some(r=>r.code==='2'&&applies(r,1914)));assert.ok(worldWar.some(r=>r.code==='2'&&applies(r,1917)));assert.ok(db.alliances.every(r=>r.from<=r.to&&r.from>=1816&&r.to<=2012));});
import {updateTerrainScale} from '../src/terrain.mjs';
test('terrain animation reuses GPU mesh and synchronizes CPU samples and depth cache',()=>{let cleared=0,dirty=0,render=0;const mesh={};const map={terrain:{mesh,exaggeration:1,options:{exaggeration:1},coverage:{exaggeration:1,reset:()=>cleared++}},painter:{markTerrainDepthDirty:()=>dirty++},triggerRepaint:()=>render++};assert.equal(updateTerrainScale(map,3),true);assert.equal(map.terrain.mesh,mesh);assert.equal(map.terrain.exaggeration,3);assert.equal(map.terrain.coverage.exaggeration,3);assert.deepEqual([cleared,dirty,render],[1,1,1]);assert.equal(updateTerrainScale({},4),false);});
import {cowPolityName} from '../src/archive-rules.mjs';
test('continuous COW state codes use contemporary names instead of anachronistic labels',()=>{assert.equal(cowPolityName('345','Yugoslavia',1914),'塞尔维亚王国');assert.equal(cowPolityName('365','Russia',1941),'苏联');assert.equal(cowPolityName('640','Turkey',1914),'奥斯曼帝国');assert.equal(cowPolityName('710','China',1900),'清朝');});
