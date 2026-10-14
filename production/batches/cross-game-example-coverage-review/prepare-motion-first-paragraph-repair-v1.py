"""Prepare one verbatim held-paragraph candidate; retain all prior PCM and evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,copy,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
def save(p,x):
    assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
tts=read(R/'narration-tts-execution-v7.json');diag=read(R/'additions-diagnostic-contexts-execution-v1.json');alt=read(R/'first-paragraph-alternate-decode-v1.json')
assert tts['actualOuterExitCode']==0 and tts['researchResumeVerified']
assert diag['actualOuterExitCode']==0 and diag['completed']==15 and alt['exitCode']==0
assert alt['text'].count('퍼즐의')>10 and diag['results'][0]['text'].count('퍼즐의')>10
for x in tts['protectedInputs']+tts['results']:assert sha(ROOT/x['path'])==x['sha256']
first=read(R/'script/additions.ko.json')['scenes'][0]['lines'][0]
for lang in ['ko','en']:
    original=read(R/f'script/additions.{lang}.json')['scenes'][0]
    save(R/f'script/first-paragraph-repair.{lang}.json',dict(title=original['title'],status='verbatim-repair-candidate-only',scenes=[dict(id='07b-p01',title=original['title'],lines=[original['lines'][0]])]))
manifest=copy.deepcopy(read(R/'tts-manifest-v1.json'))
manifest['paths'].update(script=(R/'script/first-paragraph-repair.ko.json').relative_to(ROOT).as_posix(),scriptEn=(R/'script/first-paragraph-repair.en.json').relative_to(ROOT).as_posix())
manifest['tts'].update(outputDir='shared/output/narration/motion-sickness-games/cross-game-four-first-paragraph-repair-v1',filenameStem='motion-sickness-first-paragraph-repair-v1')
save(R/'tts-first-paragraph-repair-manifest-v1.json',manifest)
request=copy.deepcopy(read(R/'narration-tts-request-v1.json'))
request.update(total=1,paragraphs=1,manifest=(R/'tts-first-paragraph-repair-manifest-v1.json').relative_to(ROOT).as_posix(),
    scenes=[dict(id='07b-p01',path='shared/output/narration/motion-sickness-games/cross-game-four-first-paragraph-repair-v1/chunks/07b-p01-scene.wav',text=first)],
    purpose='Two bounded decoders and whole decoder did not recover the first Portal paragraph. Generate one shorter verbatim candidate; no adopted splice before actual current ASR review.',
    preserveHeldOriginalFirstParagraph=True,retainedExistingThreeScenePcm=True,newCandidateAdopted=False)
request['protectedInputs']+= [dict(path=x['path'],sha256=x['sha256']) for x in tts['results']]
save(R/'narration-first-paragraph-repair-request-v1.json',request)
wrapper=(B/'render-motion-four-additions-v7.py').read_text('utf-8')
for a,b in [
    ('narration-tts-execution-v7.json','narration-first-paragraph-repair-execution-v1.json'),
    ('narration-tts-session-v7.json','narration-first-paragraph-repair-session-v1.json'),
    ('narration-tts-waiting-v7.json','narration-first-paragraph-repair-waiting-v1.json'),
    ('narration-tts-request-v1.json','narration-first-paragraph-repair-request-v1.json'),
    ('voice-retry-resource-verification-v14.json','first-paragraph-repair-resource-v1.json'),
    ("request['total']==3 and request['paragraphs']==15","request['total']==1 and request['paragraphs']==1"),
    ("R/'tts-manifest-v1.json'","R/'tts-first-paragraph-repair-manifest-v1.json'"),
    ("R/'script/additions.ko.json'","R/'script/first-paragraph-repair.ko.json'"),
    ("R/'script/additions.en.json'","R/'script/first-paragraph-repair.en.json'"),
    ('total=3,results=[]','total=1,results=[]'),('assert len(state[\'results\'])==3','assert len(state[\'results\'])==1'),
    ('Three comparisons measured','One held-paragraph candidate measured'),('three-comparisons','first-paragraph-repair-candidate'),
    ('Prepared3newcomparisons/15pairedparagraphs','Prepared1verbatim-held-paragraph-candidate')]:wrapper=wrapper.replace(a,b)
dest=B/'render-motion-first-paragraph-repair-v1.py';assert not dest.exists();dest.write_text(wrapper,'utf-8')
verifier=(B/'verify-motion-four-voice-resume-v7.py').read_text('utf-8')
for a,b in [('narration-tts-session-v7.json','narration-first-paragraph-repair-session-v1.json'),('narration-tts-execution-v7.json','narration-first-paragraph-repair-execution-v1.json'),('research-handoff-verification-v7.json','first-paragraph-repair-handoff-verification-v1.json'),("expected_ids={'07b','08b','11b'}","expected_ids={'07b-p01'}"),("state['total']==3 and len(state['protectedInputs'])==68","state['total']==1 and len(state['protectedInputs'])==71"),("len(state['results'])==3","len(state['results'])==1"),('allThreeCurrentPcmHashesMatched','allCandidatePcmHashesMatched'),('all68ProtectedInputsMatched','all71ProtectedInputsMatched')]:verifier=verifier.replace(a,b)
dest=B/'verify-motion-first-paragraph-repair-resume-v1.py';assert not dest.exists();dest.write_text(verifier,'utf-8')
save(R/'additions-whole-and-diagnostic-held-review-v1.json',dict(schemaVersion=1,reviewedAt=now,
    actualWholeSession=59538,actualWholeExitCode=0,actualDiagnosticSession=41620,actualDiagnosticExitCode=0,actualAlternateSession=24172,actualAlternateExitCode=0,
    allThreeWholeRecognizedTextsDirectlyCompared=True,all15DiagnosticRecognizedTextsDirectlyCompared=True,
    wholeProofSha256=sha(R/'additions-whole-asr-execution-v1.json'),diagnosticProofSha256=sha(R/'additions-diagnostic-contexts-execution-v1.json'),alternateProofSha256=sha(R/'first-paragraph-alternate-decode-v1.json'),
    heldParagraph='07b-p01',reason='Whole and two bounded decoders return repeated 퍼즐의 rather than the requested first paragraph. No source text was supplied as recognizer prompt, no anti-repetition suppression used. This is a failed recognizability gate; actual acoustic cause is not asserted.',
    remaining14ContextTexts='Directly compared.08b game-name resolved in its bounded context;07b-p03 앞에/앞의 and11b-p01 내/네,새/세,화면에/화면의 are recorded pronunciation/recognition alternatives, with human pronunciation pending.',
    provisionalBoundaryScope='Quiet-valley estimated spans produced recognizable sentence contexts except first. No all-boundary or whole continuous-listening approval.',
    currentUnmixedAudioApproved=False,finalMixedAsrApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,
    original14PcmRegenerated=0,existingThreePcmOverwritten=0,newRepairCandidateAdopted=False))
print('Prepared one verbatim held-first-paragraph candidate. All original14 and three newly measured scene PCM retained; no model or GPU request.')
