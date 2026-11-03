import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {leadershipFor,scopedFacts} from '../src/archive-rules.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';

const read=path=>JSON.parse(readFileSync(new URL('../public/data/'+path,import.meta.url),'utf8'));
const facts=read('polity-facts.json').entities, identities=read('curated-facts.json').identities;
const shard=read('temporal/19.geojson');
const find=(name,year)=>activePolities(shard,year).features.find(f=>f.properties.NAME===name);
const idFor=f=>identities[f.properties.NAME]||f.properties.qid;
const heads=(id,field,year)=>scopedFacts(facts[id],field,year).rows;

test('Mussolini is government head in wartime Italy and leads the distinct northern regime',()=>{
 const italy=idFor(find('Kingdom of Italy',1941));
 const early=leadershipFor(facts[italy],undefined,1941);
 assert.ok(early.rows.some(r=>r.value==='Q150642'));
 assert.deepEqual(early.governmentRows.map(r=>r.value),['Q23559']);
 assert.deepEqual(heads(italy,'headOfGovernment',1943).map(r=>r.label).sort(),['彼得罗·巴多格里奥','贝尼托·墨索里尼'].sort());
 assert.ok(!heads(italy,'headOfGovernment',1944).some(r=>r.value==='Q23559'));
 assert.ok(heads(italy,'ruler',1944).some(r=>r.value==='Q187149'&&r.roleLabel.includes('代理')));
 const north=find('Italian Social Republic',1944);
 assert.equal(north.properties.controlArea,true);
 assert.deepEqual(heads(idFor(north),'ruler',1944).map(r=>r.value),['Q23559']);
 const portrait=read('portraits.json').people.Q23559;
 assert.ok(portrait.license&&existsSync(new URL('../public'+portrait.path,import.meta.url)));
});

test('wartime leadership records follow real countries and offices',()=>{
 for(const [year,name,field,label] of [
  [1916,'Kingdom of Italy','headOfGovernment','保罗·博塞利'],
  [1917,'French Third Republic','ruler','雷蒙·普恩加莱'],
  [1918,'Austria-Hungary','ruler','卡尔一世'],
  [1918,'United Kingdom of Great Britain and Ireland','headOfGovernment','劳合·乔治'],
  [1939,'Second Polish Republic','ruler','莫希齐茨基'],
  [1941,'Commonwealth of Australia','headOfGovernment','约翰·柯廷'],
  [1941,'Republic of China','ruler','林森'],
  [1943,'Republic of China','ruler','蒋介石'],
  [1943,'Empire of Japan','headOfGovernment','东条英机'],
  [1944,'Free French','ruler','戴高乐'],
  [1944,'Communist Party of China','ruler','毛泽东'],
 ]) {
  const f=find(name,year);
  assert.ok(f,`${year} ${name}`);
  assert.ok(heads(idFor(f),field,year).some(r=>r.label.includes(label)&&r.citation?.length),`${year} ${name} ${label}`);
 }
});

test('interwar and wartime countries expose the relevant leaders in the active archive',()=>{
 for(const [year,name,field,label] of [
  [1917,'Kingdom of Greece','ruler','亚历山大一世'],
  [1927,'Second Hellenic Republic','ruler','孔杜里奥蒂斯'],
  [1939,'Kingdom of Greece','headOfGovernment','梅塔克萨斯'],
  [1945,'Kingdom of Greece','ruler','达马斯基诺斯'],
  [1939,'Yugoslavia','ruler','保罗亲王'],[1944,'Yugoslav Partisans','ruler','铁托'],
  [1938,'Albania','ruler','佐古一世'],[1945,'Albania','headOfGovernment','恩维尔·霍查'],
  [1916,'Qajar Dynasty','ruler','艾哈迈德沙'],[1939,'Pahlavi Dynasty','ruler','礼萨·沙阿'],
  [1941,'Pahlavi Dynasty','ruler','穆罕默德·礼萨'],
  [1929,'Estonia','ruler','奥古斯特·雷伊'],[1939,'Estonia','ruler','康斯坦丁·佩茨'],
  [1939,'Republic of Latvia','ruler','乌尔马尼斯'],[1939,'Republic of Lithuania','ruler','斯梅托纳'],
  [1937,'Second Spanish Republic','ruler','阿萨尼亚'],[1937,'Second Spanish Republic','headOfGovernment','内格林'],
  [1936,'Spanish Nationalists','ruler','卡瓦内利亚斯'],[1937,'Spanish Nationalists','ruler','佛朗哥'],
  [1925,'Irish Free State','headOfGovernment','科斯格雷夫'],[1933,'Irish Free State','ruler','乌阿·布阿哈拉'],
  [1940,'Éire','ruler','海德'],[1940,'Éire','headOfGovernment','德·瓦莱拉'],
 ]) {
  const f=find(name,year);
  assert.ok(f,`${year} ${name}`);
  assert.ok(heads(idFor(f),field,year).some(r=>r.label.includes(label)&&r.citation?.length),`${year} ${name} ${label}`);
 }
});

test('China’s full-scale War of Resistance keeps a continuous public archive across the COW split',()=>{
 const database=read('conflicts.json'), details=read('war-details.json');
 for(const year of [1937,1941,1942,1945]){
  const wars=warsAtYear(database,details,year);
  const matching=wars.filter(w=>w.id==='cow-inter-130');
  assert.equal(matching.length,1);
  const [war]=matching;
  assert.equal(war.detail.title,'抗日战争（全面抗战）');
  assert.deepEqual([war.from,war.to],[1937,1945]);
  assert.deepEqual(participantsAt(war,year).map(p=>p.side),['1','2','2']);
  for(const name of ['Republic of China','Communist Party of China','Empire of Japan'])assert.ok(warInvolvesPolity(war,name,year));
 }
 assert.ok(!warsAtYear(database,details,1946).some(w=>w.id==='cow-inter-130'));
});
