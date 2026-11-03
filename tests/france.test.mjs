import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {GeoJSONVT} from '@maplibre/geojson-vt';
import {classifyRings} from '@maplibre/maplibre-gl-style-spec';
import {polygonRenderParts} from '../src/polygon-render.mjs';
import {activePolities} from '../src/temporal.mjs';
import {buildAtlasFrame} from '../src/atlas-render.mjs';
import {pointInGeometry,areaKm2} from '../src/history.mjs';
import {selectFlag} from '../src/archive-rules.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
function tileCovers(index,point,z){
 const n=2**z,x=(point[0]+180)/360*n,y=(1-Math.log(Math.tan(Math.PI/4+point[1]*Math.PI/360))/Math.PI)/2*n;
 const tx=Math.floor(x),ty=Math.floor(y),local=[(x-tx)*8192,(y-ty)*8192],tile=index.getTile(z,tx,ty);
 return (tile?.features||[]).some(f=>classifyRings(f.geometry.map(r=>r.map(([x,y])=>({x,y}))),500).some(p=>pointInGeometry(local,{type:'Polygon',coordinates:p.map(r=>r.map(p=>[p.x,p.y]))})));
}
test('French mainland remains a filled exterior through low-zoom tile quantization',()=>{
 for(const year of [1960,2000,2001,2024]){
  const raw=read(`public/data/temporal/${Math.floor(year/100)}.geojson`),world=activePolities(raw,year),france=world.features.find(f=>f.properties.NAME==='French Fifth Republic');
  const frame=buildAtlasFrame({type:'FeatureCollection',features:[france]});
  // Match MapLibre's pixel-to-tile conversion (8192 / 512 = 16), including
  // the wide default buffer which exposes the tiny sliver/winding regression.
  const tiles=new GeoJSONVT(frame.atlas.fills,{maxZoom:12,extent:8192,tolerance:.03*16,buffer:128*16});
  for(const zoom of [1,2,3,4,5])for(const point of [[2.35,48.86],[4.84,45.76],[-.58,44.84],[1.44,43.6]])assert.ok(tileCovers(tiles,point,zoom),`${year}, zoom ${zoom}, ${point}`);
 }
});
test('render splitting preserves original coordinates, real holes, polity properties and area',()=>{
 const f={type:'Feature',properties:{NAME:'Country',id:'source-id',color:'#65a6ce'},geometry:{type:'MultiPolygon',coordinates:[[[[0,0],[8,0],[8,8],[0,8],[0,0]],[[2,2],[2,4],[4,4],[4,2],[2,2]]],[[[10,0],[12,0],[12,2],[10,2],[10,0]]]]}};
 const before=JSON.stringify(f),result=polygonRenderParts({type:'FeatureCollection',features:[f]});
 assert.equal(result.features.length,2);assert.equal(JSON.stringify(f),before);
 assert.equal(result.features[0].properties.id,'source-id');
 assert.equal(result.features[0].geometry.coordinates,f.geometry.coordinates[0]);
 assert.ok(!pointInGeometry([3,3],result.features[0].geometry));
 assert.ok(Math.abs(result.features.reduce((n,f)=>n+areaKm2(f.geometry),0)-areaKm2(f.geometry))<1e-6);
 assert.equal(new Set(result.features.map(f=>f.id)).size,2);
});
test('1415 France uses its dated royal banner, never the restoration white flag',()=>{
 const flags=read('public/data/flags.json'),curated=read('public/data/curated-facts.json'),portraits=read('public/data/portraits.json');
 assert.equal(curated.identities['Kingdom of France'],'Q70972');
 const selected=selectFlag(flags.entities.Q70972,1415);
 assert.equal(selected.flag.file,'Royal flag of France.svg');assert.equal(selected.reference,false);
 assert.match(selected.flag.role,/王旗/);assert.equal(selectFlag(flags.entities.Q207162,1415).flag,undefined);
 assert.ok(selectFlag(flags.entities.Q207162,1820).flag);
 assert.ok(curated.polities.Q70972.rulers.some(([a,b,n])=>a<=1415&&1415<=b&&n==='查理六世'));
 for(const [key,qid] of Object.entries(portraits.manualRulers))if(key.startsWith('Q207162|')&&curated.polities.Q70972.rulers.some(r=>key==='Q207162|'+r[2]))assert.equal(portraits.manualRulers[key.replace('Q207162|','Q70972|')],qid);
 const france=activePolities(read('public/data/temporal/14.geojson'),1415).features.find(f=>f.properties.NAME==='Kingdom of France');assert.equal(france.properties.qid,'Q70972');
});
