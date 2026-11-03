/** MapLibre 6.16 keeps the GPU mesh reusable when only elevation scale changes.
 * All dependent CPU sampling/depth state must change together. Fall back to the
 * public API if a later renderer changes this shape; package version is pinned.
 */
export function updateTerrainScale(map,scale){
 const terrain=map.terrain,coverage=terrain?.coverage;
 if(!terrain||!coverage||!Object.getOwnPropertyDescriptor(coverage,'exaggeration')?.writable||typeof coverage.reset!=='function'||typeof map.painter?.markTerrainDepthDirty!=='function')return false;
 terrain.exaggeration=scale;terrain.options.exaggeration=scale;
 coverage.exaggeration=scale;coverage.reset();
 map.painter.markTerrainDepthDirty();map.triggerRepaint();return true;
}
