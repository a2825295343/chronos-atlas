/** Strong, matte cartographic colors. Grey is reserved for areas without a polity. */
import {colorIdentity} from './color-identity.mjs';
import {polityColors} from './color-registry.mjs';
export const POLITY_PALETTE=['#d7a641','#65a6ce','#cf7a79','#79b08a','#ac87c9','#dc985e','#5da99e','#d58cac','#899bd2','#b5b35f','#a98467','#77bacc','#ba7990','#8caa62','#bd98ce','#c28b45','#7198b3','#bf7860','#83b7aa','#b89870','#a8bcd1','#cdb681','#8f85b3','#a9bc74'];
export function baseColor(name){const key=colorIdentity(name);if(polityColors[key])return polityColors[key];let h=2166136261;for(const c of key)h=Math.imul(h^c.charCodeAt(0),16777619);return POLITY_PALETTE[(h>>>0)%POLITY_PALETTE.length];}
const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
export function colorDistance(a,b){const x=rgb(a),y=rgb(b);return Math.hypot(...x.map((v,i)=>v-y[i]));}
export function colorPolities(collection){
 // Runtime colors must not depend on feature order, territory size, neighbors,
 // year, or browsing direction. Readability is planned in the fixed registry;
 // national border casing and occupation hatches remain independent of fills.
 return {...collection,features:collection.features.map(f=>({...f,properties:{...f.properties,thematicColor:baseColor(f.properties.controlArea?f.properties.controller:f.properties.NAME)}}))};
}
