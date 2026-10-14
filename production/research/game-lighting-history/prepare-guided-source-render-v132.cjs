const fs=require('node:fs'),path=require('node:path'),c=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/',src='motion-canvas/src/projects/game-lighting-history-04/spatial/',folder='production/research/game-lighting-history/local/guided-source-render-v132';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>c.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),ref=p=>({path:p,sha256:sha(p)});
const write=(p,v)=>{p=path.join(root,p);if(fs.existsSync(p))throw Error('Preserve '+p);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const scriptPath='projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json',script=read(scriptPath),selected=read(b+'part3-guided-actions-selected-execution-v84.json'),newSelected=read(b+'native-followup-selected-v126.json'),review=read(b+'guided-observation-asr-direct-progress-v112.json'),followup=read(b+'native-followup-asr-direct-review-v130.json');
if(!followup.allTenFullTextsDirectlyCompared||!followup.wholeAndIndependentPhraseCoverageAccepted)throw Error('Direct followup comparison required');
const data={
 'appearance-prerequisite':{title:'같은 책임, 서로 다른 표면',cues:[
 [0,2.54,'같은 역할을 서로 다른 게임에서 비교해 보죠.'],[2.8,7.04,'앞의 세 영상은 이천이십육년 삼월의\n디엘에스에스 오 미리보기입니다.'],[7.6,9.34,'끄기와 켜기 표시를 먼저 읽고,'],[9.62,11.52,'얼굴과 옷에 입혀진 빛을 보겠습니다.'],[11.94,15.5,'구월의 농구 게임 출시 사례는\n이 미리보기와 따로 구분하죠.']],stages:[[0,2.54,0,.12,'서로 다른 게임'],[2.8,7.04,.12,.3,'삼월 미리보기'],[7.6,9.34,.3,.5,'끄기와 켜기 표시'],[9.62,11.52,.5,.64,'얼굴과 옷의 빛'],[11.94,15.5,.64,1,'구월 출시 사례 구별']]},
 'appearance-to-controls':{title:'표현을 보고 입력을 확인하기',cues:[
 [0,3.64,'네 게임의 차이를\n최종 화면의 표면 표현으로 비교했습니다.'],[4,5.78,'이제 원인을 직접 조절해 보죠.'],[6.1,10.36,'조명을 옮기지 않고도 노출과 초점 설정만으로\n화면은 바뀔 수 있습니다.'],[10.68,13.2,'먼저 편집기에서 설정과 결과를 연결하고,'],[13.44,16.22,'그다음 프레임 안의 실제 자료를 검사하겠습니다.']],stages:[[0,3.64,0,.16,'네 게임의 표면 표현'],[4,5.78,.16,.38,'입력 조절'],[6.1,10.36,.38,.58,'노출과 초점'],[10.68,13.2,.58,.72,'설정과 결과'],[13.44,16.22,.72,1,'프레임 자료 검사']]},
 'focus-later-settings':{title:'흐림을 거리 영역으로 나누기',cues:[
 [0,3.46,'뒤의 편집기 구간에서도\n같은 상자 배치가 기준입니다.'],[3.76,5.18,'조절창에서 선택한 항목과'],[5.18,7.92,'가까운 면, 먼 면을 번갈아 보세요.'],[8.14,12.96,'화면 전체의 흐림 정도만 기억하면\n어떤 거리 영역이 달라졌는지 놓칠 수 있습니다.'],[13.24,15.08,'초점 기준과 앞뒤 영역을 나누면'],[15.08,18.3,'변화가 일어난 위치를\n더 구체적으로 설명할 수 있습니다.']],stages:[[0,3.46,0,.25,'같은 상자 기준'],[3.76,7.92,.25,.52,'가까운 면과 먼 면'],[8.14,12.96,.52,.75,'달라진 거리 영역'],[13.24,18.3,.75,1,'초점 기준과 앞뒤 위치']]},
 'focus-observation-protocol':{title:'입력, 변화, 영향을 순서대로',cues:[
 [0,2.7,'시연을 다시 볼 때에는\n먼저 입력 이름을 읽고,'],[2.7,4.66,'그 값이 바뀌는 순간을 찾고,'],[4.66,6.86,'마지막으로 영향을 받은 면을 보세요.'],[7.2,10.72,'카메라가 함께 움직이면\n그 변화도 별도로 기록합니다.'],[10.92,15.36,'이렇게 원인 후보를 나누는 방법은\n다른 엔진의 후처리 비교에서도 쓸 수 있지만,'],[15.36,18.54,'모든 엔진의 내부 순서가 같다는 뜻은 아닙니다.']],stages:[[0,2.7,0,.17,'입력 이름'],[2.7,4.66,.17,.43,'값의 변화'],[4.66,6.86,.43,.62,'영향받은 면'],[7.2,10.72,.62,.83,'카메라 별도 기록'],[10.92,18.54,.83,1,'관찰 방법과 내부 순서 구별']]},
 'focus-to-frame-inspection':{title:'표시된 화면에서 프레임 자료로',cues:[
 [0,2.14,'지금까지 네 게임의 최종 표현과'],[2.14,5.22,'편집기의 노출, 색, 초점을 비교했습니다.'],[5.48,7.58,'화면에서 변화를 보는 방법은 생겼지만,'],[7.58,12.12,'어느 명령이 어떤 자료를 읽었는지는\n아직 별도의 질문입니다.'],[12.34,14.6,'다음 프레임 검사에서는 기능의 이름보다'],[14.6,17.74,'실제 입력과 출력의 연결을 찾아보겠습니다.']],stages:[[0,5.22,0,.26,'네 게임과 편집기 화면'],[5.48,7.58,.26,.45,'표시된 결과'],[7.58,12.12,.45,.73,'명령과 입력의 남은 질문'],[12.34,17.74,.73,1,'프레임 입력과 출력']]}
};
let cursor=0;const scenes=[];
for(const [id,d] of Object.entries(data)){
 const s=script.scenes.find(s=>s.id===id),r=(id==='focus-to-frame-inspection'?newSelected:selected).results.find(r=>r.id===id);
 if(!s||!r||!r.technicalTailGatePassed||sha(r.path)!==r.sha256)throw Error('Selected PCM changed '+id);
 const resultPath=b+'local/'+(id==='focus-to-frame-inspection'?'native-followup-asr-v124':'guided-observation-asr-v107')+'/whole-'+id+'.json';
 if(id!=='focus-to-frame-inspection'&&!review.rows.some(x=>x.label==='whole-'+id&&x.directlyCompared)){
  const row=review.rows.find(x=>x.label==='whole-'+id);if(!row)throw Error('Whole review missing '+id);
 }
 const norm=t=>t.replace(/\s+/g,'');if(norm(d.cues.map(c=>c[2]).join(''))!==norm(s.ko))throw Error('Caption wording loss '+id);
 const frames=Math.ceil(r.samples/400),wrapper=src+'guided-'+id+'-v132.tsx';
 const stages=d.stages.map(([a,z,p,q,anchor])=>({fromFrame:Math.round(a*60),toFrame:Math.min(frames,Math.round(z*60)),progressFrom:p,progressTo:q,anchor}));
 write(wrapper,`import {guidedSourceScene} from './guided-source-runtime-v132';\nexport default guidedSourceScene(${JSON.stringify({role:id,title:d.title,frames,sourceSha256:r.sha256,boundSourceSha256:r.sha256,wholeAndContextCompared:true,stages},null,2)});\n`);
 write(wrapper.replace(/\.tsx$/,'.meta'),{version:0,timeEvents:[],seed:132000+scenes.length});
 scenes.push({id,effectiveRole:'explanation',wrapper:ref(wrapper),source:ref(r.path),sourceSamples:r.samples,frames,fromFrame:cursor,toFrame:cursor+frames,silentPaddingSamples:frames*400-r.samples,ko:s.ko,en:s.en,cues:d.cues.map(([a,z,text])=>({fromFrame:Math.round(a*60),toFrame:Math.min(frames,Math.round(z*60)),text})),stages,wholeAsr:ref(resultPath)});cursor+=frames;
}
const name='episode04-guided-source-v132',project=src+name+'.ts',audio=folder+'/audio/'+name+'.wav';
write(project,"import {makeProject} from '@motion-canvas/core';\n"+scenes.map((s,i)=>`import s${i} from './guided-${s.id}-v132?scene';`).join('\n')+`\nexport default makeProject({scenes:[${scenes.map((s,i)=>'s'+i).join(',')}],audio:'/@fs/${root.replaceAll('\\','/')+'/'+audio}'});\n`);
write(project.replace(/\.ts$/,'.meta'),{version:0,shared:{background:null,range:[0,(cursor-1)/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:30,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:true}}}});
const template=fs.readFileSync(path.join(root,'motion-canvas/vite.game-lighting-history04.physical-framing-v59.config.ts'),'utf8');
write('motion-canvas/vite.game-lighting-history04.guided-source-v132.config.ts',template.replaceAll('episode04-physical-framing-v59',name).replaceAll('physical-framing-v59','guided-source-v132').replace('local/'+name,folder.slice(folder.indexOf('local/'))).replace('port:9270','port:9272'));
write('motion-canvas/tsconfig.game-lighting-history04-guided-source-v132.json',{extends:'./tsconfig.json',include:['src/env.d.ts',src.replace('motion-canvas/','')+'guided-source-runtime-v132.tsx',...scenes.map(s=>s.wrapper.path.replace('motion-canvas/','')),project.replace('motion-canvas/','')]});
write(folder+'/plan.json',{schemaVersion:1,preparedAt:new Date().toISOString(),review:ref(b+'guided-observation-asr-direct-progress-v112.json'),followupReview:ref(b+'native-followup-asr-direct-review-v130.json'),selected:ref(b+'part3-guided-actions-selected-execution-v84.json'),followupSelected:ref(b+'native-followup-selected-v126.json'),model:ref(src+'guided-teaching-model-v74.tsx'),focusModel:ref(src+'focus-analysis-model-v96.tsx'),runtime:ref(src+'guided-source-runtime-v132.tsx'),jobs:[{name,project,frames:cursor,audio:{path:audio,samples:cursor*400},output:folder+'/renders/'+name+'.mp4',execution:folder+'/renders/'+name+'.execution.json'}],scenes,palette:'research-black-v1',classification:'explanation',captionStyle:'boxed-white-forest-v1',captionsBurnedIntoSource:false,cpuThreads:2,gpuJobs:0,original111Regenerated:false,rendered:false,movingPixelsReviewed:false,finalMixedAsrApproved:false,uploaded:false});
console.log(JSON.stringify({independentScenes:5,frames:cursor,seconds:cursor/60,cues:scenes.reduce((n,s)=>n+s.cues.length,0),newImages:0,rendered:false}));
