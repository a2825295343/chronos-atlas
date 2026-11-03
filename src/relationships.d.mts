import type {FeatureCollection} from 'geojson';
export function groupedAlliances(rows:any[],code:string,year:number):any[];
export function dependenciesAt(world:FeatureCollection|null,relations:any[],year:number,curated?:any[]):any[];

export function relationMembers(row:any):string[];
