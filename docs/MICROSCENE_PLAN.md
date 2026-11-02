# From regional landscape context to mapped local scenes

Research and implementation plan · updated 2 November 2026

## Objective

Keep the same geographic map and camera as the user zooms from CONUS to a
neighborhood and an individual building. Use mapped object geometry for scene
placement. Retain the existing regional distribution package as environmental
context; its 3 km cells cannot locate buildings, streets, plazas or individual trees.

The first shared-map pilot now reaches zoom 20 using mapped footprints and
streets. The earlier procedural illustration remains separately labelled.
Follow the [digital-scene direction](DIGITAL_SCENE_DIRECTION.md): geometric
models, real geographic anchors and explicit rendering assumptions.

## Data choices

| Feature | Primary candidate | Access and precision boundary |
| --- | --- | --- |
| Building outlines, parts and available heights | Overture Buildings; local government footprints where available | Versioned GeoParquet, bounding-box extraction; retain feature IDs, source attribution and optional heights. A footprint does not establish roof/facade details or current occupancy. |
| Street and path geometry | Overture Transportation and OpenStreetMap | Road/path segments are often centerlines, not surveyed pavement edges. Preserve mapped width when supplied; mark rendering assumptions separately. |
| Plazas, pedestrian areas, parks, water and land use | OpenStreetMap area geometry; Overture Base | Coverage varies. A named place point is not a plaza boundary. Preserve multipolygon holes and distinguish areas from line features. |
| Individual trees | Municipal inventories and mapped OpenStreetMap tree points | Exactness is limited to the inventory's location accuracy, survey date and coverage. No uniform national individual-tree guarantee. |
| Canopy and vegetation structure | Local canopy products; USGS 3DEP lidar; NAIP imagery for validation | Canopy polygons are not individual-tree stems. Lidar/imagery-derived crowns require processing and validation; source dates vary geographically. |
| Terrain | USGS 3DEP elevation and lidar | Use source resolution and vertical datum explicitly. Do not stretch a coarse regional mean into detailed hills. |
| Address lookup | Overture Addresses; official address/parcel data | Needed to find a target by street address; footprint coverage alone is not complete geocoding. |

Overture's published inspection PMTiles are explicitly not a production basemap
service. Use pinned source releases and build our own viewport-sized tiles for
HF/static delivery. Public Overpass instances are suitable for bounded research
extracts; do not make every visitor trigger large live queries.

## Incremental delivery

1. Verify official access methods and obtain small real neighborhood extracts.
2. Publish a geographic scene contract and reusable bounded extractor with source
   dates, IDs, licensing and explicit missing fields.
3. Implement a shared-map zoom transition: regional view → street geometry →
   building footprints and optional height extrusion. Keep the selected forecast
   issue and geographic anchor, and preserve return navigation.
4. Verify desktop/mobile behavior, known building/road alignment, incomplete data,
   source outages and request cancellation. Publish a limited, clearly identified
   pilot before claiming nationwide building-level scene coverage.
5. Scale with Overture/local-government batch ingestion, source-versioned PMTiles
   on HF, a small manifest, bounded browser caching, and source-specific refreshes.

## Coordinate and rendering contract

- WGS84 longitude/latitude for exchange; metre-based local projected coordinates
  for the simulation engine. Record origin, axes, CRS, vertical datum and units.
- Geometry and provenance remain separate from rendering parameters. Unknown
  building height, tree height, road width or survey date remains null.
- Preserve building multipolygons/holes, road junctions and pedestrian polygons.
- Ground terrain, building height and canopy height are distinct quantities.
- No invented buildings or trees are added to fill missing map data.
- Keep map and scene on one canvas/camera where possible. Load detail only near
  its zoom threshold, fade geometry progressively and reuse the geographic anchor.
- Building-level visualization does not increase the native forecast resolution
  and does not establish building-level fire probability or fire-spread validity.

## Official references

- Overture access and production-tile warning: https://docs.overturemaps.org/getting-data/cloud-sources/
- Overture buildings: https://docs.overturemaps.org/guides/buildings/
- Overture transportation: https://docs.overturemaps.org/guides/transportation/
- Overture extraction: https://docs.overturemaps.org/getting-data/
- Overture release catalog: https://stac.overturemaps.org/catalog.json
- OpenStreetMap Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API
- OpenStreetMap attribution and license: https://www.openstreetmap.org/copyright
- USGS The National Map access: https://tnmaccess.nationalmap.gov/api/v1/docs
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program
- MapLibre geographic buildings: https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/
- MapLibre shared-map 3D integration: https://maplibre.org/maplibre-gl-js/docs/examples/add-3d-tiles-3d-objects-and-models-using-threejs/

See the implementation/validation record for which sources and areas were
actually downloaded and tested. A candidate in this table is not a claim that
its complete national inventory has already been integrated.
