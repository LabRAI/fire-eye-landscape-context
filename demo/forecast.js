'use strict';
(async()=>{
 const base='https://huggingface.co/datasets/yx21e/fire-eye-forecasts-preview/resolve/main/';
 const note=document.getElementById('demo-forecast-status');
 for(let i=0;i<600&&!window.mappedSceneDemo;i++)await new Promise(r=>setTimeout(r,100));if(!window.mappedSceneDemo)return;
 const map=mappedSceneDemo.map,S={map,ready:false,active:null,manifest:null,riskVisible:true,riskOpacity:1,refinementMix:0},P={ready:false,manifest:null};window.fireEyePreview=S;window.fireEyePlatform=P;
 function approved(value){const u=new URL(value,location.href);if(u.protocol!=='https:'||u.hostname!=='huggingface.co'||!/^\/datasets\/[^/]+\/[^/]+\/resolve\/[a-f0-9]{40}\//.test(u.pathname))throw Error('Unapproved forecast data');return u.href;}
 const json=async url=>{const r=await fetch(url,{credentials:'omit',cache:'no-store',signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error('Forecast unavailable');return r.json();};
 P.loadAsset=async key=>{const a=P.manifest.assets[key];if(!a||a.bytes>4*1024*1024||!/^[a-f0-9]{64}$/.test(a.sha256))throw Error();const r=await fetch(approved(a.url),{credentials:'omit',signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error();const b=new Uint8Array(await r.arrayBuffer());if(b.length!==a.bytes||Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('')!==a.sha256)throw Error();return JSON.parse(new TextDecoder().decode(a.encoding==='gzip'?fflate.gunzipSync(b):b));};
 S.syncHeatmapDisplay=()=>{if(S.active&&map.getLayer(S.active.id))map.setPaintProperty(S.active.id,'raster-opacity',S.riskOpacity*(1-S.refinementMix));};
 async function refresh(){try{
  const [m,p]=await Promise.all([json(base+'latest.json'),json(base+'platform.json')]);const run=m.runs?.find(r=>r.lead_hours===12);if(!run?.overview||Date.parse(run.target_time_utc)-Date.parse(m.issue_time_utc)!==12*3600000)throw Error();
  P.manifest=p;P.ready=true;if(S.active?.run.source_id===run.source_id)return;
  const id='demo-forecast-'+run.source_id,url=approved(new URL(run.overview.image.path,m.asset_base).href),anchor=map.getStyle().layers.find(l=>l.type==='symbol')?.id;
  map.addSource(id,{type:'image',url,coordinates:run.overview.coordinates});map.addLayer({id,type:'raster',source:id,paint:{'raster-opacity':.001,'raster-resampling':'nearest','raster-fade-duration':0}},anchor);
  await new Promise((resolve,reject)=>{let timer;const check=()=>{if(map.isSourceLoaded(id)){clearTimeout(timer);map.off('sourcedata',check);resolve();}};timer=setTimeout(()=>{map.off('sourcedata',check);reject(Error());},18000);map.on('sourcedata',check);check();});
  if(S.active){map.removeLayer(S.active.id);map.removeSource(S.active.id);}S.manifest=m;S.active={id,run,kind:'overview'};S.refinementMix=0;S.ready=true;S.syncHeatmapDisplay();
  note.textContent='Fire risk +12h · Window ending '+new Date(run.target_time_utc).toLocaleString('en-US',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit',timeZone:'UTC'})+' UTC';
  window.dispatchEvent(new Event('fire-eye:forecast-changed'));
 }catch{note.textContent=S.active?'Published forecast retained':'Forecast overlay pending · Geographic scene available';}}
 await refresh();setInterval(()=>{if(!document.hidden)refresh();},300000);
})();
