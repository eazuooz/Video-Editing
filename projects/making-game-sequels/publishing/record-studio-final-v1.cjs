// Close only the actual saved/read-back platform checks, keeping human review pending.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/making-game-sequels/',pub=base+'publishing/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const text=p=>fs.readFileSync(path.join(root,p),'utf8');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now=new Date().toISOString(),r=read(pub+'youtube-upload.json');
if(r.actualVideoId!=='DWsAfi-fUKw'||!r.privateSaved||!r.burnedCaptionVerification.verified)throw Error('Actual private reviewed upload required');
const additional=['studio-no-claims.ax.txt','studio-ads-final.ax.txt','studio-content-complete.ax.txt','studio-korean-published.ax.txt','studio-advanced-saved.ax.txt'];
const claims=text(pub+additional[0]),ads=text(pub+additional[1]),content=text(pub+additional[2]),ko=text(pub+additional[3]),advanced=text(pub+additional[4]);
if(!claims.includes('동영상에서 소유권 주장이 발견되지 않았습니다')||!claims.includes('동영상에서 저작권 보호 콘텐츠가 발견되지 않았습니다'))throw Error('No-claim result missing');
if(!ads.includes('generic: 사용')||!ads.includes('미드롤 광고 게재" [checked]')||ads.includes('검사 중'))throw Error('Actual advertising state not ready');
if(!content.includes('/video/DWsAfi-fUKw/edit')||!content.includes('cell "—"')||!content.includes('cell "비공개"')||!content.includes('1개 중 1~1'))throw Error('Actual single private/no-alert content row missing');
if(!ko.includes('수동 자막')||!ko.includes('게시됨'))throw Error('Manual Korean published readback missing');
for(const s of ['아니요, 아동용이 아닙니다" [checked]','아니요, 동영상에 유료 프로모션이 포함되어 있지 않습니다." [checked]','예, AI가 사용되었습니다." [checked]','라이선스 표준 YouTube 라이선스','button "교육"','making-game-sequels.captioned.mp4','img "고화질 완료"','generic: 비공개'])if(!advanced.includes(s))throw Error('Saved advanced setting missing '+s);
r.platformCheckHistory=[{status:'pending',observedMessage:r.monetization.observedMessage}];
Object.assign(r,{status:'private-saved-settings-verified-human-review-pending',observedAt:now,fullSettingsVerified:true,automaticChecksVerified:true,productionGitDelivery:'pending-actual-normal-push'});
r.subtitles.ko.published=true;
Object.assign(r.monetization,{automaticAdSuitability:'checked; ads enabled and initial check/alert no longer present',automaticCopyright:'complete-no-claims',observedMessage:'Saved no-claims overview, no protected content found, advertising enabled with checked midroll, and current single private content row has no alert. No numeric suitability score was observed.',numericAdSuitabilityResultObserved:false,verifiedAt:now});
r.advancedSettings={savedAndReopened:true,notForKids:true,paidPromotion:false,aiDisclosure:true,language:'ko',category:'Education',license:'Standard YouTube License',evidence:pub+'studio-advanced-saved.ax.txt'};
for(const n of additional){const p=pub+n;r.evidence.push({path:p,sha256:sha(p)});}
write(pub+'youtube-upload.json',r);
const recipe=read(pub+'thumbnail-recipe.json');recipe.gitEssentialReview='approved exact image path and SHA256 in shared/git-essential-images.json';write(pub+'thumbnail-recipe.json',recipe);
const qPath='production/batches/sakurai-planning-game-design/queue.json',q=read(qPath),item=q.items.find(i=>i.slug==='making-game-sequels');
Object.assign(item,{status:'in-progress',stage:'private-settings-verified-git-delivery-pending',updatedAt:now,nextAction:'Selectively commit/push reviewed final-v2 production and actual single private settings from actual shared HEAD; preserve foreign staged/worktree edits. Then continue familiar-game-rules full-content duplicate review.'});
item.finalReview.fullSettingsVerified=true;item.finalReview.automaticChecksVerified=true;
Object.assign(item.execution,{observedAt:now,status:'all-production-workers-closed-private-settings-verified-selective-git-next'});
for(const k of ['rendered','collected','uploaded','productionRendered','productionCollected','privateSaved','fullSettingsDelivered'])q.progress[k]=12;
q.updatedAt=now;q.lastProgressAt=now;write(qPath,q);
for(const p of [base+'production/latest-checkpoint.json','production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']){const d=read(p);Object.assign(d,{stage:item.stage,updatedAt:now,nextAction:item.nextAction,execution:item.execution});d.finalReview.fullSettingsVerified=true;d.finalReview.automaticChecksVerified=true;write(p,d);}
const manifest=read(base+'project.json');manifest.status='private-saved-settings-verified-human-review-pending';manifest.finalProduction.fullSettingsVerified=true;manifest.finalProduction.publishReady=false;write(base+'project.json',manifest);
console.log(JSON.stringify({actualVideoId:r.actualVideoId,private:true,schedule:null,fullSettingsVerified:true,platformChecks:'actual no-claims/no-alert/ads-enabled readback',humanReview:'pending',git:'pending'}));
