import type {FeatureCollection,Point} from 'geojson';
export function capitalsAtYear(world:FeatureCollection|null,year:number,index:unknown,identities:Record<string,string>):FeatureCollection<Point,{label:string;owner:string;ownerLabel:string;reference:boolean;source?:string;federationLabel?:string}>;
export function reviewedCapitals(index:unknown,id:string,year:number,name?:string):[string,[number,number],number|null,number|null,number|null,boolean,string,(string|null)?,(string|null)?][];
