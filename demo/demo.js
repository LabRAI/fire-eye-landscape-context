'use strict';
const map=new maplibregl.Map({container:'map',style:'https://tiles.openfreemap.org/styles/bright',center:[-98,38],zoom:3.4,maxZoom:20,antialias:true,attributionControl:true});
map.addControl(new maplibregl.NavigationControl(),'bottom-right');
map.on('load',()=>{const scene=FireEyeGeographicScene.mount(map,{catalogURL:'../scene/catalog.json'});window.mappedSceneDemo={map,scene};for(const button of document.querySelectorAll('[data-point]'))button.onclick=()=>{document.getElementById('message').hidden=true;scene.enter(button.dataset.point.split(',').map(Number));};map.on('click',e=>scene.onMapClick(e));});
map.on('error',()=>{if(!window.mappedSceneDemo)document.getElementById('message').textContent='The map source could not load. Reload to try again.';});
