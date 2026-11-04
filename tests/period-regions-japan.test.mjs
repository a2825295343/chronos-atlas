import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {regionsAtYear} from '../src/regions.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../public/data/'+p,import.meta.url),'utf8'));
const shards=new Map(),world=y=>{const c=Math.floor(y/100);if(!shards.has(c))shards.set(c,read(`temporal/${c}.geojson`));return activePolities(shards.get(c),y);};
const owners=(y,p)=>world(y).features.filter(f=>pointInGeometry(p,f.geometry));
const modern=read('provinces.geojson'),historical=read('historical-provinces.geojson');
const divisions=y=>regionsAtYear(modern,historical,world(y),y);
const labelsAt=(c,p)=>c.features.filter(f=>!f.properties.suppressLabel&&pointInGeometry(p,f.geometry)).map(f=>f.properties.label);

test('1645–1647 Kham omissions contain local tusi without annexing existing Tibet or Qing',()=>{
 for(const y of [1645,1646,1647]){assert.ok(owners(y,[101.96,30.05]).some(f=>f.properties.NAME==='Chakla Tusi'));assert.ok(owners(y,[97.18,31.14]).some(f=>f.properties.NAME==='Tibet'));}
 assert.ok(!world(1648).features.some(f=>f.properties.NAME==='Chakla Tusi'));
});

test('Ming-era Amur gaps contain named regional communities while Liaodong remains separately owned',()=>{
 for(const y of [1371,1400,1444,1500,1600])assert.ok(owners(y,[127.5,50.25]).length,`${y} Heihe`);
 const f=owners(1444,[127.5,50.25]).find(f=>f.properties.NAME==='Amur Local Communities');assert.ok(f);assert.equal(f.properties.regionalCollection,true);assert.match(f.properties.representationNote,/并非统一国家/);
 assert.ok(owners(1444,[123.17,41.27]).some(f=>f.properties.NAME==='Ming Dynasty'));
});

test('Japanese epoch labels become courts or independent named daimyo forces',()=>{
 for(const y of [650,750,900])for(const f of world(y).features.filter(f=>['Asuka Japan','Nara Japan','Heian Japan'].includes(f.properties.NAME))){assert.ok(!f.properties.displayName.includes('时代'));assert.equal(f.properties.qid,'local:japanese-imperial-court');}
 assert.ok(!world(1570).features.some(f=>f.properties.NAME==='Warring States Japan'));
 for(const [p,key]of [[[136.9066,35.1815],'Oda'],[[138.568,35.6639],'Takeda'],[[137.17,34.96],'Tokugawa'],[[138.24,37.15],'Uesugi'],[[132.46,34.4],'Mori'],[[130.56,31.6],'Shimazu']])assert.ok(owners(1570,p).some(f=>f.properties.NAME==='Japanese clan - '+key),key);
 assert.ok(world(1601).features.some(f=>f.properties.NAME==='Tokugawa Government'));assert.ok(!world(1601).features.some(f=>f.properties.NAME==='Tokugawa Shogunate'));
 assert.ok(!world(1868).features.some(f=>f.properties.NAME==='Tokugawa Shogunate'));
});

test('China changes divisions across Han, Tang, Song, Yuan, Ming and Qing instead of repeating modern provinces',()=>{
 for(const [y,p,expected]of [[200,[113.26,23.13],'交趾刺史部'],[750,[113.26,23.13],'岭南道'],[1100,[120.15,30.27],'两浙路'],[1330,[120.15,30.27],'江浙行省'],[1444,[120.15,30.27],'浙江布政使司'],[1700,[120.15,30.27],'浙江省']])assert.ok(labelsAt(divisions(y),p).includes(expected),`${y} ${expected}`);
 assert.ok(labelsAt(divisions(1200),[120.15,30.27]).includes('两浙西路'));
});

test('Japan old kuni and Korean do replace the later prefecture and north-south divisions',()=>{
 const jp=divisions(1570);assert.ok(labelsAt(jp,[138.568,35.6639]).includes('甲斐国'));assert.ok(!jp.features.some(f=>f.properties.country==='Japan'&&f.properties.dataKind==='modern-reference'));
 const source=read('japan-old-provinces.geojson');assert.equal(source.features.length,85);assert.ok(source.features.every(f=>f.properties.credit&&f.properties.license==='CC BY-NC 4.0'));
 const kr=divisions(1600);assert.ok(kr.features.some(f=>f.properties.label==='全罗道'));assert.ok(kr.features.some(f=>f.properties.label==='咸镜道'));
});

test('France, Mughal India and Ottoman Anatolia receive owner-scoped historic divisions',()=>{
 assert.ok(divisions(1600).features.some(f=>f.properties.label==='诺曼底'));
 assert.ok(divisions(1600).features.some(f=>f.properties.label==='比哈尔苏巴'));
 assert.ok(divisions(1650).features.some(f=>f.properties.label==='安纳托利亚行省'));
});

test('historic names cannot extend across the wrong owner, and unverified modern names are not printed in antiquity',()=>{
 const a=modern.features.find(f=>f.properties.country==='China'&&f.properties.native==='Zhejiang');
 const wrongWorld={type:'FeatureCollection',features:[{...a,properties:{NAME:'Other power'}}]};
 const result=regionsAtYear({type:'FeatureCollection',features:[a]},historical,wrongWorld,750);
 assert.ok(!result.features.some(f=>f.properties.label==='江南东道'||f.properties.id===a.properties.id));
 const sample=modern.features.filter(f=>['Brazil','United States of America','Australia'].includes(f.properties.country));const ancient=regionsAtYear({type:'FeatureCollection',features:sample},{type:'FeatureCollection',features:[]},{type:'FeatureCollection',features:[]},100);
 assert.equal(ancient.features.length,0);
});
