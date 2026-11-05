"""Point the exact ten records at verified feedback masters. Keep baseline evidence labeled as prior."""
from build import *
import importlib.util,sys
R2='final-reviewed-feedback-nov05-r2';REV='feedback-20261105'
EN_TITLES=['The Bottle Tilts. How Does the Water Stay Level? | Half-Life: Alyx','How Filming Footprints from Under the Snow Makes a Dent | Batman: Arkham Origins','How Do Games Keep the Sea Outside a Floating Ship? | Sea of Thieves','How Games Create the Illusion of Endless Flight | Uncharted 3','How Games Depict Unstable Rope Physics | Uncharted 4','Why StarCraft Lets Gathering Workers Slip Past Other Units','The Bridge Is Diagonal. What Path Do StarCraft Units See?','Why Did Blizzard Bring Back Custom Maps It Had Blocked?','Why Do StarCraft II Marines Gradually Fire Out of Sync?','StarCraft II Replays Save the Order of Commands Instead of the Screen']
def update(path,change):
    x=read(path);change(x);save(path,x)
def evidence(row):
    path=Path(row['finalDirectory']).parent/R2;d=read(path/'delivery.json');qa=read(path/'feedback-check.json')
    files={f['name']:{k:v for k,v in f.items() if k!='name'} for f in d['files']}
    assert all(sha(path/k)==v['sha256'] for k,v in files.items()) and qa['master']==files['captioned.mp4']['sha256']
    ev=dict(masterSHA256=qa['master'],finalDirectory=str(path),deliveryPath=str(path/'delivery.json'),deliverySHA256=sha(path/'delivery.json'),technicalEvidence=str(path/'feedback-check.json'),sampledVisualStatus='pass-at-sampled-times',fullListening='pending',fullRealtimePlayback='pending',humanFinalReview='pending')
    if d['additionFrames']:
        idx=row['order'];pinfile=WORK/f'{idx:02}-r2'/'voice-files.json';pin=read(pinfile) if pinfile.exists() else {}
        takes=[]
        for j in (1,2):
            wav=Path(pin[str(j)]['path']) if pin else ROOT/f'shared/output/tech-ten-feedback-nov05/extra-speech/chunks/{idx:02}-{j:02}.wav'
            digest=sha(wav);record=WORK/'speech-check'/f'{idx:02}-{j:02}-{digest[:12]}.json';asr=read(record);assert asr['sha256']==digest
            takes.append(dict(sha256=digest,rawRecognition=asr['rawRecognition'],evidence=str(record)))
        ev['additionalNarrationASR']=takes
        if idx==2:
            cues=srtread(path/'captions.ko.srt');timecode=next(a for a,b,s in cues if '각 점에서' in s.replace('\n',' '))
            ev['listenAtSeconds']=round(timecode,2);ev['listeningNote']='추가 문장의 ‘높이맵’을 자동 인식은 ‘높임맵’으로 표기. 실제 발음은 청취 확인 전.'
    final=dict(directory=str(path),fourOutputsVerified=True,reviewFilesGenerated=True,presentOutputNames=FILES,issues=[],files=files,masterSHA256=qa['master'],reviewPage=str(path/'index.html'),delivery=str(path/'delivery.json'))
    return d,qa,ev,final
def worklist(w):
    for r,e in zip(BASE,ED):
        d,q,ev,f=evidence(r);row=next(x for x in w['rows'] if x.get('slug')==r['slug'])
        row.update(title=d['title'],status='local-feedback-reviewed-samples',production='complete-local-files',humanReview='pending',review='Revised local masters; sample inspection complete; full listening and human approval pending.',technicalReview=dict(width=1080,height=1920,fps=60,decodedBoth=True,audioPairMatched=True,captionBounds=True),currentFinalEvidence=ev)
    return w
