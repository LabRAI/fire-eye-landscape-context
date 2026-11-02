# Simulation in the geographic map

2 November 2026

Zooming into a prepared scene now brings Qiyuan's original tree models and an
illustrative fire/smoke effect into the **existing map canvas**. The user keeps
the same location, buildings, streets and camera. There is no Simulation launch
step, embedded page or modal transition. The region popup's existing Simulation
shortcut simply zooms into that location.

## Transition and placement

- Geographic streets and buildings appear at neighborhood scale. Tree points
  become simple 3D symbols at zoom 16–17.
- The original tree meshes fade in from zoom 17.0 to 17.8, replacing those symbols
  at the same recorded tree coordinates. Meshes prefetch at zoom 15.5.
- An illustrative ignition is anchored to a recorded tree or mapped greenspace,
  outside known building/water footprints. Panning does not relocate it.
- Point-of-interest icons fade out near the simulation scale; street and area
  names remain available.
- Pause and Scenario fire controls are optional. Zooming out stops the animation
  and restores the ordinary geographic view. Reduced-motion preferences pause
  animation initially; background tabs do not animate.

Bryant Park's extract contains 565 tree points. The FSU extract contains none,
so it does not receive invented trees. Outside the two prepared extracts, normal
mapped buildings and streets remain available; an inventory is needed before
claiming local tree coverage.

## Reused assets and renderer

Original oak models come from llll0630/wildfire-simulation, pinned at revision
eed7ae1e7b9109d1b9d13ea0f172e14900551fc3. The two meshes preserve every source
vertex position, normal, color and triangle index. Their combined binary size is
136,500 bytes, excluding the small manifest. Source and packaged SHA-256 hashes
are recorded in scene/simulation-assets/manifest.json.

mapped-simulation.js uses an instanced WebGL 1 MapLibre custom 3D layer. This
matches the existing map context without upgrading the map or adding another
renderer canvas. Fire/smoke shaders adapt the existing Fire-eye viewer. They are
visual effects, not a port of the complete scene rules or a fire-spread solver.
The independent preview retains its old representative renderer internally;
ordinary zoom and the Simulation shortcut no longer open that viewer.

## Accuracy and limitations

Buildings and streets retain mapped geometry. Tree species, crown shape and
unrecorded dimensions are display choices: missing tree height uses 8 m, with a
4.8 m crown diameter. Original unknown source attributes stay null. Trees are
placed only at source points; the models do not establish surveyed species or
biomass. Ground is flat; actual terrain/vertical-datum integration remains work
for the simulation provider.

The sample ignition is visibly labeled **Illustrative fire scenario · not a
reported fire**. It is not driven by a detected incident, predicted ignition,
weather or the current forecast value. It must not be used as evidence of a
real fire, damage or validated propagation. The national forecast is unchanged.

## Delivery and resilience

The demo and HF/GitHub preview serve this layer as static assets. Visitors do not
call a laboratory server. Hash/size validation rejects damaged mesh files;
optional asset/shader failures restore normal tree symbols and offer Retry
detail without removing the map. Disposal deletes only this layer's resources,
never the shared WebGL context.

The downloadable v1.1.1 archive remains the frozen geographic-data handoff.
This newer integration is in the repository and online demo. The national atlas
is unchanged. Existing upstream attribution is preserved; the pinned upstream
revision has no license file, and this adapter does not grant a new license.
