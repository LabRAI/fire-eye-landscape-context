# Geographic object contract

Version 1 · draft for simulation-provider integration

Exchange GeoJSON in EPSG:4326, longitude first, latitude second. Preserve
Polygon/MultiPolygon holes, line topology and object IDs. Obtain a complete
object from the extract/bulk source before simulation; a rendered vector tile
may contain a clipped fragment.

Every feature carries kind, source, source_id, source_url, license, optional name,
class, optional address, source_edit_time and survey_date. Edit time and survey
time are different. The first extractor emits building, transportation,
pedestrian_area, land_area, woodland_area, water, tree and address features when
present. The feature_counts manifest states actual availability for each extract.

height_m and width_m are nullable source-tag values in metres. building_levels
is a separate attribute; multiplying it by an assumed storey height produces a
rendering estimate, not a measured height. Missing values remain null. Canopy
polygons never become invented tree stems. Road centerlines do not establish
pavement boundaries. A tree inventory's omission does not establish no trees.

For the animation engine, project the chosen anchor and feature vertices into a
local metre CRS (for example the appropriate UTM zone). Record that CRS and the
WGS84 anchor. Use local east/north/up coordinates; a Three.js renderer can map
them to x/y/z = east/up/-north. Ground elevation and height above ground remain
separate, with an explicit vertical datum and source date for terrain. A later
terrain adapter must supply actual elevations before terrain-following simulation
is claimed.

The current shared-map viewer is the geographic placement foundation. Fire
animation, event-conditioned spread, building damage, facade geometry and
physics calibration are not implemented by this contract. Detailed rendering
does not produce a building-level wildfire probability.
