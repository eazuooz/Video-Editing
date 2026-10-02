const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>{fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true});fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');};
const evidence='과외에는 링크 걸어주고 영상 마지막에 항상 걸어줘 그리고 또 고정댓글로 달아줘 ... 영상제작 진행해줘 자막은 항상 가운데 아래로 해주고 이규칙은 영상제작 규칙에 추가해서 업데이트해줘';
const d=read('shared/publishing/youtube-defaults.json');
d.approvedAt='2026-10-02';
Object.assign(d.coaching,{requestedAvailability:'description-and-ending-plus-pinned-comment',endingRequired:true,endingType:'external-link-end-screen',alsoInPinnedComment:true,latestUserEvidence:evidence,platformConstraint:'Card teasers are hidden during end screens. Use an external-link end-screen element when available; record actual account/platform limitations.'});
d.endScreen.elements=Array.from(new Set([...d.endScreen.elements,'programming-coaching-external-link']));
d.pinnedComment={required:true,language:'ko',textFile:'projects/<slug>/publishing/pinned-comment.ko.txt',url:d.coaching.url,postAs:'own-channel',pin:true,privateVideoPolicy:'prepare-text-only; pending-video-publication; never-change-privacy-to-comment',requireActualCommentIdAndPinnedEvidence:true};
d.subtitles.burnedCaptionPlacement={anchor:'bottom-center',centerPx:[960,970],referenceResolution:[1920,1080],motionCanvasCenter:[0,430],applyTo:'all-narrated-footage-and-explanation-scenes',doNotRelocateToAvoidOverlap:true,overlapRemedy:'recompose-footage-or-split-cues',playerSrtPosition:'viewer-controlled'};
d.verification=Array.from(new Set([...d.verification,'coaching-ending-link-saved-or-actual-platform-limit-recorded','pinned-coaching-comment-or-pending-private-video-recorded','all-burned-captions-bottom-center']));
write('shared/publishing/youtube-defaults.json',d);
for(const p of ['templates/video-project/project.json','projects/blank-project-coding/project.json']){
 const m=read(p);Object.assign(m.editing.captionStyle,{placement:d.subtitles.burnedCaptionPlacement,placementApprovedAt:'2026-10-02',placementApprovalEvidence:evidence});
 m.publishing={...m.publishing,coachingEndingLinkRequired:true,pinnedCoachingCommentRequired:true,defaults:'shared/publishing/youtube-defaults.json'};
 if(p.includes('blank-project-coding')){
  m.status='production';m.requestedStage='complete-production-through-private-upload';
  Object.assign(m.approvals,{script:'approved-to-produce-2026-10-02',scriptEvidence:evidence,voiceSample:'reuse-existing-approved-Qwen-reference-under-same-method-request; new-full-listening-pending',backgroundMusic:'reuse-existing-approved-Nimbus-under-same-method-request',translation:'in-progress',broll:'building-new-owned-development-captures'});
  const previous=read('projects/game-writing/project.json');m.audio.backgroundMusic={...previous.audio.backgroundMusic,reuseBasis:'User requested same established video method; docs/VIDEO_ADDITIVE_REVISION.md channel-approved Qwen/Nimbus format',originalAssetVerification:'pending; preserve prior restored-copy provenance'};
  Object.assign(m.production,{currentStage:'owned-examples-and-recording',nextStage:'source-review-and-narration',authorizationDate:'2026-10-02',authorizationEvidence:evidence});
  m.publishing.pinnedCommentStatus='pending-video-publication';m.publishing.endingLinkStatus='pending-video-upload';
  m.editing.coaching.endingRequired=true;m.editing.coaching.pinnedCommentRequired=true;
 }
 write(p,m);
}
const script=read('projects/blank-project-coding/script/narration.ko.json');script.status='approved-to-produce';
script.scenes.find(s=>s.id==='33').lines[2]='설명란과 영상 마지막, 고정댓글에 코칭과 과외 링크를 남겨두겠습니다. 지금 배우는 내용과 직접 만들어본 코드, 그리고 어디에서 막혔는지를 정리해보세요. 어떤 도움이 필요한지부터 구체적으로 이야기할 수 있습니다.';
write('projects/blank-project-coding/script/narration.ko.json',script);
const review='projects/blank-project-coding/script/narration.review.md';let t=fs.readFileSync(path.join(root,review),'utf8');t=t.replace('설명란에 코칭과 과외 링크를 남겨두겠습니다.','설명란과 영상 마지막, 고정댓글에 코칭과 과외 링크를 남겨두겠습니다.');fs.writeFileSync(path.join(root,review),t);
const comment='강의를 따라 할 때는 이해되는데, 빈 프로젝트에서는 어디서부터 시작할지 막막하신가요?\n직접 만들어본 코드와 막힌 지점을 바탕으로 공부 방향을 잡고 싶다면 얌얌코딩 프로그래밍 코칭·과외 안내를 확인해보세요.\n\n▶ 프로그래밍 코칭·과외\n'+d.coaching.url+'\n\n오늘은 배운 기능 하나를 골라, 정답을 닫고 직접 만들어보세요.\n';
fs.mkdirSync(path.join(root,'projects/blank-project-coding/publishing'),{recursive:true});fs.writeFileSync(path.join(root,'projects/blank-project-coding/publishing/pinned-comment.ko.txt'),comment);
write('projects/blank-project-coding/production/checkpoint.json',{updatedAt:new Date().toISOString(),stage:'example-development',rulesUpdated:true,scriptApproved:true,narrationGenerated:false,footageCaptured:false,rendered:false,privateUploadSaved:false,pinnedComment:{status:'prepared-pending-video-publication',reason:'YouTube private videos do not support comments',source:'https://support.google.com/youtube/answer/157177?hl=en'},remaining:['capture-and-review-real-development-actions','KO/EN-narration-and-ASR','measured-60:40-and-34-independent-scenes','render-and-QA','collect-four-deliverables','private-upload-and-platform-settings','media-check-rebuild-check-commit-push']});
console.log('Rules, authorization, ending CTA and pending private-video comment updated.');
