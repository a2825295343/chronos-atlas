import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {scopedFacts,selectFlag} from '../src/archive-rules.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {dependenciesAt} from '../src/relationships.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const facts=read('public/data/polity-facts.json').entities,flags=read('public/data/flags.json').entities;
const world=y=>activePolities(read(`public/data/temporal/${Math.floor(y/100)}.geojson`),y);
const rulers=(q,y)=>scopedFacts(facts[q],'ruler',y).rows;
const has=(name,y,p)=>world(y).features.some(f=>f.properties.NAME===name&&pointInGeometry(p,f.geometry));

test('Ottoman flags before 1844 are sourced representative banners, not the future five-point flag',()=>{
 for(const y of [1305,1444,1516,1700,1750,1800,1843]){const flag=selectFlag(flags.Q12560,y).flag;assert.ok(flag,y);assert.ok(flag.representative&&flag.periodNote&&flag.periodSource,y);assert.ok(existsSync(new URL('../public'+flag.path,import.meta.url)));assert.ok(!flag.file.includes('1844–1922'));}
 assert.ok(selectFlag(flags.Q12560,1844).flag.file.includes('1844–1922'));
 assert.ok(selectFlag(flags.Q12560,1517).flag.file.includes('Zulfikar'));
 assert.equal(selectFlag(flags.Q70972,1415).flag.role,'王旗／王室纹章旗');
});

test('every Papal States year has an official pontiff term or documented vacancy',()=>{
 for(let y=755;y<=1870;y++){const rows=rulers('Q170174',y);assert.ok(rows.length,y);assert.equal(new Set(rows.map(r=>r.value)).size,rows.length);assert.ok(rows.every(r=>r.citation?.length));}
 assert.ok(rulers('Q170174',1444).some(r=>r.value==='Q167561'),'Eugene IV in 1444');
 assert.ok(rulers('Q170174',1269).some(r=>r.kind==='vacancy'));
 assert.ok(!rulers('Q170174',1046).some(r=>r.label.includes('本笃九')),'separate Benedict IX pontificates must not be bridged');
});

test('constituent crowns retain their own rulers and multiple contemporary appointments',()=>{
 assert.ok(rulers('local:austrian-hereditary-lands',1500).some(r=>r.label.includes('马克西米利安')));
 assert.ok(!rulers('local:austrian-hereditary-lands',1530).some(r=>r.label.includes('查理五')),'Charles handed Austrian government to Ferdinand in 1521');
 assert.ok(rulers('Q171348',1500).some(r=>r.label.includes('约翰')));
 assert.ok(rulers('Q49683',1500).some(r=>r.label.includes('亚历山大')),'Polish and Lithuanian crowns have different brothers in 1500');
 for(let y=1569;y<=1795;y++)assert.ok(rulers('Q172107',y).length,y);
 const e={fields:{ruler:[{value:'a',label:'A',from:1400,to:1450,roleLabel:'王位甲'},{value:'a',label:'A',from:1420,to:1460,roleLabel:'王位乙'}]}};
 const rows=scopedFacts(e,'ruler',1444).rows;assert.equal(rows.length,1);assert.deepEqual(new Set(rows[0].appointments.map(r=>r.roleLabel)),new Set(['王位甲','王位乙']));
});

test('Kalmar, Danish-Norwegian and Swedish-Norwegian unions are separate territorial crowns',()=>{
 for(const y of [1444,1475,1500]){const names=new Set(world(y).features.map(f=>f.properties.NAME));for(const n of ['Kingdom of Denmark','Kingdom of Norway','Kingdom of Sweden'])assert.ok(names.has(n),n+' '+y);assert.ok(!names.has('Kalmar Union'));assert.ok(!names.has('House of Oldenburg'));}
 for(const [n,y,p]of [['Kingdom of Denmark',1444,[10.39,55.4]],['Kingdom of Norway',1444,[10.75,59.91]],['Kingdom of Sweden',1475,[18.07,59.33]],['Kingdom of Norway',1850,[10.75,59.91]],['Kingdom of Sweden',1850,[18.07,59.33]]])assert.ok(has(n,y,p),n+' '+y);
 for(const y of [1500,1700,1850,1910])assert.ok(!world(y).features.some(f=>['Kalmar Union','Denmark-Norway','Sweden–Norway','United Kingdoms of Sweden and Norway'].includes(f.properties.NAME)),y);
 assert.ok(rulers('Q34',1475).some(r=>r.roleLabel?.includes('摄政')));
 const relations=read('public/data/curated-facts.json').relations;
 const union=y=>dependenciesAt(world(y),[],y,relations).filter(r=>r.kind==='union'&&[r.child,r.parent].includes('Kingdom of Denmark')&&[r.child,r.parent].includes('Kingdom of Sweden'));
 assert.equal(union(1475).length,0);assert.ok(union(1500).length);assert.equal(union(1505).length,0);
});

test('Jagiellon and Habsburg family names do not replace states or merge their crowns',()=>{
 for(const y of [1450,1500,1560]){const w=world(y);assert.ok(!w.features.some(f=>/^House of /.test(f.properties.NAME)));assert.ok(has('Crown of the Kingdom of Poland',y,[19.94,50.06]));assert.ok(has('Grand Duchy of Lithuania',y,[25.28,54.68]));}
 assert.ok(has('Austrian Hereditary Lands',1500,[16.37,48.21]));assert.ok(has('Kingdom of Bohemia',1560,[14.42,50.08]));
 assert.ok(has('Polish-Lithuanian Commonwealth',1570,[25.28,54.68]));
});

test('Ottoman-Mamluk wars have dated opponents, battle details and year-end conquest changes',()=>{
 const db=read('public/data/conflicts.json'),details=read('public/data/war-details.json');
 const war=warsAtYear(db,details,1516).find(w=>w.id==='historic-ottoman-mamluk-1516');assert.ok(war);
 assert.deepEqual(new Set(participantsAt(war,1516).map(p=>p.name)),new Set(['Ottoman Empire','Mamluk Sultanate']));
 assert.ok(war.detail.battles.some(b=>b.name.includes('达比克')));assert.ok(war.detail.cause&&war.detail.result&&war.detail.sources.length>=2);
 assert.ok(warInvolvesPolity(war,'Ottoman Empire',1516));assert.ok(warInvolvesPolity(war,'Mamluk Sultanate',1516));
 assert.ok(!warsAtYear(db,details,1518).some(w=>w.id===war.id));
 assert.ok(warsAtYear(db,details,1488).some(w=>w.id==='historic-ottoman-mamluk-1485'));
 assert.ok(!warsAtYear(db,details,1615).some(w=>w.id==='historic-dutch-revolt'),'twelve-year truce is not continuous war');
 assert.ok(has('Ottoman Empire',1516,[36.3,33.51]));assert.ok(has('Mamluk Sultanate',1516,[31.24,30.04]));
 assert.ok(has('Ottoman Empire',1517,[31.24,30.04]));assert.ok(!world(1517).features.some(f=>f.properties.NAME==='Mamluk Sultanate'));
});
