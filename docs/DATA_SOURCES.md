# Building-scale scene data: access and selection

Checked 1 November 2026. This document separates working integrations from
candidates. It does not claim survey-level accuracy or complete national coverage
for individual trees, building heights, plaza boundaries or address points.

| Need | Source and API / access | Use in this delivery |
| --- | --- | --- |
| CONUS building outlines and optional attributes | Overture Buildings, versioned GeoParquet and STAC catalog | Verified public catalog; national bulk-ingestion candidate. Latest catalog release at this check: 2026-10-21.0. Not downloaded nationwide. |
| Roads, paths and connectivity | Overture Transportation; OpenStreetMap | OSM streets appear in the shared-map viewer. Two bounded OSM extracts preserve complete available object geometry. Centerlines are not pavement polygons. |
| Building-level basemap | OpenFreeMap / OpenMapTiles, sourced from OSM | Integrated. Planet metadata reported native vector tiles through zoom 14; deeper zoom enlarges/derives display from those tiles. Native building geometry is not a 5 km forecast-grid refinement. |
| Plazas, pedestrian surfaces, greenspace, water and tagged trees | OSM object geometries and tags | Integrated in the two sample extracts. Missing mapped features remain missing. A tree point is drawn at its source coordinate, with a symbolic radius. |
| Aerial reference for roofs, pavement, plazas and canopy | USGS / USDA The National Map orthophotography | Optional viewer layer. Service description says ground resolution varies from six inches to one metre. Cache zoom levels do not guarantee new detail at every level. Dates vary by place; the service's refresh text is not a per-image acquisition date. |
| Terrain elevation and vertical vegetation structure | USGS 3DEP 1 m DEM where available, lidar point clouds and other elevation products | Dataset-discovery API verified. Detailed terrain processing is a next-stage adapter; no terrain-following physical simulation is claimed here. |
| Finding a building by address | Overture Addresses; official local address points | Candidate for address-index ingestion. The current main Fire-eye search remains city/county/state/coordinate/incident based; nationwide street-address geocoding is not newly delivered. |
| Authoritative local footprints, parcels, sidewalks, plazas and tree inventories | City/county GIS, commonly ArcGIS REST FeatureServer services | Prefer when coverage, date and license are suitable. Service URL and owner must be checked individually. A parcel is not a building footprint. |
| Alternative national building outlines | Microsoft US Building Footprints | Candidate / cross-check source. Do not independently merge overlapping inventories without deduplicating and retaining provenance. |
| Photorealistic 3D city surfaces | Google Map Tiles Photorealistic 3D Tiles | Optional paid path requiring API credentials, billing and attribution/usage compliance. No key or billing was enabled, and tiles were not copied into our archives. |

## Working endpoints and recipes

### Overture

- Documentation: https://docs.overturemaps.org/getting-data/
- Version catalog: https://stac.overturemaps.org/catalog.json
- Buildings: https://docs.overturemaps.org/guides/buildings/
- Transportation: https://docs.overturemaps.org/guides/transportation/
- Addresses: https://docs.overturemaps.org/guides/addresses/

Read the current catalog, pin a release, and run bounded GeoParquet queries with
the documented CLI or DuckDB. Check the per-theme/feature licenses and source
attribution. Produce our own versioned PMTiles/GeoJSON for delivery. Overture's
inspection PMTiles explicitly do not provide production-basemap support:
https://docs.overturemaps.org/getting-data/cloud-sources/

### OpenStreetMap and OpenFreeMap

- Bounded research query used for FSU: https://api.openstreetmap.org/api/0.6/map.json?bbox=-84.300,30.441,-84.295,30.445
- OSM API reference: https://wiki.openstreetmap.org/wiki/API_v0.6
- Overpass documentation: https://wiki.openstreetmap.org/wiki/Overpass_API
- OpenFreeMap style: https://tiles.openfreemap.org/styles/bright
- Vector tile catalog: https://tiles.openfreemap.org/planet
- Source license: https://www.openstreetmap.org/copyright

The USGS imagery cache returned a real image at zoom 16 in the FSU test and 404 at zoom 17. The viewer therefore caps imagery requests at native tile zoom 16 and enlarges those images at closer camera scales; it does not imply finer imagery content.

The main Overpass endpoint and an alternate timed out during bounded tests on
this date; the OSM map API succeeded. This is evidence for using offline extracts
and a static serving layer, not an uptime assessment of those services. Neither
public query service is wired to per-visitor scene requests. Source editor names
are omitted from the published extracts. Retrieval dates are not survey dates.

### Terrain and orthophotography

- Dataset discovery: https://tnmaccess.nationalmap.gov/api/v1/datasets
- Product search: https://tnmaccess.nationalmap.gov/api/v1/products
- API documentation: https://tnmaccess.nationalmap.gov/api/v1/docs
- Image service metadata: https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer?f=json
- 3DEP: https://www.usgs.gov/3d-elevation-program

Use the dataset tags returned by the discovery API, rather than guessing product
names. Verified tags include USDA National Agriculture Imagery Program (NAIP),
Digital Elevation Model (DEM) 1 meter, and Lidar Point Cloud (LPC). Search products
with a target bounding box and preserve acquisition metadata, horizontal/vertical
CRS and resolution. Lidar-derived crowns and imagery segmentation are inferred
products that require validation; they are not automatically exact tree locations.

### Local authorities and alternatives

- Tallahassee / Leon County GIS: https://www.tlcgis.org/
- Open data entry point: https://tlcgis-topographic-datastore-hub-leoncountyfl.hub.arcgis.com/
- Microsoft US footprints: https://github.com/microsoft/USBuildingFootprints
- Google 3D tile policies: https://developers.google.com/maps/documentation/tile/policies
- MapLibre building rendering: https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/
- Shared-map 3D engine integration: https://maplibre.org/maplibre-gl-js/docs/examples/add-3d-tiles-3d-objects-and-models-using-threejs/

Google's tile policies restrict use to visualization and prohibit several
non-visualization uses, including image analysis and machine interpretation.
Do not treat those tiles as a source for tree extraction, model training or
scientific scene-data archives. Use appropriately licensed imagery/lidar for
those tasks.

Local-government datasets remain a research/ingestion stage. For example, the
documented NYC 2015 tree-census metadata endpoint returned 404 in this environment;
that inventory was not used or substituted silently. The New York sample in this
release contains OSM tree points, not a claimed current municipal census.

## Scaling without laboratory-server requests

Scheduled backend jobs should download changed source releases, validate and
deduplicate object geometry, then publish immutable data objects to HF. GitHub
Pages serves the small frontend and catalog. Browsers request only nearby tiles,
reuse cached geometry and cancel obsolete requests. A source-specific failure
keeps the last verified data or the ordinary basemap available.

Refresh geography according to its source release schedule; do not rebuild
unchanged buildings every forecast cycle. Keep dynamic fire/weather timestamps
separate. A forecast at native 5 km resolution remains a 5 km model field even
when a detailed street or roof is visible underneath it.
