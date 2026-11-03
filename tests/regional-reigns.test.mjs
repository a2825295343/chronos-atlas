import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {leadershipFor} from '../src/archive-rules.mjs';

const read = path => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const {entities} = read('../public/data/polity-facts.json');

test('1504 Moghul courts have separate map labels and rulers', () => {
 const active = read('../public/data/temporal/15.geojson').features
  .map(f => f.properties).filter(p => p.validFrom <= 1504 && p.validTo >= 1504);
 assert.ok(!active.some(p => p.displayName === '蒙兀儿斯坦'));
 for (const [qid, label, ruler] of [
  ['local:moghul-eastern-court', '东部蒙兀儿汗廷', '曼速儿汗'],
  ['local:moghul-western-court', '西部蒙兀儿汗廷', '马哈木汗'],
 ]) {
  assert.equal(active.filter(p => p.qid === qid && p.displayName === label).length, 1);
  assert.ok(leadershipFor(entities[qid], undefined, 1504).rows.some(row => row.label === ruler));
 }
});

test('dated leaders are shown in the corresponding regional archives', () => {
 for (const [qid, year, ruler] of [
  ['Q582861', 1444, '阿卜杜勒·哈克二世'], ['Q307697', 1444, '艾哈迈德一世'],
  ['Q752662', 1444, '奥斯曼'], ['Q970799', 1504, '穆罕默德·布尔图卡利'],
  ['Q1136188', 1580, '艾哈迈德·曼苏尔'], ['Q4332415', 1444, '也先'],
  ['Q487829', 1444, '也先不花二世'], ['Q79965', 1444, '库楚克·穆罕默德'],
  ['Q484195', 1504, '侯赛因·拜哈拉'], ['Q4083686', 1504, '阿拉丁·侯赛因沙'],
  ['Q2500952', 1444, '那罗波帝一世'], ['Q4948', 1504, '莱昂纳多·洛雷丹'],
  ['Q174306', 1504, '克莱沃的菲利普'], ['Q48189', 1444, '康拉德·冯·埃利希斯豪森'],
 ]) {
  assert.ok(leadershipFor(entities[qid], undefined, year).rows.some(row =>
   row.label === ruler && row.citation?.[0]), [qid, year, ruler].join(' '));
 }
 assert.ok(!leadershipFor(entities.Q970799, undefined, 1551).rows.some(row =>
  row.supplement === 'maghreb-and-eurasian-reigns'));
});
