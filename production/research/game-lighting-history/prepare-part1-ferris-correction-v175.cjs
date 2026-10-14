// Prepare a single source-wording correction without changing the live batch.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production',s='projects/game-lighting-history-04/script';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,j)=>{if(fs.existsSync(path.join(root,p)))throw Error('Preserve '+p);fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');};
const original=s+'/physical-part1-guided-actions.koen.v169.json',script=read(original),scene=script.scenes.find(x=>x.id==='shadow-wheel-surface');
const before={ko:scene.ko,en:scene.en,focus:scene.focus};
if(!scene.ko.startsWith('바퀴와 차체 주변으로 카메라가 이동합니다.'))throw Error('Changed original wording');
scene.ko=scene.ko.replace('바퀴와 차체 주변으로 카메라가 이동합니다. 먼저 바퀴의 표면과 그 아래 그림자를 따로 잡아 보세요.','대관람차 주변으로 카메라가 이동합니다. 먼저 대관람차 구조물과 그 아래 그림자를 따로 잡아 보세요.');
scene.en=scene.en.replace('As the camera moves around the wheel and body, identify the wheel surface and its shadow separately.','As the camera moves around the Ferris wheel, identify its structure and its shadow separately.');
scene.focus='Red outline follows the Ferris-wheel structure; teal follows its ground shadow. No car, tyre-ground contact, cache hit or measured invalidation is claimed.';
script.preparedAt=new Date().toISOString();script.sourceWordingRevision='v175: Ferris wheel instead of car body; live v169 files remain immutable';
write(s+'/physical-part1-guided-actions.koen.v175.json',script);
const correction={id:scene.id,title:scene.id,lines:[scene.ko],screenRole:scene.role};
for(const language of ['ko','en'])write(s+`/physical-part1-ferris-correction.${language}.v175.json`,{title:'대관람차 실제 대상 명칭 정정',scenes:[{...correction,lines:[scene[language]]}]});
const board='production/research/game-lighting-history/local/part1-native-review-v166/samples/shadow-moving-wheel/board-01.png';
write(b+'/part1-ferris-wording-direct-review-v175.json',{reviewedAt:new Date().toISOString(),source:{path:'production/research/game-lighting-history/local/episode04-additional-action-v47/vsm-initial-editor-goldcoast2024.mp4',sha256:'d6b2cc2f1a45490b08f1c7834a4bfb20fc19f1be30a62e5b0ee09d834b6ba210'},board:{path:board,sha256:sha(board),directlyRead:true},browserObservation:{browser:4,tab:62,nativeClocks:[108,136.042,183.584,110.8,111.8],visible:'Updates lecture card at108/110.8/111.8; moving camera and Ferris-wheel structure and ground shadow at136.042/183.584. No car shown.',nominalDraftStart112NotYetApproved:true},sceneId:scene.id,before,after:{ko:scene.ko,en:scene.en,focus:scene.focus},fullPairedCorrectionDirectlyCompared:true,original111AndFiveFramingChanged:false,other36GuidesChanged:false,liveTtsInputsChanged:false,singleCorrectionTtsStarted:false,scope:'Render only this corrected guide after the current37 batch has ended and its exclusive lease has been released; retain all historical takes and all other valid takes.',wholeAsrApproved:false,finalMixedAsrApproved:false,allFinalPixelsReviewed:false,uploaded:false});
console.log('Prepared one Ferris-wheel wording repair; no TTS or live input mutation.');
