# CONUS landscape context — simulation handoff

This package describes the landscape at a selected longitude/latitude. The
simulation author owns scene construction, animation and any spread model.
The data adapter supplies real terrain and land-cover context, without an LLM
choosing a landscape or pre-rendering the country.

## What to use

- **conus_cells.csv.gz**: all source-CONUS-intersecting 3 km cells, including
  WGS84 coordinate envelopes, terrain and each landscape fraction. This is the
  requested geographic distribution file. It includes cells with missing data.
- **conus_context.npz + manifest.json**: the same national index in a compact
  form for fast coordinate lookup. The core archive is about 20 MB.
- **query.py / context.py**: offline lookup and an optional local-patch reader.
- **response.schema.json / taxonomy.json**: response contract and the complete,
  explicit mapping of source vegetation types to broad scene categories.
- **examples/**: twelve real locations, each with a national-cell response and
  a more detailed local response. **landscape_examples.png** previews these data.
- **source_metadata/**, **source_notes.json**, **validation.json** and
  **checksums.json**: source editions, caveats, checks and package integrity.

The CSV's longitude/latitude bounds are corner envelopes of projected squares,
not non-overlapping longitude/latitude rectangles. Use the provided projected
lookup to choose a cell; do not match overlapping envelopes by first occurrence.
Row and column indices are zero-based. Counts retain the original 30 m support.
The extent comes from the source product's unbuffered CONUS polygons; the
Florida Keys and other coastal locations are retained. It is not a surveyed
coastline or a new jurisdiction boundary.

## Simple offline integration

Use Python 3.11+ and install the three packages in requirements.txt, then run
from the handoff folder. Native-patch mode and the optional unit tests also
require rasterio:

```sh
python query.py --bundle . --longitude -84.28 --latitude 30.45 --output scene.json
```

For repeated requests, keep one instance loaded in the backend:

```python
from context import Atlas
atlas = Atlas('/path/to/handoff')
context = atlas.query(lon=-84.28, lat=30.45)
```

Coordinates are WGS84, **longitude first, latitude second**. The response retains
the original selection and identifies the actual returned footprint.

## What the renderer receives

**Surface composition** contains eight mutually exclusive fractions: forest /
woodland, shrubland, grass / herbaceous, agriculture, developed land, open water,
sparse / barren land, snow / ice. Fractions sum to one over valid mapped cover;
coverage and unknown area are separate. These are ground-area fractions, not
tree-canopy percentage, structure density, asset counts or fire probability.
Agriculture includes crops, pasture/hay and woody cultivation; developed land
includes roads and developed open space. Do not render all agriculture as one
crop or all developed cells as building footprints.

**Terrain** supplies elevation mean/minimum/maximum in metres, local relief,
mean slope in degrees and the share of slopes at least 15 degrees. The flat,
rolling, hilly and rugged labels are transparent rendering heuristics; numeric
values should control terrain geometry. Terrain labels depend on footprint size.

**Overlapping tags** preserve riparian/wetland vegetation, explicitly
desert-named ecosystems and developed vegetation. Do not add their fractions to
the eight surface classes. A riparian forest remains forest. Sparse ground is
not automatically desert. Open water includes lakes and rivers; this release
does not identify channel names, centerlines, current flow or water depth.

`scene_components` lists classes covering at least 10% of mapped cover for easy
asset selection. It is only a convenience label: use the full composition and
layout to preserve smaller but important water or developed features. No class
automatically establishes that a location can or cannot burn.

## Local placement: the recommended second step

The national file is deliberately regional context. It cannot tell an author
where a river or hillside sits within a 200 m scene. For placement, the included
reader extracts a small actual window from the native rasters:

```sh
python query.py --local --sources source_paths.json \
  --longitude -90.070 --latitude 35.15 --width-m 3000 --output river_scene.json
```

Start with source_paths.example.json and supply the real local raster paths.
This mode was validated with the original source rasters. The large source rasters are
not duplicated in this handoff, and no new public HTTP endpoint is deployed.
Agree on file exchange or a backend endpoint when wiring the simulation.

The local response includes a spatial grid with per-cell cover mixtures,
elevation and slope. A 3 km request returns 50 × 50 cells at 60 m spacing;
values come from 30 m source pixels. Requests from 300–6,000 m are supported.
Small requests can retain 30 m cells. Actual bounds are snapped outward in size
to the native grid and recorded explicitly. For a 200 m scene, request at least
300 m and crop by projected coordinates around the selected point.
The national query returns the containing fixed cell; the local query centres
a square near the selected point. Their footprints and mixture percentages can
therefore differ. Compare the returned bounds before comparing distributions.

Arrays are row-major, first row at the northern edge in EPSG:5070; rows proceed
south, columns east. `origin_upper_left_m` is the outer cell corner. Sample
centres are `(x0 + (column + 0.5)*spacing, y0 - (row + 0.5)*spacing)`. Projected
grid north is not exactly true north. Use the supplied transform when positioning
assets. Elevation is an absolute source value; subtract a local base for rendering.
The grid is aggregated measured/classified input, not synthetic terrain noise.
For a partly covered grid cell, multiply a class's cover_fraction by
known_cover_fraction to obtain its share of the entire cell. Leave the remaining
area unknown or outside the domain; do not stretch known vegetation over it.

Use `cover_fraction.open_water` to retain partial water cells; majority class
alone can discard narrow features. Even the native 30 m product can miss narrow
channels or small structures. It cannot support surveyed building or channel
geometry. Do not infer exact flow direction or building footprints from it.
An absent desert tag also does not prove a humid climate.

## Quality and updates

This first release uses the available **LANDFIRE 2020** vegetation and terrain
editions. Vegetation metadata retains many circa-2016 ecosystem labels with
specified 2020 updates; terrain products were prepared in 2021 and published in
2022. These are static baseline landscapes, not a 2026 vegetation survey. Some
coastal-buffer terrain nodata was zero-filled upstream; nominal raster coverage
does not independently validate those zero heights or slopes. Original product
metadata is included unchanged.

Return `outside_conus` for an unsupported target and `no_landcover_data` when
cover is unavailable. Missing fractions/elevations are `null`, not zero. Inspect
coverage even when status is `ok`; partial sources must not silently become
grassland, dry land or flat terrain. Avoid random fallback landscapes presented
as real. National source-mask coverage and wholly uncovered cells are reported
in manifest.json and RELEASE_NOTES.md; coverage is not an accuracy score.

Weather, model fire activity and dated incidents are separate dynamic inputs.
They do not belong in this static geography file. A future source revision can
rebuild/version the index without changing the response contract; no daily
countrywide recomputation is needed. See RELEASE_NOTES.md for the source edition and validation record.
Keep the national index in a reusable backend process. Send only the selected
response, and its layout when needed, to the browser; do not download the whole
country archive to each phone or rerun a renderer for every cell.

## Public delivery v1.0.1

Published 31 October 2026. The national CSV, numeric atlas, example responses,
response schema and original source metadata are unchanged from v1. Server-local
paths were replaced with filenames or placeholders for portability. The public
checksums describe this package. No laboratory account is needed for the national
lookup. Source data and scripts are distributed at
https://github.com/LabRAI/fire-eye-landscape-context .
