const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod='projects/game-lighting-history-03/production',local='production/research/game-lighting-history/local/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const timelinePath=prod+'/measured-native-timeline-candidate-v15.json',timeline=read(timelinePath),out=prod+'/native-range-allocation-candidate-v16.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve native range candidate');
const short={l:'lumen-content-examples-2021',n:'nanite-editor-motion-2021',h:'hardware-rt-ue5-preview2-2022',g:'rtxgi-ue5-preview2-2022',d:'dlss-ue5-preview2-2022',a:'nvrtx-showcase-2021',r:'rtxdi-boulevard-2021',b:'battlefield-v-rtx-2018',c:'control-dlss2-2020',w:'wolfenstein-dlss2-2020',m:'deliver-moon-dlss2-2020',o:'dlss2-overview-2020',e:'escape-naraka-rtxgi-2021',u:'ue5-reveal-2020'};
const sources={};
for(const x of read(prod+'/native-board-review-v6.json').records)sources[x.slug]={media:x.media,sha256:x.sha256,url:x.url,crop:null,rightsApproved:false};
for(const [p,key,crop] of [['native-nanite-board-review-v7.json','n',[480,0,1440,810]],['native-rtxdi-board-review-v8.json','r',null],['native-lumen-board-review-v9.json','l',[0,20,1280,720]]]){const x=read(prod+'/'+p);sources[short[key]]={media:x.media,sha256:x.sha256,url:x.url,crop,rightsApproved:false};}
const html=fs.readFileSync(path.join(root,local+'native-motion-review-v5.html'),'utf8'),entries=JSON.parse(html.match(/const entries=(\[.*?\]),s=document/s)[1]);
for(const x of entries)if(!sources[x.id])sources[x.id]={media:local+x.src,sha256:x.sha256??null,url:x.url,crop:null,rightsApproved:false};
sources[short.u].sha256=read('projects/game-lighting-history-03/sources/game-candidates.json').candidates[0].nativeMediaSha256;
sources[short.a].crop=[160,0,960,540];
const allocations=[];
function allocate(id,parts,focus,limit){
 const slot=timeline.slots.find(x=>x.id===id&&x.role==='actual');if(!slot)throw Error('Unknown actual slot '+id);
 let remaining=slot.frames;
 const ranges=parts.map(([key,from,seconds,crop],i)=>{
  const frames=i===parts.length-1?remaining:Math.round(seconds*60);if(frames<=0||frames>remaining)throw Error('Invalid range length '+id);remaining-=frames;
  const source=short[key],fromFrame=Math.round(from*60),s=sources[source];if(!s||!fs.existsSync(path.join(root,s.media)))throw Error('Acquired source required '+source);
  return {source,media:s.media,sourceSha256:s.sha256,fromSeconds:fromFrame/60,toSeconds:(fromFrame+frames)/60,sourceFromOutputTimebaseFrame:fromFrame,sourceToOutputTimebaseFrame:fromFrame+frames,frames,
   crop:crop??s.crop,rate:1,sourceAudio:false,continuousMotionDirectlyReviewed:false,finalCaptionPixelsReviewed:false};
 });
 allocations.push({id,frames:slot.frames,scene:slot.scene,originalIndex:slot.originalIndex??null,afterOriginal:slot.afterOriginal??null,ranges,claim:slot.text,viewerFocus:focus,comparisonLimit:limit,
  sourceRangesProvisional:true,allActionsDirectlyReviewed:false,finalUseApproved:false});
}
const noCost='Qualitative observed engine/game output; no isolated internal-pass cost, ray count, latency or quantitative performance measurement.';
allocate('original-06',[['g',226]],'Wall color and nearby occlusion are different observations.',noCost);
allocate('01-mesh-distance-field',[['l',237.0666667]],'Per-mesh distance representation, narrow gaps, broad walls and material-view transitions. Exact checked MeshDistanceFields is independently recorded at270s.','Geometry representation only; not Nanite clusters or SurfaceCache lighting. Current v3 opener and joined whole/context directly compared; human pronunciation pending.');
allocate('02-global-distance-field',[['l',272]],'Selected GlobalDistanceField and coarse rock representation.',noCost);
allocate('original-09',[['h',113]],'Moving ray-traced sphere/shadow scene as transition to separately drawn acceleration structure.',noCost);
allocate('original-17',[['b',3,9],['b',18]],'2018 prerelease BattlefieldV RTX reflection trailer; retain prerelease date label.','Not evidence of all shipped patch behavior or full path tracing.');
allocate('original-21',[['a',39,9],['a',80]],'Separate effects in a hybrid renderer.',noCost);
allocate('03-ray-shadow',[['h',168,5],['h',176,6],['h',186,5],['h',200]],'Point-light edit beside blue box; direction and shadow edge.',noCost);
allocate('original-22',[['b',20.3666667]],'BattlefieldV trailer reflections and source conditions.','2018 prerelease capture; paper date, game release and DXR patch are separate.');
allocate('original-23',[['a',83]],'Attic reflective surfaces as camera moves; internal sampling remains explanation.',noCost);
allocate('original-28',[['a',49]],'Attic lighting/control changes; world surface and screen coordinate are distinct.','No one-sample-per-pixel or controlled accumulation measurement is asserted for this source.');
allocate('04-nvrtx-result',[['a',12,12],['a',25]],'Glass/metal, hanging lamps and distinct reflection/shadow/GI controls.',noCost);
allocate('original-30',[['c',3]],'DLSS2 current-game image reconstruction comparison.','Vendor capture conditions; no internal network structure or independently measured timing.');
allocate('original-31',[['o',58]],'Distinct robot-game reconstruction result from the official DLSS2 overview.','Exclude presenter/diagram; inspect exact58s transition and confirm all selected frames are actual game.');
allocate('05-dlss-helmet',[['m',3,15],['m',19]],'Helmet rim, gloves and wall line under displayed source quality mode.','Preserve original enlarged-view conditions; avoid equivalent repeated short footage from the overview.');
allocate('original-35',[['w',18]],'Thin edges during camera/aiming movement.','Vendor split comparison and original FPS are not this production benchmark.');
allocate('06-dlss-thin-lines',[['w',3,15],['w',39]],'Indoor light lines followed by aiming/branches.',noCost);
allocate('original-36',[['d',294]],'Actual engine viewport/menu operations, with architecture explanation scoped out.','Actual settings/camera operations294–305.3167 replace rejected278–285 hold; no network-internal claim.');
allocate('07-dlss-engine-modes',[['d',190,3.4166667],['d',216.3,0.75],['d',257.7,1.2],['d',259,11],['d',179]],'Show DLSS quality, DLAA and NIS separately; distinguish native AA and spatial scaling.','Source settings are not identical temporal inputs; align exact selected menu labels with guide word cues.');
allocate('original-37',[['e',12,5.8],['g',178,5],['g',310]],'Actual Naraka RTXGI lighting appearance then engine volume/light edit.','Naraka primary confirms DDGI; neither capture isolates ray counts or cache-update latency.');
allocate('08-ddgi-light-change',[['g',115,6],['g',161]],'Sunlight motion; None→Plugin at166.5, colored walls return.',noCost);
allocate('original-38',[['g',315,7],['g',330,2],['g',335]],'Space-fixed probes and camera movement.',noCost);
allocate('09-ddgi-volume',[['g',205,14.3333333],['g',258]],'Move/resize volume, then show spatial probe points.','Enlarging a box is not proof of fixed occlusion or detail.');
allocate('original-41',[['g',236.85,8.15],['g',338.2666667]],'Spatial sampling and camera/view differences.','No controlled spacing/update latency benchmark.');
allocate('10-ddgi-spacing',[['g',279,14],['g',294]],'Probe spheres, grid density and corresponding wall color.','Probe spheres are debug representation rather than inserted physical lights.');
allocate('original-42',[['g',402,6],['e',27]],'Probe visualization/light change and active Naraka scene.','Qualitative light/geometry changes; no measured instant convergence.');
allocate('11-ddgi-city',[['g',363]],'City probes and original grid count label.','Grid count belongs to this source configuration; retain enough readable label context.');
allocate('original-43',[['r',3]],'Many-light moving boulevard result.','2021 RTXDI result illustrates the separately dated2020 ReSTIR paper; reservoir operations are not visible.');
allocate('12-rtxdi-boulevard',[['r',18.8833333]],'Moving car body, windows/signs and nearby surfaces.',noCost);
allocate('original-49',[['r',45]],'Lighting selection result; reuse and filtering are explained separately.',noCost);
allocate('original-50',[['n',296,12],['n',311]],'Camera movement changes visible foreground/background surfaces.',noCost);
allocate('original-51',[['n',386]],'Foreground detail hides neighboring architecture.',noCost);
allocate('13-nanite-occlusion',[['n',528]],'Statues obscure the facade during camera movement.',noCost);
allocate('original-55',[['n',318]],'Cave viewport visibility; internal depth pyramid and BVH remain distinct explanations.',noCost);
allocate('14-nanite-cave-visibility',[['n',330,7],['n',340,6],['n',350]],'Cave rocks, emerging exit and changing facade size/occlusion.',noCost);
allocate('original-61',[['n',410,9],['n',422]],'Bicycle/floor geometry as separate from texture and shading.',noCost);
allocate('15-nanite-ornament-surface',[['n',432,11],['n',398.6833333,4.3166667],['n',548.7333333]],'Ornament ridges/occlusion then bright wide exterior.',noCost);
allocate('original-62',[['n',674]],'2021 engine detail demonstration connected to2020 Nanite announcement.','Do not present the2021 source as the original2020 reveal or infer unlimited cost-free triangles.');
allocate('original-63',[['n',635]],'Triangle debug representation of bicycle geometry.','Internal hierarchy construction remains separately drawn.');
allocate('16-nanite-debug-modes',[['n',646.3,3.7],['n',110,3],['n',163,14],['n',651]],'Triangles first, clusters second, material view last.','Preserve mode labels and source counters; align exact mode changes to current guide narration.');
allocate('original-64',[['n',659.35]],'Close detail and projected screen size.',noCost);
allocate('17-nanite-distance',[['n',670.6,3.0333333],['n',695,13],['n',720]],'Face closeup then distant whole facade.','Camera changes several conditions; independent doubled-distance calculation remains separately explained.');
allocate('original-67',[['n',727]],'Aerial camera movement and changing visibility; streaming remains separately documented.',noCost);
allocate('18-nanite-bicycle',[['n',596,5],['n',605,19],['n',630]],'Bicycle tubing, spokes and floor in moving closeups.',noCost);
allocate('original-68',[['n',738.95]],'Wide geometry scene; distinguish geometry selection from lighting.',noCost);
allocate('original-69',[['l',299,6],['l',309,6],['l',181]],'LumenScene camera views then moving rock geometry.','Do not label LumenScene as SurfaceCache debug or infer cache cost.');
allocate('original-70',[['l',336,9.0333333],['l',346]],'Camera moves through a rock opening and reveals new surfaces.','Illustrates information changes; screen-trace internal paths are explained independently.');
allocate('original-71',[['l',288,4],['h',173,2],['h',307,2],['h',312,6],['h',322]],'Different dated engine modes/qualitative output, with explicit version labels.','No claim that these captures use identical software/hardware paths or benchmark conditions.');
allocate('original-74',[['u',165]],'2020 reveal explicit LumenOFF/ON cave labels.','Camera/light not locked; qualitative toggle rather than radiance/update-cost measurement.');
allocate('original-75',[['l',357]],'Selected actual engine lighting/geometry view.','Native capture does not expose internal Nanite SurfaceCache capture cost.');
allocate('original-76',[['l',490,8],['l',460]],'Light-color edits and changed surrounding surfaces.','Do not measure update latency from these cuts; camera also changes.');
allocate('19-lumen-light-edit',[['l',350,6,[640,20,1280,720]],['l',388,14],['l',402]],'First DirectionalLight selection/settings, then separate lit and shaded regions.',noCost);
allocate('original-77',[['l',498,12],['l',514]],'Camera movement reveals surfaces in changing light.','Not proof of exact temporal response or ghosting.');
allocate('original-79',[['l',514.85,7.15],['l',673,4],['l',609]],'Small gaps and varying visible rock surfaces.',noCost);
allocate('original-80',[['l',404,4.8666667],['l',478]],'Separate light-feature menu change from camera-only interval.',noCost);
allocate('20-lumen-interior-toggle',[['l',658,12.9],['l',670.9,1.8333333],['l',684,13.8],['l',710]],'Bright window/sofa wall/ceiling, observed dark/bright transition and later camera movement; hidden exact GI menu label is not asserted.','Not exposure-locked measurement. Current seven-sentence34.4000417s voice whole/context and separate sentences directly compared; no silent hold substitution.');
allocate('original-81-action',[['l',715.9]],'Interior camera movement before the complete tracing/storage/update diagram returns.','No claim of exhaustive per-frame path tracing or measured lighting latency.');
allocate('original-83',[['n',749.5833333,5.4166667],['l',681,3],['l',184.0666667,2.9333333],['l',190]],'Geometry selection then lighting/rock edit, keeping roles distinct.',noCost);
allocate('original-84',[['d',306]],'Actual engine input/output work as next-episode preview.','Label this2022 engine sample as earlier reconstruction context; never relabel it DLSS5 or frame generation.');
const expected=timeline.slots.filter(x=>x.role==='actual');if(allocations.length!==expected.length||allocations.reduce((n,x)=>n+x.frames,0)!==timeline.totals.actualFrames)throw Error('All current actual slots and measured frames required');
const flattened=allocations.flatMap(x=>x.ranges.map(r=>({...r,id:x.id}))),overlaps=[];
for(let i=0;i<flattened.length;i++)for(let j=i+1;j<flattened.length;j++){const a=flattened[i],b=flattened[j];if(a.source===b.source&&Math.min(a.sourceToOutputTimebaseFrame,b.sourceToOutputTimebaseFrame)>Math.max(a.sourceFromOutputTimebaseFrame,b.sourceFromOutputTimebaseFrame))overlaps.push({a:a.id,b:b.id,source:a.source});}
if(overlaps.length)throw Error('Overlapping source candidate '+JSON.stringify(overlaps));
const record={schemaVersion:1,preparedAt:new Date().toISOString(),status:'provisional-measured-source-allocation-not-adopted',timeline:{path:timelinePath,sha256:sha(timelinePath)},sources,allocations,
 actualFrames:timeline.totals.actualFrames,actualSlots:expected.length,nativeCuts:flattened.length,sourceOverlapCount:0,loops:0,rateChanges:0,sourceAudio:false,newMedia:0,newImages:0,
 exactSourceFrameRateConversionStillPending:true,longHoldAndModeBoundaryReviewRequired:true,nativeContinuousActionsApproved:false,allFinalCaptionPixelsReviewed:false,finalUseApproved:false,
 sourceStartOffsetsVerified:false,rightsApproved:false,humanListening:'pending',humanPronunciation:'pending'};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({out,actualSlots:expected.length,nativeCuts:flattened.length,actualFrames:timeline.totals.actualFrames,sourceOverlapCount:0,adopted:false}));
