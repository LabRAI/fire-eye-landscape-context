# Digital local scenes

Design direction · 2 November 2026

Build a geographically anchored 3D model that people can navigate continuously
from the national map down to a neighborhood. Buildings, streets, plazas, water
and vegetation should be recognizable by their recorded positions and geometry.
Use restrained solid materials and simple geometry; photographic textures are
not the presentation goal. Orthophotography may support offline validation.

## What we take from the reference

BurnPro3D describes detailed vegetation and fire-behavior models, user-defined
ignition patterns, environmental conditions and a coupled fire/atmosphere model.
That suggests a useful separation between geographic scene objects, scenario
inputs and model outputs. It does not establish that our current renderer has
those simulation capabilities.

Its public Points2Pano entry was visually inspected on 2 November 2026 and uses
panoramic imagery. Our visual direction is modeled geometry. The main map exposes
a login dialog; its authenticated workflow and simulation implementation have
not been evaluated or reproduced.

Sources: https://burnpro3d.sdsc.edu/index.html and
https://burnpro3d.sdsc.edu/points2pano/?plot=CASBC_0014&ts=20240913,20241117&m=MDBH

## Scene layers and responsibilities

- **Ground:** a future terrain mesh from actual elevation data, with horizontal
  CRS, vertical datum, resolution and date. The present pilot uses a flat ground
  reference; the national atlas's elevation statistics are not a local DEM.
- **Built environment:** source building footprints, street/path geometry, water
  and mapped land areas. Missing heights and pavement widths remain unknown in
  the data contract; renderer estimates are separate.
- **Vegetation:** recorded tree points can place schematic 3D symbols. Canopy
  polygons describe canopy extent; they must not silently become measured tree
  stems. Local lidar or tree inventories are needed for more faithful structure.
- **Fire and weather:** the simulation owner supplies scenario logic, numerical
  results and animation. The data adapter supplies geography and provenance.
  Rendered flame effects alone do not demonstrate validated fire spread.

## First implementation

The shared renderer uses a single MapLibre canvas/camera. Buildings extrude from
mapped footprints; recorded trees transition from points to low-polygon symbols
at zoom 16–17. Streets, plazas, vegetation areas and water remain vector geometry.
The local scene no longer offers an aerial-photo layer. The main platform's
separate basemap choices are outside this scene change.

Tree symbols are generated only for source tree points. Each uses four small
octagonal extrusions, with a maximum crown radius of 2.4 m. Missing height uses
an 8 m **display-only** size. Valid positive source-tagged heights up to 120 m
are used for display; other values remain preserved in the source record and use
the display fallback. These shapes do not represent measured crowns, species,
fuel load or biomass. Clicking a symbol returns the original Point and nullable
attributes, never its render polygons as surveyed geometry.

The FSU sample has no recorded trees, so none are fabricated. Bryant Park has
565 source tree points. Both remain dated, limited extracts; this is not a
nationwide individual-tree reconstruction or building-level fire forecast.

## Next delivery to the simulation author

1. Select a small urban/wildland pilot with actual elevation and canopy/tree data.
2. Deliver a bounded, versioned scene manifest: WGS84 anchor, local metre CRS,
   terrain asset and vertical datum, source object IDs, provenance and null fields.
3. Agree the renderer interface for terrain, structures, vegetation and scenario
   outputs before adding fire animation. Keep measurements and display assumptions
   in separate objects.
4. Validate known landmarks, zoom continuity, object selection and mobile request/
   memory budgets. Serve prepared assets through HF/static hosting; never require
   a visitor to launch a national live-data query.

Detailed terrain and an event-conditioned spread engine remain future work.
The existing forecast values, native resolution and national atlas are unchanged.
