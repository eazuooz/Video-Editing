// Exact local candidate ranges; preparation does not approve production or rights.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const d='production/research/game-lighting-history/local/';
const sources={
  vsmInitial:{path:d+'episode04-additional-action-v47/vsm-initial-editor-goldcoast2024.mp4',sha256:'d6b2cc2f1a45490b08f1c7834a4bfb20fc19f1be30a62e5b0ee09d834b6ba210',crop:[60,114,1520,854]},
  vsmPool:{path:d+'episode04-native-v1/virtual-shadow-editor-2024.mp4',sha256:'b6dbe8fe584e3b9401b98b7d50bdbd35dc38a611a6aedddee7341c7069bb8d32',crop:[60,114,1520,854]},
  tsrMan:{path:d+'episode04-tsr-browser-v3/mannequin-low-resolution.mp4',sha256:'6eb1d0f1f506c9ef8902f62e69bcc1e3bdaeeec9006fc5520fd2013dd020b53f',crop:[282,126,1170,658]},
  tsrFan:{path:d+'episode04-tsr-browser-v3/fan-motion-vectors.mp4',sha256:'fb21a81c1bcdcc337c39c1756622a07c8ffed1c5c783736b575f7d4d378b92a8',crop:[61,113,1518,854]},
  vt:{path:d+'episode04-additional-action-v47/virtual-texture-editor-goldcoast2024.mp4',sha256:'54510f8e0874f5ddc72691a90510845cef9e2ea58cd8b2677cd2273c188c8610',crop:[60,114,1520,854]},
  nanite:{path:d+'episode04-additional-action-v44/nanite-editor-goldcoast2024.mp4',sha256:'3bb534826f61456336ad807df6aada69e51fa798cb3a9be703e90d1c92ff4d9e',crop:[60,114,1520,854]},
  mobile:{path:d+'episode04-additional-action-v44/mobile-profile-shader-editor2024.mp4',sha256:'507fa8459952670bbb0b298f4b251b5acd6877e32f877f412d50a51b58cec80e',crop:null},
  rivalry:{path:d+'episode04-native-v1/rivalry-mobile-2014.mp4',sha256:'7668158e1bda2defb6c180d75b1ce2ce5c45147a2ad877888200052e897e0d1f',crop:null},
  horizon:{path:d+'cross-game-comparisons-v51/horizon-forbidden-west-sr.mp4',sha256:'e010785fe2b1c18736870f5331bf15c47c5554b7ca34f7f7a2d94e67294c1d97',crop:null},
  outer:{path:d+'episode04-native-v1/outer-worlds-2-dlss45.mp4',sha256:'4d6c017d7091e8b0e84e8afb1efcbad900ffb824420a1ae33ff1a0099c74adec',crop:null},
  cyber:{path:d+'episode04-native-v1/cyberpunk-ray-reconstruction.mp4',sha256:'25a4f9f3d7c2cd335df4128687582e444b61c7d119b2af5493b80003b49ac2da',crop:null},
};
for(const [k,s] of Object.entries(sources))if(hash(s.path)!==s.sha256)throw Error('Changed candidate '+k);
const rows=[];
function add(id,source,a,b,focus){rows.push({id,source,path:sources[source].path,sha256:sources[source].sha256,crop:sources[source].crop,ranges:[[a,b]],focus,selected:false,wholeMotionReviewed:false,finalPixelsApproved:false});}
add('shadow-virtual-page','vsmInitial',12,29,'Menu changes to virtual page colors. Dense review must exclude the title transition.');
add('shadow-moving-wheel','vsmInitial',112,181,'Moving wheel/shadow plus camera retreat and return. Describe visibility and invalidation conditions, no measured cost.');
add('shadow-pool-edit','vsmPool',98,198,'Actual physical page pool changes and moving camera. Exclude static lecture cards and unavailable-memory inference.');
add('tsr-moving-silhouette','tsrMan',0,39,'Mannequin running/turning along wall; motion and low-resolution source conditions.');
add('tsr-rotating-vectors','tsrFan',0,34,'Normal fan, grid, absent/present rotation vectors, normal fan. Do not infer latency.');
add('texture-streaming-toggle','vt',0,35,'Virtual streaming texture property and virtual sampler.');
add('texture-stack-uv','vt',96,120,'Duplicate/reconnect UV path, stack count changes.');
add('texture-convert-dependencies','vt',192,225,'Asset conversion and dependency dialog, exclude idle/loading.');
add('texture-project-settings','vt',246,266,'Project virtual-texture settings search.');
add('texture-runtime-size','vt',514,564,'Runtime virtual-texture asset size change, distinct from VSM physical pages.');
add('texture-streaming-statistics','vt',648,682,'Console and statistics, no independent performance measurement.');
add('texture-pool-auto-grow','vt',730,792,'Pool/AutoGrow settings; trim unchanged holds.');
add('texture-resource-lists','vt',862,906,'Resource viewer selects Lumen/VSM/VT names; distinct stored information.');
add('texture-upload-budget','vt',906,950,'Texture uploads-per-frame console control; not frame generation.');
add('texture-courtyard-selection','vt',1047,1069,'Camera and building selection, relate resource cost to visible content.');
add('geometry-road-mask','nanite',24,42,'Road spline/mask edit; real editor process.');
add('geometry-barrier-debug','nanite',96,136,'Barrier camera, wireframe/triangle debug and shaded view.');
add('geometry-courtyard-mask','nanite',180,217,'Courtyard mask/shaded people. Different visualization from shadow colors.');
add('geometry-programmable-debug','nanite',306,350,'NoDerivativeOps/PixelProgrammable menu and colored materials. Do not claim visibility-buffer adoption from colors.');
add('geometry-material-car','nanite',372,389,'Silver/rust car material changes. Distinguish geometry identity from final material evaluation.');
add('mobile-texture-group','mobile',0,16,'Texture group dropdown, not a measured bandwidth result.');
add('mobile-device-profile','mobile',30,50,'Android device profile editor.');
add('mobile-lod-cvars','mobile',66,116,'Texture LOD groups and CVar scrolling.');
add('mobile-compiler-warning','mobile',132,150,'Platform shader statistics with missing offline compiler warning.');
add('fortnite-mobile-profiling','mobile',234,260,'Fortnite31.00 developer profiling viewport, surface changes and graph; four-game candidate.');
add('rivalry-mobile-lighting','rivalry',26,90,'Historical2014 mobile engine demo; no claim of later mobile deferred or tile transfers.');
add('horizon-super-resolution','horizon',1,7.35,'CNN/Transformer SR comparison of moving Aloy costume edges.');
add('outer-generated-display','outer',0.5,16,'DLSS4.5/6x display demonstration; displayed FPS is not simulation/input rate.');
add('cyber-light-reconstruction','cyber',44,67,'Moving reflection/light reconstruction comparison; whole feature bundle, no isolated RR benchmark.');
const base='production/research/game-lighting-history/local/part1-native-review-v166';
fs.mkdirSync(path.join(root,base),{recursive:true});
const record=base+'/candidates.json',viewer=base+'/index.html';
if(fs.existsSync(path.join(root,record))||fs.existsSync(path.join(root,viewer)))throw Error('Preserve prepared review');
fs.writeFileSync(path.join(root,record),JSON.stringify({preparedAt:new Date().toISOString(),sources,rows,sourceOffsetVerified:false,rightsApproved:false,actualAllocationApproved:false,newTts:0,newGitImages:0},null,2)+'\n');
const data=JSON.stringify(rows).replaceAll('<','\\u003c');
fs.writeFileSync(path.join(root,viewer),`<!doctype html><meta charset="utf-8"><title>④-1 실제 원본 검수</title><style>body{background:#111;color:#eee;font:16px Malgun Gothic;margin:10px}button,select{font:16px Malgun Gothic;padding:7px}video{max-width:1100px;width:100%;display:block}p{max-width:1100px}#status{color:#e8cf83}</style><h1>④-1 원본 후보 · 정상 속도 움직임 검수</h1><label>후보 <select id="scene"></select></label><button id="play">선택 구간 재생</button><button id="pause">일시정지</button><button id="next">다음 후보</button><button id="start">시작 프레임</button><button id="end">끝 프레임</button><label>검수 시각 <input id="seek" type="number" step="0.1"></label><button id="seekButton">시각 이동</button><p id="status" role="status"></p><video id="v" controls muted preload="metadata"></video><p id="focus"></p><script>const rows=${data},pick=document.querySelector('#scene'),v=document.querySelector('#v'),status=document.querySelector('#status');for(const r of rows){let o=document.createElement('option');o.value=r.id;o.textContent=r.id;pick.append(o)}let row,playing=false;function update(){status.textContent=row.id+' · '+v.currentTime.toFixed(3)+'s · '+(v.paused?'PAUSED':'PLAYING')+' · rate'+v.playbackRate+' · source '+row.ranges[0].join('–')+' · approval pending'}function choose(){v.pause();playing=false;row=rows.find(x=>x.id===pick.value);v.src='/@fs/${root.replaceAll('\\','/')}/'+row.path;document.querySelector('#focus').textContent=row.focus;update()}pick.onchange=choose;document.querySelector('#play').onclick=async()=>{v.currentTime=row.ranges[0][0];v.playbackRate=1;playing=true;await v.play()};document.querySelector('#pause').onclick=()=>{playing=false;v.pause();update()};document.querySelector('#next').onclick=()=>{pick.selectedIndex=Math.min(rows.length-1,pick.selectedIndex+1);choose()};function seek(t){playing=false;v.pause();v.currentTime=t}document.querySelector('#start').onclick=()=>seek(row.ranges[0][0]);document.querySelector('#end').onclick=()=>seek(row.ranges[0][1]-.05);document.querySelector('#seekButton').onclick=()=>seek(Number(document.querySelector('#seek').value));v.ontimeupdate=()=>{if(playing&&v.currentTime>=row.ranges[0][1]){playing=false;v.pause()}update()};v.onerror=()=>status.textContent='SOURCE LOAD ERROR';choose();</script>`);
console.log(JSON.stringify({record,viewer,rows:rows.length,candidateSeconds:rows.reduce((n,r)=>n+r.ranges[0][1]-r.ranges[0][0],0),approved:false,newImages:0}));
