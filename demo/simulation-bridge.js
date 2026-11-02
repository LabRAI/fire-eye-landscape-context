/* Reuse Fire-eye's existing scene renderer; do not duplicate its model rules. */
(function(global){
 'use strict';
 function mount(options={}){
  const base=new URL(options.baseURL||'https://labrai.github.io/fire-eye-preview/');
  if(base.protocol!=='https:'&&!(base.protocol==='http:'&&['localhost','127.0.0.1'].includes(base.hostname)))throw Error('Unsupported simulation origin');
  const make=(tag,text)=>{const e=document.createElement(tag);if(text)e.textContent=text;return e;};
  const dialog=make('dialog'),header=make('div'),title=make('strong','Regional simulation'),closeButton=make('button','×'),status=make('p'),retry=make('button','Retry'),body=make('div');
  dialog.className='simulation-bridge';dialog.setAttribute('aria-label','Regional simulation');header.className='simulation-bridge-heading';closeButton.type='button';closeButton.setAttribute('aria-label','Close simulation');retry.type='button';retry.hidden=true;status.setAttribute('role','status');body.className='simulation-bridge-frame';header.append(title,closeButton);dialog.append(header,status,retry,body);document.body.append(dialog);
  let frame=null,session=null,point=null,timer=null;
  function clear(){clearTimeout(timer);session=null;frame?.remove();frame=null;body.replaceChildren();}
  function close(){clear();if(dialog.open)dialog.close();}
  function failed(){clearTimeout(timer);status.hidden=false;status.textContent='Simulation is taking longer to load. Retry or return to the map.';retry.hidden=false;}
  function load(){
   clear();session=crypto.randomUUID();const url=new URL(base);url.searchParams.set('simulation','1');url.searchParams.set('simulation_embed','1');url.searchParams.set('lng',String(point[0]));url.searchParams.set('lat',String(point[1]));url.searchParams.set('scene_session',session);url.searchParams.set('parent_origin',location.origin);
   status.hidden=false;status.textContent='Preparing the simulation for '+point[1].toFixed(4)+'°, '+point[0].toFixed(4)+'°…';retry.hidden=true;
   frame=make('iframe');frame.title='Fire-eye regional simulation';frame.setAttribute('sandbox','allow-scripts allow-same-origin allow-downloads');frame.referrerPolicy='no-referrer';frame.src=url.href;frame.addEventListener('error',failed);body.append(frame);timer=setTimeout(failed,60000);
  }
  function message(event){
   const m=event.data;if(!dialog.open||!frame||event.source!==frame.contentWindow||event.origin!==base.origin||m?.channel!=='fire-eye-simulation'||m.session!==session)return;
   if(m.type==='ready'){clearTimeout(timer);status.hidden=true;retry.hidden=true;}
   else if(m.type==='error')failed();
   else if(m.type==='return-map'||m.type==='closed')close();
  }
  closeButton.onclick=close;retry.onclick=load;dialog.addEventListener('cancel',e=>{e.preventDefault();close();});dialog.addEventListener('close',()=>{if(!dialog.open)clear();});addEventListener('message',message);
  return {open(selection){const p=selection?.lnglat;if(!Array.isArray(p)||p.length!==2||!p.every(Number.isFinite)||Math.abs(p[0])>180||Math.abs(p[1])>90)return false;point=[...p];if(!dialog.open)dialog.showModal();load();return true;},close,dispose(){close();removeEventListener('message',message);dialog.remove();}};
 }
 global.FireEyeSimulationBridge={mount};
})(window);
