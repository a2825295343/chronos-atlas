import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {scopedFacts,selectFlag} from '../src/archive-rules.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';

const read=path=>JSON.parse(readFileSync(new URL('../public/data/'+path,import.meta.url),'utf8'));
const facts=read('polity-facts.json').entities;
const flags=read('flags.json').entities;
const cache=new Map();
function world(year){
 const century=Math.floor(year/100);
 if(!cache.has(century))cache.set(century,read(`temporal/${century}.geojson`));
 return activePolities(cache.get(century),year).features;
}
const find=(year,name)=>world(year).find(f=>f.properties.NAME===name);
const rulers=(qid,year,field='ruler')=>scopedFacts(facts[qid],field,year).rows;

test('Abbasid and Buyid archives use separate dated identities, leadership and banners',()=>{
 assert.deepEqual(rulers('Q12536',814).map(r=>r.label),['马蒙']);
 const black=selectFlag(flags.Q12536,814).flag;
 assert.match(black.role,/黑旗/);
 assert.ok(black.periodSource&&black.periodNote);
 const buyid=find(1014,'Buyid Dynasty');
 assert.equal(buyid.properties.qid,'local:buyid-state');
 assert.equal(buyid.properties.displayName,'布韦希王朝');
 assert.ok(rulers('local:buyid-state',1014).some(r=>r.label==='苏丹·道莱'));
 assert.deepEqual(rulers('local:buyid-state',1014,'imperialSovereign').map(r=>r.label),['卡迪尔']);
 assert.equal(selectFlag(flags['local:buyid-state']||[],1014).flag,undefined);
 assert.ok(find(1258,'Abbasid Caliphate'));
 assert.equal(find(1259,'Abbasid Caliphate'),undefined);
 assert.ok(pointInGeometry([44.4,33.3],find(1259,'Mongol Empire').geometry));
});

test('Bahrain has one territorial label per year and the correct emir and census',()=>{
 for(const year of [1973,1981,1991,2001,2002]){
  const entries=world(year).filter(f=>/of Bahrain$/.test(f.properties.NAME));
  assert.deepEqual(entries.map(f=>f.properties.NAME),[year<2002?'State of Bahrain':'Kingdom of Bahrain']);
 }
 assert.ok(rulers('Q398',1991).some(r=>r.value==='Q309650'));
 assert.ok(rulers('local:bahrain-sheikhdom',1910).some(r=>r.label.includes('本·阿里')));
 const census=read('historical-population.json')['State of Bahrain'];
 assert.equal(census[1991].population,508037);
 assert.equal(census[1992],undefined);
});

test('territorial identities switch at verified regime transitions',()=>{
 for(const [year,name] of [[1806,'Empire of Haiti'],[1807,'Divided Haiti'],[1820,'Republic of Haiti'],[1849,'Second Empire of Haiti'],[1859,'Republic of Haiti'],[1907,'Principality of Bulgaria'],[1908,'Kingdom of Bulgaria']]){
  assert.ok(find(year,name),`${year} ${name}`);
 }
 assert.equal(find(1807,'Empire of Haiti'),undefined);
 assert.equal(find(1908,'Principality of Bulgaria'),undefined);
});

test('the Hungarian revolution keeps its own 1849 archive and rejoins Austria from 1850',()=>{
 const government=find(1849,'Hungarian Nationalists');
 assert.equal(government.properties.qid,'local:hungarian-revolution');
 assert.equal(government.properties.displayName,'匈牙利革命政府');
 assert.ok(rulers('local:hungarian-revolution',1849).some(r=>r.value==='Q157040'));
 for(const year of [1850,1851,1852]){
  assert.equal(find(year,'Hungarian Nationalists'),undefined);
  assert.ok(pointInGeometry([19.05,47.5],find(year,'Austrian Empire').geometry));
 }
 for(const year of [1849,1850,1851,1852])assert.ok(!world(year).some(f=>f.properties.qid==='Q28513'));
 assert.ok(find(1868,'Austria-Hungary'));
 const war=warsAtYear(read('conflicts.json'),read('war-details.json'),1849).find(w=>w.id==='historic-hungarian-independence-1848');
 assert.ok(warInvolvesPolity(war,'Hungarian Nationalists',1849));
 assert.ok(warInvolvesPolity(war,'Austrian Empire',1849));
 assert.ok(participantsAt(war,1849).some(p=>p.name==='Russian Empire'));
 assert.ok(!participantsAt(war,1848).some(p=>p.name==='Russian Empire'));
});
