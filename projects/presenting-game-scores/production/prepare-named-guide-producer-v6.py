"""Prepare one-item owned-boundary producer and guarded review helpers only."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rp=BASE/'named-guide-tts-request-v6.json';r=read(rp);assert len(r['scenes'])==1
assert read(BASE/'named-guide-paired-direct-review-v6.json')['allKoEnDirectlyRead']
r.update(pairedWholeTextReview=True,overviewPromiseReview=True,
 scriptReview='projects/presenting-game-scores/production/paired-script-direct-review-v1.json',
 manifestOverride=r['manifest'])
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
mapping={
 'localized-voice-repair-tts-execution-v4.json':'named-guide-tts-execution-v6.json',
 'localized-voice-repair-tts-request-v4.json':'named-guide-tts-request-v6.json',
 'localized-voice-repair-tts-session-v4.json':'named-guide-tts-session-v6.json',
 'localized-voice-repair-tts-waiting-v4.json':'named-guide-tts-waiting-v6.json',
 'localized-voice-repair-resource-v4.json':'named-guide-resource-v6.json',
 'render-localized-voice-repair-v4.py':'render-named-guide-v6.py',
 'localized-voice-repair-research-resume-verification-v4.json':'named-guide-research-resume-verification-v6.json'
}
def transform(text):
 for old,new in mapping.items():text=text.replace(old,new)
 return text
def newfile(name,text):
 p=BASE/name;assert not p.exists();p.write_text(text,'utf-8')
producer=transform((BASE/'render-localized-voice-repair-v4.py').read_text('utf-8-sig'))
producer=producer.replace('Two localized exact-text takes; completed11 candidate PCM and original10 PCM are preserved; original10 PCM scenes are immutable inputs.',
 'One rephrased unapproved named-metric guide; preserve all original10, candidate11 and localized2 PCM.')
producer=producer.replace("len(request['scenes'])==2","len(request['scenes'])==1").replace('total=2','total=1').replace("len(state['results'])==2","len(state['results'])==1")
producer=producer.replace('Prepared2 full exact-text localized takes only','Prepared one complete independently rephrased named-field guide only')
producer=producer.replace('single-localized-voice-repair-voice-measurement-v4','single-named-guide-voice-measurement-v6')
producer=producer.replace('localized-voice-repair-measured-awaiting-full-ASR-and-research-resume-verification','named-guide-measured-awaiting-full-ASR-and-research-resume-verification-v6')
needle="sys.path.insert(0,str(ROOT/'qwen3-tts'))\nfrom gpu_tts_hold"
assert needle in producer
producer=producer.replace(needle,"for name in ['localized-voice-repair-whole-asr-execution-v4.json','localized-voice-repair-contexts-asr-execution-v4.json','localized-decoding-asr-execution-v5.json']:\n    completed=read(BASE/name)\n    assert completed['exitCode']==0 and completed['actualExitObserved'],name\nassert read(BASE/'named-guide-paired-direct-review-v6.json')['allKoEnDirectlyRead']\n"+needle)
newfile('render-named-guide-v6.py',producer)
session=transform((BASE/'record-localized-voice-repair-session-v4.py').read_text('utf-8-sig'))
session=session.replace('existing two-item coordinator wait','existing one-guide coordinator wait').replace('localized-two-voice-cooperative-boundary-wait-v4','named-guide-cooperative-boundary-wait-v6')
start=session.index("action='");end=session.index("\ncp.update",start)
session=session[:start]+"action='Observe actual one-guide successor first. Complete the current research checkpoint/validation/done boundary, then own coordinator synthesizes only24-observe-named-fields-clear-start and restores original command/cwd on success/failure. After actual outer exit verify own restoration and fresh resources, whole1 and complete independent/semantic context review. Preserve original10+candidate11+localized2 PCM and all54+4 diagnostic windows. Final measured timing/mix/pixels/pair/collection/private remain false.'"+session[end:]
newfile('record-named-guide-session-v6.py',session)
verify=transform((BASE/'verify-localized-voice-repair-research-resume-v4.py').read_text('utf-8-sig'))
verify=verify.replace("len(state['results'])==state['total']==2","len(state['results'])==state['total']==1").replace('allTwoLocalizedPcmHashesMatched','allOneGuidePcmHashesMatched').replace('Actual two-item localized voice exit0','Actual one-guide voice exit0')
newfile('verify-named-guide-research-resume-v6.py',verify)
asr=transform((BASE/'review-localized-voice-repair-v4.py').read_text('utf-8-sig'))
asr=asr.replace('One CPU2 worker for2 complete unadopted localized takes','One CPU2 worker for one complete unadopted named-field guide')
asr=asr.replace("choices=['whole', 'contexts', 'targets']","choices=['whole', 'contexts']")
asr=asr.replace('localized-voice-repair-{args.mode}-asr-execution-v4','named-guide-{args.mode}-asr-execution-v6').replace('localized-voice-repair-{args.mode}-asr-v4','named-guide-{args.mode}-asr-v6')
asr=asr.replace('localized-voice-repair-whole-asr-execution-v4.json','named-guide-whole-asr-execution-v6.json')
asr=asr.replace('localized-voice-repair-targeted-context-plan-v4.json','named-guide-targeted-context-plan-v6.json').replace('localized-voice-repair-independent-context-plan-v4.json','named-guide-independent-context-plan-v6.json')
asr=asr.replace('localized-voice-repair-v4.ko.json','named-guide-repair-v6.ko.json').replace('localized-voice-repair-v4.en.json','named-guide-repair-v6.en.json')
asr=asr.replace("len(tts['results']) == 2","len(tts['results']) == 1").replace("len(script['scenes']) == 2","len(script['scenes']) == 1").replace("sum(len(x['lines']) for x in script['scenes']) == 2","sum(len(x['lines']) for x in script['scenes']) == 1")
asr=asr.replace('localized-two-voice-{args.mode}-CPU-ASR-v4','named-guide-{args.mode}-CPU-ASR-v6')
assert "whisper-large-v3-turbo" in asr
newfile('review-named-guide-v6.py',asr)
recorder=(BASE/'record-localized-asr-session-v4.py').read_text('utf-8-sig').replace('localized-voice-repair-{args.mode}-asr-execution-v4','named-guide-{args.mode}-asr-execution-v6').replace('review-localized-voice-repair-v4.py','review-named-guide-v6.py')
newfile('record-named-guide-asr-session-v6.py',recorder)
print('Prepared one-guide producer/session/resume/full-context ASR helpers; model0/GPU0. Existing producers unchanged.')
