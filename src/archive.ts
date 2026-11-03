import {applies,scopedFacts,selectFlag} from './archive-rules.mjs';
export {applies,scopedFacts,selectFlag};
import {useEffect,useState} from 'react';
import curated from '../public/data/curated-facts.json';
export type Fact={value:string|number;label:string;from:number|null;to:number|null;at:number|null;rank?:string;citation?:string[];derived?:boolean;approximate?:boolean;inference?:string;dateSource?:string;verifiedThrough?:number;reviewedAt?:string;kind?:string;reviewAfter?:number;reviewNote?:string;roleLabel?:string;appointments?:Fact[]};
export type EntityFacts={label:string;en:string;description:string;fields:Record<string,Fact[]>;rulerScopeNote?:string};
export type FlagRecord={path:string;file:string;from:number|null;to:number|null;at:number|null;license:string;artist:string;commons:string;source:string;role?:string;periodNote?:string;periodSource?:string;representative?:boolean};
type ArchiveData={facts:{entities:Record<string,EntityFacts>};flags:{entities:Record<string,FlagRecord[]>;count:number};diplomacy:{countries:Record<string,string>;alliances:any[];wars:any[];coverage:{alliances:number[];wars:number[]}};relations:any[]};
let pending:Promise<ArchiveData>|undefined;
export const curatedData=curated as any;
export function identityFor(name:string,qid?:string){return (curated.identities as Record<string,string>)[name]||qid||'';}
export function useArchive(){
 const [data,setData]=useState<ArchiveData|null>(null);
 useEffect(()=>{let cancelled=false;pending??=Promise.all(['/data/polity-facts.json','/data/flags.json','/data/diplomacy.json','/data/temporal/relations.json'].map(url=>fetch(url,{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error(url);return r.json();}))).then(([facts,flags,diplomacy,relations])=>({facts,flags,diplomacy,relations}));pending.then(value=>{if(!cancelled)setData(value);}).catch(()=>{});return()=>{cancelled=true;};},[]);
 return data;
}
export {cowCode} from './country-codes.mjs';
