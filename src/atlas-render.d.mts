import type {FeatureCollection} from 'geojson';
export function buildAtlasFrame(data:FeatureCollection,localize?:(name:string)=>string):FeatureCollection;
export function countryGlyphs(features:FeatureCollection['features'],localize?:(name:string)=>string):FeatureCollection;
