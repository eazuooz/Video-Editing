// Record the actual incremental full-content comparison; no foreign project writes.
const fs=require('node:fs'),cp=require('node:child_process'),crypto=require('node:crypto');
const root='production/research/game-lighting-history/',slug='game-lighting-history-03';
const json=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const changes=json(root+'local/episode03-current-distinct-changes-v21.json');
const stamp=new Date().toISOString();
const studio=['foundations','calculations','conversions'].map(k=>{
 const p=`projects/${slug}/publishing/local/proof-v21/duplicate-${k}-current.ax.txt`;
 const t=fs.readFileSync(p,'utf8');
 const id={foundations:'HdJw7bgKlbM',calculations:'SPq_41LyOG0',conversions:'n-k7zwaSum0'}[k];
 if(!t.includes(id)||!t.includes('text entry area'))throw Error('Actual full details evidence missing: '+k);
 return {kind:k,path:p,sha256:sha(Buffer.from(t)),actualId:id,readOnly:true};
});
const record={schemaVersion:1,reviewedAt:stamp,priorRecord:root+'current-duplicate-rereview-v11.json',
 method:'All newly changed KO/EN scripts directly read in full; truncation repaired by separate complete reads. Full metadata read either literally or as a recursive complete structural delta against a directly-read manifest. Outline exact script repetitions verified by exact string equality and referenced to the already-read full scene; all other outline prose, claims and sequence read directly.',
 changedFiles:changes.map(x=>({path:x.path,priorSha256:x.old,sha256:sha(fs.readFileSync(x.path)),bytes:fs.statSync(x.path).size})),
 fullScriptReads:['interpolation-numeric-retakes-v4','interpolation-paths-v2','interpolation-teaching-additions-v2','interpolation-worked-checks-v3','quaternion-foundations-v2','quaternion-calculations-v2',...Array.from({length:6},(_,i)=>'quaternion-teaching-additions-v'+(i+2)),'rotation-conversions-v2','limited-color-world'].map(x=>'projects/'+(x==='limited-color-world'?x:'game-math-'+x)),
 comparisons:[
 'Quaternion foundations: imaginary multiplication, four components, half angles, unit norm, sign equivalence and inverse. Calculations: Hamilton dot/cross, ordered world/body composition, relative target orientation, shortest angle and q[0,v]q^-1. These teach orientation algebra, not historical light-transport data and rendering pipelines.',
 'Interpolation and conversions: delta^t*start, SLERP/NLERP, unit arcs, physical angle versus quaternion arc, timing/history, declared Y-X-Z conventions and matrix/quaternion/axis-angle round trips. Shared vectors and ray words do not duplicate BVH intersection, radiance estimators, visibility buffers, temporal reconstruction, Nanite or Lumen.',
 'Polar3D changes retain cylindrical/spherical coordinates, heading/pitch, target/camera placement and projected math annotations; same independent coordinate question.',
 'Limited-color-world: Chicory contour, paint/erase, mushroom height, flower current state and local cave contrast; a readability/game-design question. Does not teach lighting algorithms or infer engine internals from appearance.'
 ],studio,foreignFilesModified:false,decision:'distinct',
 boundaries:'Foreign lecture40:60/noBGM/white exceptions remain foreign; this series retains60:40/Nimbus/research-black-v1. Conversion actual draft settings/processing are incomplete; no foreign upload completion inferred.'};
const target=root+'episode03-current-distinct-rereview-v21.json';fs.writeFileSync(target,JSON.stringify(record,null,2)+'\n');
const prior=json('production/preflight/'+slug+'.json');
const reason=prior.contentReview+'; incremental full current comparison: '+target+'. '+record.comparisons.join(' ');
const evidence=prior.studioEvidence+'; latest read-only actual Studio full descriptions: '+studio.map(x=>x.actualId+' '+x.path).join('; ');
const r=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs',slug,'--candidate-file',root+'candidate-03.json','--decision','distinct','--reason',reason,'--studio-evidence',evidence],{encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stdout+r.stderr);
console.log(r.stdout.trim());
const check=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs',slug,'--candidate-file',root+'candidate-03.json','--check'],{encoding:'utf8',windowsHide:true});if(check.status!==0)throw Error(check.stdout+check.stderr);console.log(check.stdout.trim());
const manifestPath=`projects/${slug}/project.json`,manifest=json(manifestPath);
manifest.productionGates.currentDistinct=true;manifest.currentDuplicateReview={record:target,sha256:sha(fs.readFileSync(target)),preflight:'production/preflight/'+slug+'.json',inputsDigest:json('production/preflight/'+slug+'.json').inputsDigest,checkedAt:stamp};fs.writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+'\n');
