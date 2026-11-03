import type {Fact,EntityFacts,FlagRecord} from './archive';
export function applies(row:{from?:number|null;to?:number|null;at?:number|null},year:number):boolean;
export function scopedFacts(entity:EntityFacts|undefined,field:string,year:number):{rows:Fact[];reference:boolean};
export function selectFlag(records:FlagRecord[],year:number):{flag:FlagRecord|undefined;reference:boolean};
export function cowPolityName(code:string,fallback:string,year:number):string;
export function leadershipFor(entity:EntityFacts|undefined,parent:EntityFacts|undefined,year:number):{rows:Fact[];fromSovereign:boolean;governmentRows:Fact[]};
