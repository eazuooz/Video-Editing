const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const root=path.resolve(__dirname,'../../..'),proof='production/batches/sakurai-planning-game-design/proof-similar-game-design/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,j)=>fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');
const target=proof+'content-review-v14.json',prior=proof+'content-review-v13.json';
if(fs.existsSync(path.join(root,target)))throw Error('Preserve v14');
const files=[
 ['projects/game-lighting-history-01/project.json','fb50b47860014e3913264e13d598d812ef071683a9b37f1e2c0c50cef0825a76'],
 ['projects/game-math-projection-depth/project.json','959a27909e0ca7bfbbd2476de12092eda22fa40e212e901f81f98438d932c942'],
 ['projects/game-math-projection-depth/README.md','907257da96e61707ccfd2d43c4d2a222e531e66d95f14ad2a3d76b33815e70a5'],
 ['projects/game-math-projection-depth/publishing/youtube-upload.json','4d682dcb953779f1dfb4113fc957c7aa9a27ffc1298645b3ba546b858c6b1f1b']
];
for(const [p,h] of files)if(sha(p)!==h)throw Error('Changed after complete direct read: '+p);
const ax='shared/output/similar-game-design/preflight/studio-current-list-v14.ax.txt',rows='shared/output/similar-game-design/preflight/studio-current-rows-v14.json';
if(read(rows).rows.length!==30)throw Error('Expected30 rendered rows');
const detail={schemaVersion:1,reviewedAt:new Date().toISOString(),previousReview:{path:prior,sha256:sha(prior)},files:files.map(([p,h])=>({path:p,sha256:h,entireCurrentFileDirectlyRead:true,foreignFileModified:false})),detailsKo:'변경된 조명1편 manifest 전체와 깊이/w 수학의 manifest·README·현재 receipt 전체를 직접 읽었다. 조명은 DOOM sector/Quake lightmap/forward-deferred 질문과 현재108문단 음성1260.87025초,07 수정ASR 및 최종미승인을 보존한다. 깊이/w는10장66문단의 수학 질문을 그대로 유지하면서 실제38020프레임633.6667초,40:60/noBGM·현재QA와4파일을 수집한 상태다. receipt가 읽는 동안 업로드중으로 변경되어 전체를 다시 읽었고 PuXZUArWFko/설정pending을 보존했다. 전체 KOEN 설명/챕터/권리·청취pending은 이전 질문을 유지한다. Studio에서 보인18% 미확인초안을 이 ID의 검수완료로 추정하지 않는다. 둘 다 익숙한 장르에 목적·공간·함께 플레이를 조합해 새 게임을 만들 이유를 설계하는 우리 질문과 다르다. 다른 강의의 예외와 pending을 우리 제작 승인으로 복사하지 않는다.',studio:{ax,axSha256:sha(ax),rows,rowsSha256:sha(rows),renderedRowsDirectlyRead:30,observedAt:read(rows).observedAt,unknownUploadingDraft:{title:'To do....',progress:'18%',videoIdObserved:false,contentIdentified:false},c96qTnlHBVU:{privacy:'private',checks:'reviewing'},listDescriptionsTruncated:true,relatedFullDetailsRetainPreviousReview:true,platformWrites:0},foreignWrites:0};
write(proof+'current-foreign-delivery-change-review-v14.json',detail);
const j=read(prior);j.reviewedAt=detail.reviewedAt;j.previousReview=detail.previousReview;j.currentForeignChangeReview=detail.files;j.addedWholeScriptReview=proof+'current-foreign-delivery-change-review-v14.json';j.currentStudio.currentList=detail.studio;j.scope+=' Entire changed lighting manifest and depth/w manifest, README and prepared KOEN upload receipt directly reread;30 current Studio rendered rows reread. An18% uploading draft is unidentified, not a confirmed topic or completed upload.';delete j.gate;j.gateStatus='awaiting-current-check';write(target,j);
let r=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','similar-game-design','--decision','distinct','--reason','기존 전체 개념·관련 전체 KOEN·현재 Studio 및 변경4파일 전체 직접 검토 근거 '+target+'. 조명/깊이 수학은 새 장르 작품의 고유 매력 설계와 다르며 미확인 업로드 초안은 내용 승인으로 사용하지 않음.','--studio-evidence',target],{cwd:root,encoding:'utf8'});if(r.status!==0)throw Error(r.stderr||r.stdout);
const current=read('production/batches/sakurai-planning-game-design/preflight/similar-game-design.json');for(const [p,h]of files)if(current.inputFiles.find(x=>x.path===p)?.sha256!==h)throw Error('Concurrent input change: '+p);
r=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','similar-game-design','--check'],{cwd:root,encoding:'utf8'});if(r.status!==0)throw Error(r.stderr||r.stdout);j.gateStatus='current-distinct-check-passed';j.gate={command:'node scripts/review-video-duplicates.cjs similar-game-design --check',exitCode:0,checkedAt:new Date().toISOString(),inputsDigest:current.inputsDigest};write(target,j);console.log(JSON.stringify({proof:target,digest:current.inputsDigest,check:0,foreignWrites:0}));
