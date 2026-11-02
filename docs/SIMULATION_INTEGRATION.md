# Existing simulation integration

2 November 2026

The online digital-scene demo now provides a **Simulation** action. It opens
the existing Fire-eye simulation renderer for the current map location or the
selected mapped object. The demo supplies coordinates; Fire-eye supplies its
latest published forecast and archived landscape inputs. Closing the simulation
returns to the same map position.

Within the independent Fire-eye platform, the region popup's **Simulation**
button opens the renderer directly and preserves the selected forecast issue
and lead time. **Map location** returns to the geographic scene. The geographic
scene's own Simulation button uses the clicked object or current map center,
so a previous region selection cannot silently provide the wrong coordinates.

## Reused implementation

- Original scene assets and visualization rules from
  https://github.com/llll0630/wildfire-simulation at pinned revision
  eed7ae1e7b9109d1b9d13ea0f172e14900551fc3.
- Fire-eye's existing Three.js viewer: orbit/walk navigation, vegetation and
  structures, fire/smoke effects, pause and alternative realizations.
- Published location inputs: modeled fire activity, fuel, canopy, housing
  density and available satellite fire-radiative-power context. Source dates
  and display fallbacks remain available in the scene.

This is a representative 200 × 200 m scene with procedurally placed objects and
flat ground. Its fire effects are visualization rules, not validated fire spread.
The real building/tree geometries in the geographic viewer are **not yet** fed
into the animation engine. The next adapter must supply those geometries and
actual terrain while preserving source uncertainty.

## Delivery and isolation

The demo lazily opens the existing static Fire-eye preview in an embedded view;
it does not copy the scene rules into a second implementation. Coordinates are
explicit. Ready/close messages check origin, source window and session ID.
Closing removes the frame and its graphics resources. A failed scene can be
closed or retried without changing the geographic map. No laboratory-server
endpoint is required for the independent preview.

The online integration requires network access to the preview and its published
assets. The v1.1.1 downloadable handoff remains the earlier frozen geographic
data/renderer release; the new integration is in the current repository and
online demo. The national offline atlas is unchanged.

Existing upstream attribution is preserved. The pinned upstream revision did
not include an open-source license file; this integration does not invent or
grant a new license for those assets. The public handoff adds only the bridge
and documentation; animation assets remain in their existing Fire-eye delivery.