def main():
    if len(sys.argv)>1:
        src,out=sys.argv[1:];save(out,worklist(read(src)));return
    selected=[];batchfile=HERE.parent/'batch.json';cpfile=HERE.parent/'checkpoint.json'
    batch=read(batchfile);checkpoint=read(cpfile)
    for r,e,item,bcp in zip(BASE,ED,batch['projects'],checkpoint['projects']):
        slug=r['slug'];p=ROOT/'projects'/slug
        d,q,ev,final=evidence(r)
        assert (Path(final['directory'])/'visually-inspected.txt').is_file(),'inspect actual frame sheets before adoption'
        manifest=p/'project.json';meta=p/'publishing/metadata.json';pc=p/'production/checkpoint.json';led=p/'production/review-ledger.json';cfg=p/'production/visual-config.json'
        publication=read(meta);publication.update(title=d['title'],englishTitle=EN_TITLES[e['n']-1],description=d['description'],revision=REV,humanFinalReview='pending');save(meta,publication)
        m=read(manifest);m.update(currentRevision=REV,currentVisualVersion=REV,title=d['title'],currentFinalDirectory='production/local/'+R2,status='local-final-review-pending')
        for k,name in zip(['videoClean','videoBurnedCaptions','captionsKo','captionsEn','localReview'],[*FILES,'index.html']):m['paths'][k]=f'projects/{slug}/production/local/{R2}/{name}'
        m['paths']['feedbackEdit']=(HERE/'edit.json').relative_to(ROOT).as_posix();save(manifest,m)
        cfgdata=read(cfg);cfgdata['head']=e['head'];save(cfg,cfgdata)
        h=read(led);h.update(revision=REV,status='local-feedback-reviewed-samples',technicalChecks='pass',actualCompleteHumanListening=False,visualPlaybackReview='pending',humanFinalReview='pending',currentTechnicalReview=ev)
        h['sampleVisualReviews']=[a for a in h.get('sampleVisualReviews',[]) if a.get('masterSHA256')!=q['master']]+[dict(revision=REV,masterSHA256=q['master'],sampleTimes=q['sampleTimes'],sheet=q['sampleSheet'],sheetSHA256=q['sampleSheetSha256'],status='passed-sampled-visual-review')]
        save(led,h)
        cur=read(pc);cur.update(revision=REV,status='local-feedback-reviewed-samples',productionStatus='complete-local-files',humanFinalReview='pending',generatedReviewVideo=True,finalOutputs=final,sampledFinalEvidence=ev,feedbackRevision=dict(baseMaster=r['masterSha256'],selection=e,additionFrames=d['additionFrames'],newEvidence=q,actualFullListening=False));save(pc,cur)
        for o in (item,bcp):
            o.setdefault('originalTitle',r['title']);o.update(title=d['title'],revision=REV,status='local-feedback-reviewed-samples')
        bcp.update(finalOutputs=final,sampledFinalEvidence=ev,actualFullListeningRecorded=False,humanFinalReview='pending',reviewEvidenceSource=str(led))
        checkpoint['currentFinalEvidence'][slug]=ev
        selected.extend(str(f.relative_to(ROOT).as_posix()) for f in (meta,manifest,pc,led,cfg))
    save(batchfile,batch)
    work=ROOT/'shared/publishing/shorts-worklist.json';save(work,worklist(read(work)))
    x=sp.check_output([sys.executable,'-X','utf8',str(HERE.parent/'build-review-overview.py'),'--require-all'],text=True,encoding='utf8')
    report=json.loads(x);checkpoint.update(status='all-ten-feedback-revisions-local-review-pending',revision=REV,humanFinalReview='pending',generatedReviewVideos=10,localReviewCollection=dict(page=report['index'],snapshot=report['snapshot'],snapshotSHA256=sha(Path(report['snapshot'])),verifiedFinalCount=10),feedbackEdit=(HERE/'edit.json').relative_to(ROOT).as_posix())
    save(cpfile,checkpoint);selected.extend(f.relative_to(ROOT).as_posix() for f in (batchfile,cpfile,HERE.parent/'build-review-overview.py'))
    save(WORK/'git-include.json',selected);print(x)
if __name__=='__main__':main()
