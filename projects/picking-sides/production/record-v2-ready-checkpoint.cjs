const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/picking-sides/production/';
const voice='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const report=read(voice+'picking-sides-qwen3-1.7b-balanced-v2.asr-review.json');
const approval=read(base+'voice-approval.json');
for(const id of ['09','11']){
 const r=report.scenes.find(s=>s.scene===id),wav=voice+'chunks/'+id+'-scene.wav';
 if(!r||hash(wav)!==r.audio_sha256)throw Error('Stale current wave '+id);
 const reason=id==='09'?'All seven paragraphs and the ending recovered without the oldv1invented greeting. ASR 얼티밋→얼티미 is a minor final-consonant ambiguity; all source/camera limitation claims retained.':'All seven paragraphs recovered; genitive 의→에 is normal spoken Korean variation. Separate-attempt and no-overall-winner limitations retained, no omissions or added greeting.';
 approval.scenes=approval.scenes.filter(s=>s.id!==id);
 approval.scenes.push({id,decision:'content-readback-pass',reason,wav,audioSha256:r.audio_sha256,
 approvedAsr:voice+'asr/'+id+'.json',acousticChecks:r.acousticChecks,expected:r.expected,recognized:r.recognized});
}
approval.scenes.sort((a,b)=>a.id.localeCompare(b.id));approval.allCurrentScenesTechnicallyReviewed=false;
approval.reviewedAt=new Date().toISOString();approval.kind='v2-completed-readback-with-targeted02-05-07repairs-pending';
approval.targetedRepair=base+'existing-game-replan/phrase-repair1/request.json';write(base+'voice-approval.json',approval);
const note='2026-10-03 01:43 KST: v2 단일 합성·12장 조립·CPU-ASR(58440/PID27528)은 종료했다. 01/03/09/11과 바이트 동일 설명5장의 읽기 검수 근거를 보존했다. 02 연결문의 지금부터 누락,05 게임명 앞 임의 음절,07 닭의 점프 발음을 확인해 그대로 승인하지 않았다. 별도 구간 ASR81151/81404/49939/87563도 종료했다. 새 phrase-repair1은02연결문·05첫문단·07두문단만 합성 후보로 만든다. 여섯 PPT와29개 원래 설명문단은 바꾸지 않았다. 단일 대기 runner89568/PID58124가 다른 GPU 학습의 여유를 기다리며, 자식0개인 이전 bridge13018/PID40708은 대체 전에 종료했다. 이전58440/13018을 다시 실행하지 않는다. 현재해시/실행 상태는repair-v2-phrases.json과queue를 우선한다. 후보 ASR 직접 검수 후에만 원본PCM 보존 접합·전체 재조립/ASR를 한다.\n\n실측 소스 연결 검토는 existing-game-replan/source-timing-followup.json에 있다.03의 동물 설명은16.30초에 끝나므로85–86.5667새 UCH구간 후16.5667의 일반 위치 설명에서 트럭으로 전환하는 안을 기록했다.07트럭 후반664–674의 새 실제 지붕 동작은 후보이며, 앞쪽 매달린 손 문장에 충분한 구간을 더 맞춰야 한다. 고정자막 충돌·컷 경계·60:40 최종 승인은 미완료다. 대본/소스 계획을 다시 검토 없이 바꾸거나 현재 후보은행을 최종 렌더 증거로 쓰지 않는다.\n\n';
for(const rel of ['projects/picking-sides/README.md','production/batches/sakurai-planning-game-design/README.md']){
 const p=path.join(root,rel),text=fs.readFileSync(p,'utf8'),pos=text.indexOf('\n');
 if(!text.includes('2026-10-03 01:43 KST:'))fs.writeFileSync(p,text.slice(0,pos+1)+'\n'+note+text.slice(pos+1));
}
write(base+'existing-game-replan/checkpoint-20261003-0143.json',{
 updatedAt:new Date().toISOString(),oldParent:{session:58440,pid:27528,status:'finished',assemblySeconds:590.075},
 supersededBridge:{session:13018,pid:40708,childrenStarted:0,status:'stopped-superseded-before-child'},
 currentRepair:{session:89568,pid:58124,state:base+'repair-v2-phrases.json',input:base+'existing-game-replan/phrase-repair1/request.json'},
 remaining:['Candidate02/05/07directASR','PreservedPCMcomposites and all12current-hash ASR','Exact actual-source alignment and60:40','FinalMC/mix/KOENcaptions/render/fullQA/collection/privatecaptionedupload/Git'],
 sourceTiming:base+'existing-game-replan/source-timing-followup.json',renderComplete:false,humanListening:'pending'
});
console.log('Checkpoint saved; six delivered videos remain unchanged, picking-sides not complete.');
