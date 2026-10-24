"""Record observed publication and local delivery without inventing human review."""
import json, datetime, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
control_path=R/'shared/publishing/video-production-control.json'
work_path=R/'shared/publishing/shorts-worklist.json'
c=read(control_path); w=read(work_path); schedule=read(R/'production/batches/distinctive-shorts-20261024/publishing-schedule.json')
evidence_names=['titanfall-1080p60.png','superliminal-quality.png','ghost-quality.png','gears-quality.png','portal-quality.png']
for item,evidence in zip(schedule['items'],evidence_names):
 p=R/'projects'/item['slug']; receipt=read(p/'publishing/youtube-upload.json')
 assert receipt['schedule']['active'] and all(s['status']=='published-verified-in-studio' for s in receipt['subtitles'])
 proof='production/batches/distinctive-shorts-20261024/local/publishing-evidence/'+evidence
 assert (R/proof).exists()
 receipt['status']='scheduled';receipt['platformPlayback']={'observedAt':now,'qualityMenu':'1080p60 HD','evidence':proof,'wholePlaybackListeningClaimed':False,'selectableCcPlaybackPropagation':'not-yet-verified'}
 receipt['playlist']={'title':'도움이 되는 게임 개발 이야기','status':'saved-in-studio','verification':'Checked playlist, saved, observed all-changes-saved toast.'}
 receipt['thumbnail']={'status':'existing-generated-frame-retained','customFileUploaded':False,'reason':'Retain approved vertical Shorts frame with its headline; no new long-form illustration substituted in this task.'}
 receipt['shortsUnavailableElements']=['00:00 external card and long-form end-screen controls not offered in observed Shorts flow']
 receipt['remainingPlatformChecks']=['Selectable CC propagation in watch player','Automatic dubbed-audio drafts not listened to or published','Pinned comment waits for publication']
 receipt['fullSettings']=False;receipt['updatedAt']=now;save(p/'publishing/youtube-upload.json',receipt)
 item['status']='scheduled';item['settingsReceipt']=str((p/'publishing/youtube-upload.json').relative_to(R)).replace('\\','/')
 cp=read(p/'production/checkpoint.json');cp['youtube']={'status':'scheduled','videoId':receipt['videoId'],'url':receipt['url'],'schedule':receipt['schedule'],'receipt':item['settingsReceipt']};save(p/'production/checkpoint.json',cp)
 project=read(p/'project.json');project['status']='scheduled';save(p/'project.json',project)
 row=next(x for x in w['rows'] if x.get('slug')==item['slug'])
 row.update(status='scheduled',production='complete',review='accepted-for-upload-and-schedule',youtube=receipt['url'],youtubeState='scheduled',scheduledFor=item['requestedLocal'],publishingReceipt=item['settingsReceipt'],updatedAt=now)
 row['authorization']['status']='completed-local-delivery';row['publishingAuthorization']=schedule['id']
new=[]
for order,slug in enumerate(read(B/'batch.json')['authorization']['slugs'],6):
 p=R/'projects'/slug;d=read(p/'production/delivery.json');master=Path(d['files']['captioned']['path'])
 assert hashlib.sha256(master.read_bytes()).hexdigest()==d['files']['captioned']['sha256'] and d['technicalChecks']['status']=='pass'
 project=read(p/'project.json'); final=p/project['currentFinalDirectory']; qa=next(final.glob('qa-sequential-*'))
 review={'slug':slug,'masterSha256':d['files']['captioned']['sha256'],'version':d['masterVersion'],'checkedAt':now,
 'technical':'Full decode, exact 60 fps timestamps, 1080x1920, unchanged identical AAC, all caption bounds passed.',
 'visual':{'method':'Directly viewed all cue/join contact sheets; native frames and 375px-derived mobile layouts. Browser playback separately recorded.','sampleIndex':str((qa/'index.json').relative_to(R)).replace('\\','/'),'captionClearance':('Momentum v2 omits the redundant bottom note while preserving the main speed label and implementation chip.' if order==6 else 'Traversal v2 raises footer 40px above two-line captions; fixed caption position unchanged.'),'screenshotReference':'Synchronized observer/player views adopted; no third-party screenshot, character, audio or scene assets reused.'},
 'audio':{'sourceAndEncodedContinuity':'Analyzed; no sustained encoded attenuation found. Original PCM preserved.','asr':'Full voice/mix transcription and caption alignment checked; brief particle/adverb variants retained for listening.','humanWholeListening':False,'humanReview':'pending'},
 'decisions':['Use CPU/WARP capture and CPU voice; leave user Unity and unrelated jobs untouched.','Show one simulated body plus a rendering-only copy. Same pose and synchronized time; do not present as measured Valve internals.','Traversal cat appears only at the closing reaction to protect clipping explanation.','Use verified independent native 1080p60 Portal recording; commentary/reference media excluded.'],
 'remaining':['User full viewing and listening of this exact captioned file','Review marked quiet-speech contexts and short Korean ASR variants'],
 'platform':{'youtube':'not-uploaded','drive':'not-requested','schedule':'not-set'}}
 save(p/'production/review-ledger.json',review)
 cp=read(p/'production/checkpoint.json');cp['reviewLedger']=str((p/'production/review-ledger.json').relative_to(R)).replace('\\','/');save(p/'production/checkpoint.json',cp)
 row={'slug':slug,'title':d['title'],'batchOrder':order,'status':'local-review-ready','production':'complete','review':'human-final-review-pending','youtube':'not-uploaded','drive':'not-requested','delivery':str((p/'production/delivery.json').relative_to(R)).replace('\\','/'),'captionedSha256':d['files']['captioned']['sha256'],'updatedAt':now,'authorization':c['portalTraversalShortsAuthorization']['id']}
 existing=next((x for x in w['rows'] if x.get('slug')==slug),None)
 if existing:existing.update(row)
 else:w['rows'].append(row)
 new.append({'slug':slug,'durationSeconds':d['durationSeconds'],'sha256':d['files']['captioned']['sha256'],'captioned':str(master),'humanReview':'pending'})
schedule['sixthStatus']='complete-local-review-ready; actual human review pending';schedule['seventhSlug']='shorts-portal-seamless-traversal';schedule['seventhStatus']='complete-local-review-ready; production-only, not scheduled'
save(R/'production/batches/distinctive-shorts-20261024/publishing-schedule.json',schedule)
c['shortsPublishingBatchAuthorization']=schedule;c['portalTraversalShortsAuthorization'].update(status='completed-local-review-ready',completedAt=now,deliveries=new,fullProductionAuthorized=False)
save(control_path,c);w['updatedAt']=now;save(work_path,w)
save(B/'completion.json',{'completedAt':now,'scheduled':schedule['items'],'localReview':new,'driveChanged':False,'unrelatedSchedulesChanged':False,'humanReviewInferred':False})
print(json.dumps({'scheduled':5,'localReview':new},ensure_ascii=False))
