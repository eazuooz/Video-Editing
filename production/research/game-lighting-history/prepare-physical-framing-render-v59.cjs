const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const folder='production/research/game-lighting-history/local/episode04-physical-framing-v59';
const src='motion-canvas/src/projects/game-lighting-history-04/spatial/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)});
const write=(p,j)=>{const f=path.join(root,p);if(fs.existsSync(f))throw Error('Preserve existing '+p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof j==='string'?j:JSON.stringify(j,null,2)+'\n');};
const selectedPath=base+'physical-framing-selected-execution-v55.json',reviewPath=base+'physical-framing-direct-text-review-v59.json';
const selected=read(selectedPath),review=read(reviewPath),request=read(base+'physical-framing-tts-request-v49.json');
if(!review.allTenCompleteTextsCompared||!review.sourceSceneReviewRenderingAllowed||review.selectedTakes.sha256!==sha(selectedPath))throw Error('Direct review source binding required');
// Cues preserve all supplied wording. Endpoints below were directly read from
// the whole-word ASR results; disputed spellings do not replace the script.
const data={
 'part1-overview':{title:'계산과 메모리를 어디에 쓸까?',cues:[
 [0,3.94,'화면을 더 선명하게 만들려면\n어디에 계산과 메모리를 써야 할까요?'],
 [4.18,7.2,'이번 편은 그림자 페이지,\n시간적 업스케일링,'],
 [7.2,9.34,'모바일 렌더링을 차례로 연결합니다.'],
 [9.62,12.16,'실제 엔진 시연과 작은 수치 예시를 보며,'],
 [12.16,15.5,'먼저 필요한 그림자만 저장하는\n방법부터 살펴보죠.']],
 stages:[[0,3.94,0,.02,'질문'],[4.72,5.78,.02,.22,'그림자 페이지'],[5.78,7.2,.22,.48,'시간적 업스케일링'],[7.2,8.22,.48,.7,'모바일 렌더링'],[12.66,15.5,.7,1,'필요한 그림자만 저장']]},
 'part1-conclusion':{title:'필요한 정보와 남는 비용',cues:[
 [0,4.22,'필요한 그림자만 저장하고,\n유효한 이전 표본을 재사용하며,'],
 [4.22,7.26,'기기에 맞게 중간 데이터를 다루었습니다.'],
 [7.44,9.18,'핵심은 계산을 없애는 것이 아니라'],
 [9.18,12.48,'필요한 정보와 남는 비용을\n구별하는 것입니다.'],
 [12.68,14.28,'다음 편은 그 예산 안에서'],
 [14.28,18.06,'빛의 경로와 광원 표본을\n고르는 문제로 이어집니다.']],
 stages:[[0,1.76,0,.22,'그림자 저장'],[1.76,4.22,.22,.48,'이전 표본 재사용'],[4.22,7.26,.48,.7,'기기의 중간 데이터'],[7.44,12.48,.7,.85,'정보와 비용 구별'],[14.28,18.06,.85,1,'다음 표본 질문']]},
 'part2-overview':{title:'모든 경로를 계산할 수 없다면?',cues:[
 [0,4.5,'빛의 경로를 모두 계산할 수 없다면\n어떤 표본을 골라야 할까요?'],
 [4.92,8.18,'이번 편에서는 사이버펑크의\n경로 추적과 복원,'],
 [8.18,12.5,'언리얼의 많은 광원,\n가는 머리카락과 겹침을 연결합니다.'],
 [12.84,15.16,'실제 화면의 변화와 계산 예시를 비교하며,'],
 [15.16,18.9,'먼저 경로 하나가 밝기에\n기여하는 과정부터 보죠.']],
 stages:[[0,4.5,0,.04,'표본 질문'],[5.68,7.56,.04,.3,'사이버펑크 경로'],[7.56,10,.3,.6,'복원과 광원'],[10.06,12.5,.6,.88,'겹친 표면'],[15.68,18.9,.88,1,'한 경로의 기여']]},
 'part2-conclusion':{title:'가시성과 복원의 서로 다른 책임',cues:[
 [0,4.24,'중요한 경로와 광원을 선택해도\n표본 부족은 남고,'],
 [4.24,8.2,'머리카락처럼 가늘고 겹친 표면은\n추가 정보가 필요합니다.'],
 [8.56,10.26,'그래서 가시성을 구하는 단계와'],
 [10.26,13.24,'남은 정보를 복원하는 단계를\n나누어 보았습니다.'],
 [13.4,16.94,'다음 편에서는 이 결과가 마지막 화면으로\n바뀌는 과정과'],
 [16.94,19.58,'실제 프레임 검사를 연결하겠습니다.']],
 stages:[[0,4.24,0,.3,'표본 선택'],[4.24,8.2,.3,.6,'얇고 겹친 표면'],[8.56,13.24,.6,.88,'가시성과 복원 구별'],[13.4,19.58,.88,1,'최종 화면과 검사']]},
 'part3-overview':{title:'화면만으로 내부 계산을 알 수 있을까?',cues:[
 [0,3.14,'좋아 보이는 화면만으로\n내부 계산까지 알 수 있을까요?'],
 [3.46,6.44,'이번 편은 디엘에스에스 오까지의\n역할을 정리한 뒤,'],
 [6.6,8.84,'노출과 초점의 실제 시연을 거쳐'],
 [9.06,11.28,'프레임의 입력과 출력을 검사합니다.'],
 [11.5,13.82,'표시 프레임과 게임의 계산을 구별하고,'],
 [14.12,16.46,'먼저 재구성이 맡는 책임부터 확인하죠.']],
 stages:[[0,3.14,0,.01,'내부 계산 질문'],[4,6.44,.01,.25,'DLSS 역할'],[6.6,8.84,.25,.5,'노출과 초점'],[9.06,11.28,.5,.75,'프레임 입력 출력'],[11.5,16.46,.75,1,'표시와 계산 구별']]},
};
let cursor=0;const scenes=[];
for(const s of request.scenes){
 const r=selected.results.find(r=>r.id===s.id),d=data[s.id];if(sha(r.path)!==r.sha256)throw Error('PCM changed');
 const frames=Math.ceil(r.samples/400),wrapper=src+'physical-framing-'+s.id+'-v59.tsx';
 const cues=d.cues.map(([a,b,text])=>({fromFrame:Math.round(a*60),toFrame:Math.min(frames,Math.round(b*60)),text}));
 const stages=d.stages.map(([a,b,p,q,anchor])=>({fromFrame:Math.round(a*60),toFrame:Math.min(frames,Math.round(b*60)),progressFrom:p,progressTo:q,anchor}));
 const normalize=t=>t.replace(/\s+/g,'');
 if(normalize(cues.map(c=>c.text).join(''))!==normalize(s.ko))throw Error('Caption wording omission: '+s.id);
 write(wrapper,`import {physicalFramingScene} from './physical-framing-runtime-v59';\nexport default physicalFramingScene(${JSON.stringify({role:s.id,title:d.title,frames,sourceSha256:r.sha256,boundSourceSha256:r.sha256,allWholeAndContextTextsCompared:true,stages},null,2)});\n`);
 write(wrapper.replace(/\.tsx$/,'.meta'),{version:0,timeEvents:[],seed:59000+scenes.length});
 scenes.push({id:s.id,role:s.role,physicalPart:s.physicalPart,wrapper:ref(wrapper),source:ref(r.path),sourceSamples:r.samples,frames,fromFrame:cursor,toFrame:cursor+frames,silentPaddingSamples:frames*400-r.samples,textKo:s.ko,textEn:s.en,cues,stages});cursor+=frames;
}
const name='episode04-physical-framing-v59',project=src+name+'.ts',audio=folder+'/audio/'+name+'.wav';
write(project,"import {makeProject} from '@motion-canvas/core';\n"+scenes.map((s,i)=>`import s${i} from './physical-framing-${s.id}-v59?scene';`).join('\n')+`\nexport default makeProject({scenes:[${scenes.map((s,i)=>'s'+i).join(',')}],audio:'/@fs/${root.replaceAll('\\','/')+'/'+audio}'});\n`);
write(project.replace(/\.ts$/,'.meta'),{version:0,shared:{background:null,range:[0,(cursor-1)/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:30,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:true}}}});
const template=fs.readFileSync(path.join(root,'motion-canvas/vite.game-lighting-history04.inspection-math-repair-v40.config.ts'),'utf8');
write('motion-canvas/vite.game-lighting-history04.physical-framing-v59.config.ts',template.replaceAll('episode04-inspection-math-repair-v40',name).replaceAll('inspection-math-repair-v40','physical-framing-v59').replace('port:9269','port:9270'));
write('motion-canvas/tsconfig.game-lighting-history04-physical-framing-v59.json',{extends:'./tsconfig.json',include:['src/env.d.ts',src.replace('motion-canvas/','')+'physical-framing-runtime-v59.tsx',...scenes.map(s=>s.wrapper.path.replace('motion-canvas/','')),project.replace('motion-canvas/','')]});
write(folder+'/plan.json',{schemaVersion:1,preparedAt:new Date().toISOString(),review:ref(reviewPath),selected:ref(selectedPath),model:ref(src+'physical-framing-model-v57.tsx'),runtime:ref(src+'physical-framing-runtime-v59.tsx'),
 jobs:[{name,project,frames:cursor,audio:{path:audio,samples:cursor*400},output:folder+'/renders/'+name+'.mp4',execution:folder+'/renders/'+name+'.execution.json'}],scenes,
 palette:'research-black-v1',classification:'explanation',captionStyle:'boxed-white-forest-v1',captionsBurnedIntoSource:false,cpuThreads:2,gpuJobs:0,
 original111Regenerated:false,rendered:false,animatedPixelsReviewed:false,finalMixedAsrApproved:false,uploaded:false});
console.log(JSON.stringify({independentScenes:5,frames:cursor,seconds:cursor/60,cues:scenes.reduce((n,s)=>n+s.cues.length,0),imageFiles:0,rendered:false}));
