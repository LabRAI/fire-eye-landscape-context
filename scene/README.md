# Geographic scenes: a second, finer layer

The original national atlas supplies environmental distributions. This module
adds actual mapped object geometry and a shared MapLibre camera. It is an initial
geographic visualization layer; physical fire propagation is still owned by the
simulation implementation.

## A small, auditable extract

~~~sh
cd scene
npm ci --ignore-scripts
node extract-osm.mjs --bbox -84.300,30.441,-84.295,30.445 --out examples/fsu
~~~

This command is for occasional bounded research extracts. It uses the official
OpenStreetMap API, preserves mapped geometry, discards incomplete features and
records source IDs, attribution, a retrieval date and a file hash. It does not
copy editor names or invent building/tree heights. A saved raw API response can
be passed with --input and --retrieved-at (its original download timestamp) for reproducibility. Repackaging a saved response does not refresh its source date.

Do not use the editing API or shared Overpass servers as a production tile
backend. Prepare versioned local extracts/tiles offline and deliver them through
HF/static hosting. Use Overture bulk data and local-government sources for scale.

## Rendering

geographic-scene.js mounts on an existing MapLibre map; it does not create a
second scene canvas or relocate the selected coordinate. The shared camera
supports zoom 20. Street-scale geometry appears gradually, and building
extrusion begins at neighborhood scale. The existing regional forecast is
visually reduced at high zoom; its values and resolution are unchanged.

The public basemap uses OpenFreeMap's OpenStreetMap/OpenMapTiles vector tiles.
Their render_height is a display property, not proof of surveyed building height.
The optional USGS aerial layer helps inspect recognizable geometry and canopy;
its acquisition dates vary and its imagery is not live. Increasing zoom above a
tile's native scale only magnifies that tile.

The full 3D animation engine should consume the geographic object contract in
[OBJECT_CONTRACT.md](OBJECT_CONTRACT.md), replacing procedural placement where
real geometry is available. It must retain unknown areas and fields explicitly.

## Attribution

OpenStreetMap-derived extracts: © OpenStreetMap contributors, ODbL 1.0.
https://www.openstreetmap.org/copyright

OpenFreeMap / OpenMapTiles provide the displayed vector basemap. USGS / USDA
The National Map provides optional orthophotography. Original source terms and
attribution remain applicable. osmtogeojson is a separately installed dependency;
its own license accompanies that package.

To run the complete downloaded demo locally, serve the handoff root with python -m http.server 8000, then open http://localhost:8000/demo/. The online demo loads public map tiles; the national atlas query is independent and works offline once its Python dependencies are installed.
