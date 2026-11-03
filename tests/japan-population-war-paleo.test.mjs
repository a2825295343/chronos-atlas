import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {cowCode} from '../src/country-codes.mjs';
import {scopedFacts,selectFlag} from '../src/archive-rules.mjs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
import {paleogeographyAt} from '../src/paleogeography.mjs';
import {regionsAtYear} from '../src/regions.mjs';
import {nationalObservation,comparableEconomy} from '../src/statistics-policy.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../public/data/'+p,import.meta.url)));
const facts=read('polity-facts.json'),countries=read('diplomacy.json').countries;
test('ROC uses the Taiwan statistical jurisdiction after 1949, including 1991',()=>{
 assert.equal(cowCode('Republic of China',undefined,countries,1930),'710');
 const code=cowCode('Republic of China',undefined,countries,1991);
 assert.equal(code,'713');const n=read('national-strength.json').countries[code].observations['1991'];
 assert.equal(n.population,20557000);assert.ok(n.population<3e7);
 assert.equal(cowCode('East Germany',undefined,countries,1980),'265');
 assert.equal(cowCode('West Germany',undefined,countries,1980),'260');
 assert.equal(cowCode('Democratic Republic of Vietnam',undefined,countries,1968),'816');
 assert.equal(cowCode('Republic of Vietnam',undefined,countries,1968),'817');
 assert.equal(cowCode('Socialist Republic of Vietnam',undefined,countries,1980),'816');
 const nmc=read('national-strength.json');
 const soviet=nationalObservation(nmc,'365',1991,'Soviet Union');
 assert.ok(soviet.population>2.8e8);assert.equal(soviet.observationYear,1989);assert.equal(soviet.reference,true);
 assert.ok(nationalObservation(nmc,'365',1991,'Russian Federation').population<1.6e8);
 for(const [iso,y,name]of [['DEU',1980,'Federated Republic of Germany'],['VNM',1968,'Republic of Vietnam'],['VNM',1968,'Democratic Republic of Vietnam'],['PAK',1970,'Pakistan'],['SDN',2000,'Sudan'],['ETH',1980,'Ethiopia'],['YEM',1980,'Yemen'],['MYS',1964,'Malaysia']])assert.equal(comparableEconomy(iso,y,name),false,`${iso} ${y}`);
 assert.equal(comparableEconomy('VNM',1980,'Socialist Republic of Vietnam'),true);
 assert.equal(comparableEconomy('DEU',2000,'Germany'),true);
});
test('Vietnam wars link to dated participants across country name variants',()=>{
 const db=read('conflicts.json'),details=read('war-details.json');
 const w=warsAtYear(db,details,1968).find(w=>w.id==='ucdp-293'||w.id==='cow-inter-163');assert.ok(w);
 for(const name of ['Democratic Republic of Vietnam','Republic of Vietnam','United States of America','Republic of Korea','Australia','Kingdom of Thailand'])assert.ok(warInvolvesPolity(w,name,1968),name);
 const participants=participantsAt(w,1968),north=participants.filter(p=>String(p.code)==='816');assert.equal(north.length,1);
 assert.ok(participants.some(p=>p.name==='National Liberation Front of South Vietnam'&&p.side===north[0].side));
 assert.equal(warInvolvesPolity(w,'Republic of China',1968),false);
 assert.equal(warInvolvesPolity(w,'United States of America',1974),false);
 const sino=warsAtYear(db,details,1979).find(w=>w.id==='cow-inter-193'||w.also?.some(x=>x.id==='cow-inter-193'));assert.ok(sino);
 assert.ok(warInvolvesPolity(sino,'Socialist Republic of Vietnam',1979));
 assert.ok(facts.entities.Q172640.fields.ruler.some(r=>r.label==='胡志明'&&r.from<=1968&&1968<=r.to));
});
test('Japanese bakufu, imperial court and shikken display distinct named offices',()=>{
 const rows=(q,field,y)=>scopedFacts(facts.entities[q],field,y).rows;
 for(const [q,y,name]of [['Q205662',1604,'德川家康'],['Q205662',1610,'德川秀忠'],['Q205662',1700,'德川纲吉'],['Q205662',1867,'德川庆喜'],['Q736839',1260,'宗尊'],['Q1154406',1430,'足利义教'],['local:japanese-imperial-court',750,'孝谦'],['local:japanese-imperial-court',1000,'一条'],['Q188712',1868,'明治']])assert.ok(rows(q,'ruler',y).some(r=>r.label.includes(name)),`${q} ${y} ${name}`);
 assert.ok(rows('Q736839','headOfGovernment',1260).some(r=>r.label.includes('北条长时')));
 assert.ok(rows('Q205662','imperialSovereign',1604).some(r=>r.label.includes('后阳成')));
 assert.ok(rows('Q736839','ruler',1200).some(r=>r.label.includes('源赖家')));
 assert.ok(rows('Q1154406','ruler',1444).some(r=>r.kind==='vacancy'&&r.label.includes('1449')));
 assert.ok(read('japan-complete-review.json').people>=150);
 const flag=selectFlag(read('flags.json').entities.Q188712,1868).flag;
 assert.ok(flag?.representative&&flag.periodSource&&flag.periodNote.includes('1854'));
});
test('1868–69 Japanese home islands have actors rather than a dissolved shogunate',()=>{
 const shard=read('temporal/18.geojson');
 for(const year of [1868,1869]){
  const world=activePolities(shard,year);
  assert.ok(!world.features.some(f=>f.properties.NAME==='Tokugawa Shogunate'));
  for(const p of [[139.7,35.7],[135.5,34.7],[135.75,35],[140.74,41.77],[141.35,43.07]])assert.ok(world.features.some(f=>pointInGeometry(p,f.geometry)),`${year} ${p}`);
  assert.ok(world.features.some(f=>f.properties.NAME==='Ezo Island Government'));
 }
 const active=warsAtYear(read('conflicts.json'),read('war-details.json'),1868);
 assert.equal(active.filter(w=>w.detail?.title==='戊辰战争').length,1);
 assert.ok(!active.some(w=>w.id==='historic-boshin-reviewed'));
 const w=active.find(w=>w.detail?.title==='戊辰战争');assert.ok(w);
 assert.ok(warInvolvesPolity(w,'Empire of Japan',1868));assert.ok(warInvolvesPolity(w,'Northern Alliance of Japanese Domains',1868));
 assert.equal(warInvolvesPolity(w,'Northern Alliance of Japanese Domains',1869),false);
});
test('military intervention does not paint South Vietnam as US sovereign territory',()=>{
 const shard=read('temporal/19.geojson');
 for(const [y,name]of [[1968,'Republic of Vietnam'],[1991,'Socialist Republic of Vietnam']]){
  const world=activePolities(shard,y);
  assert.ok(world.features.some(f=>f.properties.NAME===name&&pointInGeometry([106.7,10.8],f.geometry)));
  assert.ok(!world.features.some(f=>f.properties.NAME==='United States of America'&&pointInGeometry([106.7,10.8],f.geometry)));
  if(y===1991)assert.ok(!world.features.some(f=>f.properties.NAME==='Republic of China'&&pointInGeometry([110,19.5],f.geometry)));
 }
});
test('global historical names change by era without claiming modern administrative borders',()=>{
 const modern=read('provinces.geojson'),history=read('historical-provinces.geojson'),empty={type:'FeatureCollection',features:[]};
 for(const [year,p,label]of [[1800,[-0.8,52.2],'北安普敦'],[1450,[-89.5,20.8],'尤卡坦'],[-100,[35,39],'卡帕多西亚'],[1800,[36,33.5],'']]){
  if(!label)continue;
  const c=regionsAtYear(modern,history,empty,year);
  assert.ok(c.features.some(f=>f.properties.label.includes(label)&&!f.properties.suppressLabel&&pointInGeometry(p,f.geometry)),`${year} ${label}`);
 }
 const ref=history.features.find(f=>f.properties.geographicReference);assert.equal(ref.properties.boundaryVisible,false);
 assert.ok(read('global-historical-regions-review.json').countries.length>=35);
 const old=regionsAtYear(modern,history,empty,1860);
 const virginia=old.features.find(f=>f.properties.native==='Virginia');
 assert.ok(virginia&&!virginia.properties.suppressLabel);
 assert.equal(virginia.properties.boundaryVisible,false);
});
test('paleocoasts use BP dating and real submerged shelves, not fixed modern land',()=>{
 const index=read('paleogeography/index.json');
 assert.equal(paleogeographyAt(index,1444),null);
 const glacial=paleogeographyAt(index,-19000);assert.ok(glacial.level<=-110&&glacial.level>=-130);
 // The published estimate near 125 ka is -6.65 ±9.21m; do not override it
 // with a generic interglacial highstand or ignore the BP/BC offset.
 assert.ok(paleogeographyAt(index,-123000).estimate>=-8&&paleogeographyAt(index,-123000).estimate<=-4);
 const modern=read('paleogeography/land-p0.geojson').features[0].geometry;
 const ancient=read('paleogeography/land-m60.geojson').features[0].geometry;
 for(const p of [[110,-5],[3,55]]){assert.equal(pointInGeometry(p,modern),false);assert.equal(pointInGeometry(p,ancient),true);}
 const zones=read('paleogeography/cultures-m60.geojson').features;
 assert.ok(zones.some(f=>f.properties.displayName.includes('巽他')&&pointInGeometry([110,-5],f.geometry)));
 assert.ok(zones.every(f=>f.properties.representationKind==='human-presence'&&f.properties.regionalCollection));
 assert.ok(index.limitations.some(s=>s.includes('冰川均衡')));
});
