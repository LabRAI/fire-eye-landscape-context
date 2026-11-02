/* Bounded, offline preparation; never run this for every map visitor. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import osmtogeojson from 'osmtogeojson';

const args={};
for(let n=2;n<process.argv.length;n+=2){if(!process.argv[n]?.startsWith('--')||process.argv[n+1]===undefined)throw Error('Use --bbox west,south,east,north --out folder [--input saved-api-response.json]');args[process.argv[n].slice(2)]=process.argv[n+1];}
const bbox=args.bbox?.split(',').map(Number);
if(!bbox||bbox.length!==4||!bbox.every(Number.isFinite)||bbox[0]>=bbox[2]||bbox[1]>=bbox[3]||bbox[0]<-125||bbox[2]>-66||bbox[1]<24||bbox[3]>50)throw Error('A valid CONUS bounding box is required');
if((bbox[2]-bbox[0])*(bbox[3]-bbox[1])>.0002)throw Error('Research extracts must stay below 0.0002 square degrees; use a scheduled bulk-data pipeline for larger areas');
if(!args.out)throw Error('--out is required');
const retrievedAt=args.input?args['retrieved-at']:new Date().toISOString();
if(!retrievedAt||!Number.isFinite(Date.parse(retrievedAt)))throw Error('Saved inputs require --retrieved-at with their original download timestamp');
const url='https://api.openstreetmap.org/api/0.6/map.json?bbox='+bbox.join(',');
let raw;
if(args.input)raw=await fs.readFile(args.input);
else{const r=await fetch(url,{headers:{'User-Agent':'Fire-eye-Landscape-Research/1.1 (+https://github.com/LabRAI/fire-eye-landscape-context)'},signal:AbortSignal.timeout(30000)});if(!r.ok)throw Error('Source API returned HTTP '+r.status);raw=Buffer.from(await r.arrayBuffer());}
if(raw.length>16*1024*1024)throw Error('Extract exceeds the bounded payload budget');
const source=JSON.parse(raw);if(!Array.isArray(source.elements)||source.elements.length>50000)throw Error('Unsupported source payload');
const converted=osmtogeojson(source,{flatProperties:false});
const measure=v=>{if(typeof v!=='string'&&typeof v!=='number')return null;const m=String(v).trim().match(/^([0-9]+(?:\.[0-9]+)?)\s*(m|metres?|meters?|ft|feet)?$/i);if(!m)return null;const n=Number(m[1])*(/^(ft|feet)$/i.test(m[2]||'')?.3048:1);return Number.isFinite(n)&&n<=1000?n:null;};
const classify=(t,g)=>{
 if(t.building||t['building:part'])return ['Polygon','MultiPolygon'].includes(g)?'building':null;
 if(t.natural==='tree')return g==='Point'?'tree':null;
 if(t.highway==='pedestrian'&&['Polygon','MultiPolygon'].includes(g))return 'pedestrian_area';
 if(t.highway)return g.includes('LineString')?'transportation':null;
 if(t.natural==='water'||t.water||t.waterway)return 'water';
 if(t.natural==='wood'||t.landuse==='forest')return 'woodland_area';
 if(t.leisure||t.landuse||['grassland','scrub','heath'].includes(t.natural))return ['Polygon','MultiPolygon'].includes(g)?'land_area':null;
 if(t['addr:housenumber']&&g==='Point')return 'address';
 return null;
};
let incomplete=0;const features=[];
for(const feature of converted.features){
 const p=feature.properties||{},tags=p.tags||{},kind=classify(tags,feature.geometry?.type||'');if(!kind)continue;
 if(p.tainted){incomplete++;continue;}
 const sourceId=p.type+'/'+p.id,height=measure(tags.height),levels=Number(tags['building:levels']);
 features.push({type:'Feature',id:sourceId,geometry:feature.geometry,properties:{kind,source:'OpenStreetMap',source_id:sourceId,source_url:'https://www.openstreetmap.org/'+sourceId,license:'ODbL-1.0',name:tags.name||null,class:tags.highway||tags.building||tags.landuse||tags.leisure||tags.natural||null,height_m:height,height_status:height===null?'not_mapped':'source_tag_not_independently_verified',building_levels:Number.isFinite(levels)&&levels>0?levels:null,width_m:measure(tags.width),below_ground:(tags.tunnel&&tags.tunnel!=='no')||tags.location==='underground'||Number(tags.layer)<0?true:false,indoor:!!tags.indoor&&tags.indoor!=='no',layer:Number.isFinite(Number(tags.layer))?Number(tags.layer):null,bridge:!!tags.bridge&&tags.bridge!=='no',address:tags['addr:housenumber']?[tags['addr:housenumber'],tags['addr:street']].filter(Boolean).join(' '):null,source_edit_time:p.meta?.timestamp||null,survey_date:null}});
}
const content={type:'FeatureCollection',features};
const data=Buffer.from(JSON.stringify(content));
const counts={};for(const f of features)counts[f.properties.kind]=(counts[f.properties.kind]||0)+1;
const metadata={schema_version:1,kind:'geographic-scene-extract',bbox_wgs84:bbox,source_url:url,retrieved_at_utc:new Date(retrievedAt).toISOString(),prepared_at_utc:new Date().toISOString(),source:'OpenStreetMap contributors',license:'ODbL-1.0',attribution_url:'https://www.openstreetmap.org/copyright',source_payload_sha256:crypto.createHash('sha256').update(raw).digest('hex'),source_elements:source.elements.length,feature_counts:counts,omitted_incomplete_features:incomplete,geometry_units:'longitude_latitude_degrees',horizontal_crs:'EPSG:4326',height_units:'metres_above_local_ground_when_tagged',survey_date:null,limits:['Research bbox snapshot, not a complete national inventory.','Missing trees or buildings do not establish absence.','Road lines are centerlines, not surveyed widths.','Building/tree heights are source tags, not independently surveyed by this project.','Source edit timestamps are not survey dates.','No procedural objects are added.'],asset:{path:'features.geojson',bytes:data.length,sha256:crypto.createHash('sha256').update(data).digest('hex')}};
await fs.mkdir(args.out,{recursive:true});
await fs.writeFile(path.join(args.out,'features.geojson'),data);
await fs.writeFile(path.join(args.out,'manifest.json'),JSON.stringify(metadata,null,2)+'\n');
console.log(JSON.stringify({feature_counts:counts,omitted_incomplete_features:incomplete,asset:metadata.asset}));
