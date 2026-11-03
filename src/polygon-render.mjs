/** Keep disconnected polygons as independent tile features. Tiny exterior rings
 * can reverse winding during low-zoom integer quantization; when a MultiPolygon
 * is flattened into one ring list, that ring can make a continent look like a
 * hole. Splitting components isolates that ambiguity without changing any
 * coordinates, actual holes, country identity, or the historical source data.
 */
export function polygonRenderParts(collection,projectProperties=p=>p){
 let id=0;
 return {type:'FeatureCollection',features:collection.features.flatMap(feature=>{
  const geometry=feature.geometry,properties=projectProperties(feature.properties);
  const parts=geometry?.type==='Polygon'?[geometry.coordinates]:geometry?.type==='MultiPolygon'?geometry.coordinates:[];
  return parts.map(coordinates=>({type:'Feature',id:id++,properties,geometry:{type:'Polygon',coordinates}}));
 })};
}
