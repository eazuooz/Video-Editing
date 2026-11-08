"""Prepare only source-verified changed game passages; never regenerate a body."""
from pathlib import Path
import json,hashlib,copy
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def main():
    control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert control['fullLocalProductionAuthorized'] and control['candidateUserApproval']['text']=='이 목록으로 진행'
    plan=read(H/'narration/revisions.json');script={'scenes':[]};evidence=[]
    for ep in plan['episodes']:
        assert ep['id'] in control['episodes'] and ep['id']!='A03'
        assert ep['sourceVerified'] and ep['completeKoEnReadThrough']
        P=R/'projects'/ep['slug'];old={lang:read(P/f'production/relations-v4/final.{lang}.json') for lang in ['ko','en']}
        new=copy.deepcopy(old);changed={c['id']:c for c in ep['changes']}
        assert len(changed)==len(ep['changes'])
        for c in ep['changes']:
            assert c['sourceVerified'] and (R/c['evidence']).is_file()
            key=ep['id']+'S'+c['id']
            script['scenes'].append(dict(id=key,title=f"{ep['id']} verified game passage {c['id']}",lines=[c.get('spokenKo',c['ko'])]))
            evidence.append(dict(key=key,episode=ep['id'],sentence=c['id'],sourceEvidence=c['evidence'],sourceEvidenceSha256=sha(R/c['evidence']),ko=c['ko'],en=c['en']))
        for lang in ['ko','en']:
            for sentence in new[lang]['scenes']:
                if sentence['id'] in changed:sentence['lines']=[changed[sentence['id']][lang]]
            for a,b in zip(old[lang]['scenes'],new[lang]['scenes']):
                assert a['id']==b['id']
                if a['id'] not in changed:assert a==b
            save(P/f'production/contrast-v5/final.{lang}.json',new[lang])
    save(H/'narration/changed.ko.json',script)
    save(H/'narration/source-review.json',dict(revisionsSha256=sha(H/'narration/revisions.json'),evidence=evidence,existingSpokenAudioRegenerated=False))
    manifest={'slug':'animation-contrast-v5','revision':'contrast-v5','paths':{'script':(H/'narration/changed.ko.json').relative_to(R).as_posix()},
      'editing':{'narrationPlacement':'continuous-across-example-and-explanation'},'tts':{
      'language':'Korean','model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base','reference':'shared/voice-reference/reference-15-35s.wav',
      'referenceText':'shared/voice-reference/reference-15-35s.ko.txt','outputDir':(H/'local/voice').relative_to(R).as_posix(),
      'filenameStem':'contrast-game-passages','renderMode':'scene','sceneGapSeconds':.28,'tailRatioThreshold':.07,'tailDecayMsThreshold':70,
      'maxRenderAttempts':3,'maxNewTokens':2048,'edgeFadeSeconds':.006,'gpuMinimumFreeMiB':8192,
      'gpuProfileReason':'Only observed-source-matched changed game sentences, same approved1.7B own voice, batch1; no engine capture/model in parallel; preserve all other PCM.'}}
    save(H/'narration/tts-manifest.json',manifest)
    print(f'{len(script["scenes"])} verified changed narration paragraphs ready; no TTS started')
if __name__=='__main__':main()
