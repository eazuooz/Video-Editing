const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const mfile=path.join(root,'projects/counting-animation-frames/project.json'),m=read(mfile),qafile=path.join(__dirname,'final-v2/qa.json'),qa=read(qafile);
if(m.finalRender.revision!=='final-v2'||qa.visualReview!=='passed-direct-all-cue-and-cut-inspection')throw Error('Current final-v2 render and direct QA required');
m.finalRender.knownIssues=[...new Set([...m.finalRender.knownIssues,'전체 내레이션 인간 청취와 공개 사용 권리의 최종 검토가 남아 있습니다.','현재 수정본은 final-v2이며 기존 piZTx_239R8 업로드는 final-v1입니다.'])];
m.localRevision.status='rendered-qa-collected-awaiting-user-review';write(mfile,m);
execFileSync(process.execPath,['scripts/collect-video-output.cjs','counting-animation-frames'],{cwd:root,stdio:'inherit',windowsHide:true});
const delivery=read(path.join(__dirname,'delivery-output.json'));
for(const f of delivery.files){const actual=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,delivery.directory,f.name))).digest('hex');if(actual!==f.sha256)throw Error('Collected file changed');}
const checkpoint=path.join(__dirname,'revision-v2.json'),r=read(checkpoint),now=new Date().toISOString();
Object.assign(r,{status:'rendered-qa-collected-awaiting-git',stage:'final-four-files-collected',updatedAt:now,delivery:{...delivery,revision:'final-v2',qa:'projects/counting-animation-frames/production/final-v2/qa.json'},nextAction:'Selective metadata/code/caption/evidence commit and normal push. Do not wait on finished jobs or recreate this revision; old uploaded final-v1 is preserved.'});write(checkpoint,r);
const qfile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qfile),item=q.items.find(i=>i.slug==='counting-animation-frames');item.revision=r;item.delivery={...item.delivery,revision:'final-v2',qa:r.delivery.qa,uploadedRevision:'final-v1',uploadedVideoId:'piZTx_239R8'};item.publishing.revision='final-v1';q.updatedAt=now;write(qfile,q);
const readme=path.join(root,'production/batches/sakurai-planning-game-design/README.md'),marker='## 프레임 세기 수정본 final-v2';
if(!fs.readFileSync(readme,'utf8').includes(marker))fs.appendFileSync(readme,`\n${marker}\n\n사용자의 실제 격투게임 예시 추가 요청에 따라 본론02–06장에 새로운 SF6 류·춘리와 GGST 솔 동작을 교차 삽입했습니다. 상용 게임70.017초·자체 실행 테스트44.233초·흰2.5D 설명71.350초이며 본편의 실제 예시는61.557%입니다. 기존 내레이션과 한영50큐 시간은 유지했습니다. 197.6초 최종 두 MP4 전체 디코딩·음량·동일 AAC·58개 자막/컷 구간과 전체 ASR 직접 검수 후 output/counting-animation-frames에4개 파일을 모았습니다. 이전 로컬 완성본과 piZTx_239R8 업로드의 final-v1 기록은 보존했습니다. 현재 업로드가 수정본이라는 뜻은 아니며 자동 중복 업로드하지 않습니다. 사람 청취·공개 권리·Nimbus 원래 파일·회원 잘린 핸들·외부 백업은 미완료로 유지합니다. 실행 세션은 종료됐고 다음 game-writing은 변경된 전체 프로젝트 기준으로 중복 근거를 새로 확인한 후 진행합니다.\n`);
console.log('Current final-v2 delivery hashes verified; previous actual upload kept distinct.');
