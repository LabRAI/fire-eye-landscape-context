# Release notes — CONUS landscape context v1

Prepared 2026-10-26 for the Fire Eye simulation provider.

- 901,703 source-CONUS-intersecting 3 km cells.
- 901,487 cells contain mapped land cover; 216 have none.
- 8,977,864,155 original 30 m pixel centres fall inside the supplied extent.
- Nominal mapped-cover coverage: 99.97618%; this is not accuracy.
- National numeric archive: 19.86 MB; no GPU, forecast model or LLM required.
- 12 local scene examples, 35 schema-checked responses,
  and 24 exact native-window rechecks.
- The final extent uses LANDFIRE's unbuffered geographic-area polygons, preserving
  Florida Keys and other coastal locations excluded by the old simplified model outline.

The simulation and live website have not been changed by this data handoff.
This is a static source-edition landscape package, not fire propagation or current conditions.

## Public delivery v1.0.1 — 31 October 2026

- Publishes the existing v1 geography and examples for anonymous download.
- Replaces build-host paths in source provenance and local-reader defaults with portable names/placeholders.
- Updates delivery instructions and file checksums. No numeric data, scientific method, source metadata or response schema is changed.
- New native local patches still require the original rasters; the included national index is self-contained.
