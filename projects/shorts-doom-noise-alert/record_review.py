"""Record the daily selection once, with exact local review artifacts and no platform changes."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from compose import FINAL, MEDIA, RAW, WORK, PROJECT, ROOT, PLAN, ed
DATE=PLAN['dateKst']
def audio_hash(path):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a','-c:a','copy','-f','hash','-hash','SHA256','-'],text=True).strip()
def worklist(obj):
    slug=PLAN['slug']
    d=ed.read(FINAL/'delivery.json');sha=d['files'][1]['sha256']
    row=dict(order=max((r.get('order',0) for r in obj['rows'] if r.get('slug')!=slug and isinstance(r.get('order'),int)),default=0)+1,
             slug=slug,title=d['title'],status='ready-for-local-final-review',production='complete-local-files',productionDateKst=DATE,
             authorization='daily-five-topics-one-short-v2',humanReview='pending',checkpoint=(PROJECT/'checkpoint.json').relative_to(ROOT).as_posix(),
             review='Encoded mobile samples, native FHD and matching audio checked. Full human listening pending.',platform='local-only',youtube=False,drive=False,scheduled=False,published=False,
             currentFinalEvidence=dict(masterSHA256=sha,finalDirectory=str(FINAL),deliveryPath=str(FINAL/'delivery.json'),fullListening='pending',humanFinalReview='pending'))
    obj['rows']=[r for r in obj['rows'] if r.get('slug')!=slug]+[row]
    earlier=obj.get('dailyProduction')
    if earlier and earlier.get('dateKst')!=DATE:
        history=obj.setdefault('dailyProductionHistory',[])
        if earlier not in history:history.append(earlier)
    obj['dailyProduction']=dict(dateKst=DATE,project=slug,status='local-review-ready',candidates=PLAN['candidates'],selected=PLAN['choice'],next='Actual user review of this master on the local review page.',masterSha256=sha)
    return obj
def main():
    d=ed.read(FINAL/'delivery.json');qa=ed.read(FINAL/'technical-review.json');player=ed.read(FINAL/'player-check.json');master=d['files'][1]['sha256']
    assert player['masterSha256']==qa['masterSha256']==master
    previous=MEDIA/'final-reviewed-v1'
    ident=audio_hash(FINAL/'captioned.mp4')
    assert ident==audio_hash(previous/'captioned.mp4')
    asr=ed.read(previous/'asr.json');asr.update(masterSha256=master,recognitionSourceMaster=asr['masterSha256'],matchingEncodedAudioHash=ident)
    ed.save(FINAL/'asr.json',asr)
    evidence=dict(freedoomVersion='0.13.0',engine='ViZDoom 1.3.2, software renderer, native 1920×1080 at 35 game tics/second',
                  sourceFiles=ed.read(PROJECT/'source-footage.json'),actualOpening='Stock MAP04, wait/fire; directly inspected in footage before writing the script.',
                  customMapNote='Original teaching rooms are separately identified. Real game simulation in both variants; only second linedef blocksound differs.',
                  runComparison=qa['gameplay'],bgm=ed.sha(ROOT/'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.mp3'),
                  rights={'freedoomLicense':'https://github.com/freedoom/freedoom/blob/v0.13.0/COPYING.adoc','musicCreditFile':'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.LICENSE.md','cat':'shared/assets/branding/cat-reactions-v1/provenance.json'},
                  voice=dict(model='Qwen3-TTS 1.7B',source='same approved Korean reference',inputs=ed.read(WORK/'timing.json'),mixRecognition=asr['segments']),
                  sampleChecks=['Actual camera at 1st attack and quiet match','Source-target circles with visibility from the game label buffer','Zoomed one/two flag comparison at the same tick','Caption and cat clear of the target at mobile width'])
    ed.save(PROJECT/'evidence.json',evidence)
    port=(MEDIA/'review-port.txt').read_text().strip();review=f'http://127.0.0.1:{port}/'
    project=ed.read(PROJECT/'project.json');project.update(currentRevision=d['revision'],status='ready-for-local-final-review',currentFinalDirectory=str(FINAL),currentFinalMaster=master)
    ed.save(PROJECT/'project.json',project)
    cp=dict(revision=d['revision'],selectedOnKst=DATE,status='local-final-review-pending',reviewPage=review,outputFolder=str(FINAL),
            completeCaptioned=str(FINAL/'captioned.mp4'),title=d['title'],description=d['description'],sha256=master,outputs=d['files'],
            actualChecks=['original native FHD source and controlled game capture inspected','both video streams decoded in full','audio stream and subtitles checked','375px samples inspected','real browser play and seek','independent encoded mix ASR'],
            remaining=['full human listening','full real-time viewing','user final review'],platformActions=False)
    ed.save(PROJECT/'checkpoint.json',cp)
    w=ROOT/'shared/publishing/shorts-worklist.json';ed.save(w,worklist(ed.read(w)))
    print(json.dumps(dict(review=review,sha256=master,seconds=d['durationSeconds']),ensure_ascii=False))
if __name__=='__main__':main()
