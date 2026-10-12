// Resume only the index/preparation steps after the collector's shared-index lock.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='game-lighting-history-04-1';
const project=path.join(root,'projects',slug),out=path.join(root,'output');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
async function sha(p){const h=crypto.createHash('sha256');for await(const b of fs.createReadStream(p))h.update(b);return h.digest('hex');}
const esc=t=>String(t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const page=(title,content)=>`<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${esc(title)}</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;font:17px/1.7 'Malgun Gothic',sans-serif;color:#202020;background:white}a{color:#24569b}video{width:100%;background:#eee}section{margin:32px 0}small{color:#666}.notice{padding:16px;border-left:4px solid #bb8624;background:#fff8e9}</style><h1>${esc(title)}</h1>${content}</html>`;
async function main(){
 const delivery=read(path.join(project,'production/delivery-output.json'));
 if(delivery.files.length!==4||delivery.directory!=='output/'+slug)throw Error('Unexpected delivery');
 for(const f of delivery.files){const p=path.join(out,slug,f.name);if(fs.statSync(p).size!==f.bytes||await sha(p)!==f.sha256)throw Error('Current output differs: '+f.name);}
 const entries=fs.readdirSync(out,{withFileTypes:true}).filter(e=>e.isDirectory()&&!e.isSymbolicLink()&&fs.existsSync(path.join(out,e.name,'index.html')));
 fs.writeFileSync(path.join(out,'index.html'),page('영상 결과물 모음',`<p>프로젝트마다 자막 영상·무자막 영상·한글 SRT·영어 SRT를 모았습니다. 게시 전 확인 사항은 각 페이지에 표시됩니다.</p><ul>${entries.map(e=>`<li><a href="${encodeURIComponent(e.name)}/index.html">${esc(e.name)}</a></li>`).join('')}</ul>`));
 const receiptPath=path.join(project,'publishing/youtube-upload.json'),u=read(receiptPath);
 if(u.actualVideoId||u.uploaded)throw Error('Preserve actual upload');
 const cap=delivery.files.find(f=>f.name.endsWith('.captioned.mp4'));
 u.video={path:delivery.directory+'/'+cap.name,sha256:cap.sha256,bytes:cap.bytes,seconds:1485.8,frames:89148};
 u.metadata={title:u.titleKo,description:u.descriptionKo,privacyStatus:'private',madeForKids:false};
 u.englishMetadata={title:u.titleEn,description:u.descriptionEn};
 u.descriptionBody={ko:u.descriptionKo.split('\n\n🎮')[0],en:u.descriptionEn.split('\n\n🎮')[0]};
 for(const t of u.subtitles){const f=delivery.files.find(f=>f.name.endsWith('.'+t.language+'.srt'));t.sha256=f.sha256;t.bytes=f.bytes;}
 u.collected=true;u.collectionEvidence='projects/'+slug+'/production/collection-index-resume-v349.json';
 u.inputs.push({path:'projects/game-lighting-history-04/production/part1-final-input-plan-v309.json',sha256:await sha(path.join(root,'projects/game-lighting-history-04/production/part1-final-input-plan-v309.json'))});
 save(receiptPath,u);
 const evidence={completedAt:new Date().toISOString(),status:'four-files-verified-index-resume-complete',initialCollector:{command:'node scripts/collect-video-output.cjs '+slug,exitCode:1,failedStep:'shared projects/rebuild-index.json write after four files and own delivery/rebuild were written',reason:'temporary UNKNOWN file lock'},resume:{scopedRebuildCommand:'node scripts/build-rebuild-manifests.cjs '+slug,observedExitCode:0,rootOutputIndexUpdated:true},files:delivery.files,bytesAndHashesDirectlyVerified:true,mediaCopiesRepeated:false,deliveryArchiveCreated:false,foreignProjectFilesEdited:false,uploaded:false};
 save(path.join(project,'production/collection-index-resume-v349.json'),evidence);
 console.log(JSON.stringify({collected:true,verifiedFiles:4,indexUpdated:true,externalUploadPerformed:false}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
