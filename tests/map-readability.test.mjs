import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {baseColor,colorDistance} from '../src/colors.mjs';

const read = name => JSON.parse(readFileSync(new URL('../public/data/'+name,import.meta.url),'utf8'));

test('major neighbors keep distinct stable colors including the requested blues and reds',()=>{
 for(const [a,b] of [
  ['Republic of Venice','Austrian Hereditary Lands'],['Republic of Venice','Ottoman Empire'],
  ['Kimek-Kipchak confederation','Mongol Empire'],['United States','French Fourth Republic'],
  ['Union of Soviet Socialist Republics',"People's Republic of China"],
 ]) assert.ok(colorDistance(baseColor(a),baseColor(b))>60,a+' / '+b);
 for(const name of ['United States','French Fourth Republic']){
  const [r,g,b]=baseColor(name).slice(1).match(/../g).map(x=>parseInt(x,16));
  assert.ok(b>g&&g>r);
 }
 for(const name of ['Union of Soviet Socialist Republics',"People's Republic of China"]){
  const [r,g,b]=baseColor(name).slice(1).match(/../g).map(x=>parseInt(x,16));
  assert.ok(r>g&&r>b);
 }
});

test('1600–1601 Japan covers Osaka, Edo and northern Kyushu',()=>{
 const shard=read('temporal/16.geojson');
 for(const year of [1600,1601]){
  const japan=activePolities(shard,year).features.find(f=>f.properties.NAME==='Tokugawa Government');
  for(const point of [[135.5,34.7],[139.7,35.7],[130.4,33.6]])assert.ok(pointInGeometry(point,japan.geometry),point.join(','));
 }
});

test('Chukotka spans the antimeridian in Soviet and modern map frames',()=>{
 for(const [year,owner] of [[1950,'Union of Soviet Socialist Republics'],[2024,'Russian Federation']]){
  const world=activePolities(read('temporal/'+Math.floor(year/100)+'.geojson'),year);
  const polity=world.features.find(f=>f.properties.NAME===owner);
  for(const point of [[177,65.5],[-171,65.8]])assert.ok(pointInGeometry(point,polity.geometry),point.join(','));
 }
});
