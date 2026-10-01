const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const file=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const queue=JSON.parse(fs.readFileSync(file,'utf8')),now=new Date().toISOString();
const duplicate=queue.items.find(v=>v.slug==='natural-tutorials');
Object.assign(duplicate,{status:'skipped-duplicate',stage:'duplicate-confirmed',updatedAt:now,
 duplicateReview:{verdict:'duplicate',report:'production/batches/sakurai-planning-game-design/preflight/natural-tutorials.json',existingProjects:['play-first','let-them-play'],existingVideoIds:['IHKv1p_aSJ4','bSPwEfdU_JI'],reason:'Existing scripts already teach one action at a time, immediate result, failure clues and guidance at the necessary moment; actual Studio titles/descriptions verified.'},
 nextAction:'Preserve existing videos; do not create script, voice, project or upload for this duplicate.'});
const item=queue.items.find(v=>v.slug==='praise-player');
Object.assign(item,{status:'in-production',stage:'independent-script-and-fresh-source-review',startedAt:item.startedAt||now,updatedAt:now,
 duplicateReview:{verdict:'distinct',report:'production/batches/sakurai-planning-game-design/preflight/praise-player.json',scope:'Immediate, specific and proportionate recognition with rewards/performance held equal; distinct from visible-rewards and tutorial topics.'},
 paths:{project:'projects/praise-player/project.json',script:'projects/praise-player/script/narration.ko.json',sources:'projects/praise-player/sources/game-candidates.json'},
 nextAction:'Verify new official gameplay cuts; author original bilingual six-scene script and executable comparisons; single approved-voice synthesis. No final render/upload yet.'});
queue.currentSlug=item.slug;queue.updatedAt=now;queue.lastProgressAt=now;
queue.progress.duplicateExcluded=queue.items.filter(v=>v.status==='skipped-duplicate').length;
queue.progress.remaining=queue.items.filter(v=>!['skipped-duplicate','uploaded-private-awaiting-user-review'].includes(v.status)).length;
fs.writeFileSync(file,JSON.stringify(queue,null,2)+'\n');
const readme=path.join(root,'production/batches/sakurai-planning-game-design/README.md');
let text=fs.readFileSync(readme,'utf8').replace('다음 natural-tutorials는 이 확인부터 시작한다.','natural-tutorials는 실제 Studio의 IHKv1p_aSJ4/bSPwEfdU_JI와 기존 전체 대본의 실질 중복으로 제외했다. praise-player는 distinct 사전 검토를 통과했다.').replace('다음은 natural-tutorials이며 나머지 21편을 순서대로 진행한다.','natural-tutorials 한 편은 중복으로 제외했으며 다음 praise-player부터 남은 20편을 같은 사전 검토로 진행한다.');
fs.writeFileSync(readme,text);
console.log({current:item.slug,duplicate:duplicate.slug,remaining:queue.progress.remaining});
