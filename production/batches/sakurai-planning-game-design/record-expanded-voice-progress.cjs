const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/sakurai-planning-game-design',proof=batch+'/proof-avoid-game-comparisons',project='projects/avoid-game-comparisons';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const r=read(proof+'/expanded-voice-git-verification.json');
if(r.pushExitCode!==0||!r.remoteMatches||r.completedVideoDelivery)throw Error('Actual progress push evidence required');
const evidence={commit:r.expandedVoiceProgressCommit,verifiedAt:r.verifiedAt,localSha:r.localSha,remoteSha:r.remoteSha,normalPush:r.normalPush,pushExitCode:r.pushExitCode,remoteMatches:r.remoteMatches,paths:r.commitPaths.length,newRasterCommitted:0,mediaCommitted:false,otherUsersFilesIncluded:false,completedVideoDelivery:false,evidence:proof+'/expanded-voice-git-verification.json',current14SceneTechnicalAsrApproved:true,finalTimingRatioApproved:false};
const now=new Date().toISOString();
function update(c){c.updatedAt=now;c.expandedVoiceProgressGit=evidence;c.nextAction='Use current14 measured PCM and native source boundaries to resolve scene06 rocket/cup,10 short vehicle/cylinder/assist,13 tilt/key and14 red-chest/card cue alignment. Writing/reflection diagrams count as explanation. Then final frames/body60:40 and13/14 diagram pixel review; mix/SRT/chapters/outro/render/QA/output/private upload still pending.';return c;}
for(const p of [proof+'/latest-checkpoint.json',project+'/production/latest-checkpoint.json'])write(p,update(read(p)));
const q=read(batch+'/queue.json');
function visit(o){if(!o||typeof o!=='object')return;if(o.slug==='avoid-game-comparisons'&&o.stage)update(o);for(const v of Object.values(o))if(v&&typeof v==='object')Array.isArray(v)?v.forEach(visit):visit(v);}
visit(q);q.expandedVoiceProgressGit=evidence;write(batch+'/queue.json',q);
const check=proof+'/expanded-voice-evidence-pre-delivery-checks.json';
const paths=[batch+'/record-expanded-voice-progress.cjs',batch+'/deliver-expanded-voice-evidence.cjs',batch+'/expanded-voice-evidence-paths.json',batch+'/queue.json',proof+'/latest-checkpoint.json',proof+'/expanded-voice-git-verification.json',check,project+'/production/latest-checkpoint.json'];
write(batch+'/expanded-voice-evidence-paths.json',paths);
let runner=fs.readFileSync(path.join(root,batch+'/deliver-expanded-voice-progress.cjs'),'utf8');
runner=runner.replaceAll('expanded-voice-pre-delivery-checks','expanded-voice-evidence-pre-delivery-checks').replaceAll('expanded-voice-delivery-paths','expanded-voice-evidence-paths').replaceAll('expanded-voice-git-verification','expanded-voice-evidence-git-verification').replaceAll('expandedVoiceProgressCommit','expandedVoiceEvidenceCommit').replace('Review additive game-pitch narration and mixed actual-action explanation scenes','Record verified additive game-pitch narration progress push evidence');
fs.writeFileSync(path.join(root,batch+'/deliver-expanded-voice-evidence.cjs'),runner);
console.log(JSON.stringify({actualProgressCommit:evidence.commit,files:evidence.paths,evidenceScope:paths.length,completedVideoDelivery:false}));
