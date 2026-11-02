# Automatic fire-risk detail

2 November 2026

The geographic demo and independent Fire-eye map now follow the same scale
sequence: national forecast → 50 m spatial refinement → local 3D scene.
Zooming is the control; there is no separate higher-resolution button.

## Data and dates

The base forecast remains FireWx-FM's native 5 km active-fire occupancy index.
The 50 m layer uses the existing learned terrain/fuel-conditioned refinement
weights. It is experimental spatial redistribution, not a newly trained native
50 m forecast, an ignition probability or a building-level forecast.

For archived windows with a published refined field, the viewer verifies the
source ID, issue time, valid time and native-grid checksum before using it.
For other available forecast windows, it reads that window's exact float32 native
grid and applies the same existing refinement equation to visible cells. A scalar
bias is solved against the fine-input histogram so each native cell retains its
original mean. Missing fine-input pixels retain the native value. Values of zero
and one, and native missing-data cells, remain unchanged.

This makes new forecast windows usable without relabeling an old October field
or requesting a new CONUS-wide computation. It does not advance the published
refinement archive or represent browser-generated detail as a previously archived
50 m prediction. Historical refinement remains retrospective.

## Delivery and interaction

- No fine-data downloads at national zoom. Detail begins loading at zoom 10 and
  blends into view over zoom 10–11.
- Only required immutable HF weight ranges are read, checked against hashes and
  cached within bounded worker budgets. A visitor does not call a lab server.
- Forecast issue/lead changes invalidate the old layer. The native map remains
  visible while the new matching detail is prepared or if a dependency fails.
- Active-fire observations remain a separate overlay above the same risk map.
- Regional charts and numerical summaries continue using native 5 km data.
- At street scale, the same risk layer remains on the ground beneath buildings
  and the local scene. No second map or camera is created.

The demo's header shows its latest +12h forecast window. The complete preview
retains its normal timeline and archive controls. The original separate
resolution-lab URL remains available for old links, but is no longer required.

## Fire visualization

The local scenario now uses more visible orange flame particles, a taller flame
plume, and lighter smoke beginning above the flame base. A failed placement can
be reconsidered after the camera moves. The ignition stays geographically fixed
once placed. These effects are labeled **Illustrative fire scenario** and are
not generated from the risk value or a reported incident. A green/low-risk cell
can still contain the explicitly illustrative demonstration.

The geographic object inventories are still limited to the prepared FSU and
Bryant Park extracts. The forecast/refinement layer covers available CONUS model
cells; this does not imply a national individual-tree inventory or physical
fire-spread simulation.
