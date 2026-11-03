import fs from 'node:fs';
import {VectorTile} from '@mapbox/vector-tile';
import {PbfReader} from 'pbf';
const folder=new URL('../.local/japan-kuni/',import.meta.url),features=[];
for(const name of fs.readdirSync(folder).filter(n=>/^5-\d+-\d+\.pbf$/.test(n))){
 const [z,x,y]=name.slice(0,-4).split('-').map(Number),tile=new VectorTile(new PbfReader(fs.readFileSync(new URL(name,folder)))),layer=tile.layers.kuni;
 if(layer)for(let i=0;i<layer.length;i++)features.push(layer.feature(i).toGeoJSON(x,y,z));
}
if(new Set(features.map(f=>f.properties.id)).size!==85)throw Error('Expected all 85 source provinces; do not publish an incomplete download.');
fs.writeFileSync(new URL('decoded.geojson',folder),JSON.stringify({type:'FeatureCollection',features}));
console.log('Decoded old-kuni tile pieces:',features.length);
