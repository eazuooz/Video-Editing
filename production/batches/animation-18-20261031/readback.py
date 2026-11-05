"""Recognize all encoded review audio without an expected-text prompt."""
from pathlib import Path
import json,sys,difflib,re,subprocess,hashlib,os
H=Path(__file__).resolve().parent;R=H.parents[2]
slug,revision=sys.argv[1:3];P=R/'projects'/slug;L=P/'production/local'/revision
assert L.resolve().is_relative_to((R/'projects').resolve()) and (L/'audio.m4a').is_file()
def read(f):return json.loads(f.read_text('utf-8-sig'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
sys.path.insert(0,str(R/'projects/animation-assigning/production/grid-v1'))
import storage_paths as store
store.LOCAL=L;store.HERE=P/'production'/revision
import audio_pipeline as ap
ap.LOCAL=L
file=L/'qa-aac.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',L/'audio.m4a','-ac','1','-ar','16000','-c:a','pcm_s16le',file],check=True)
from gpu_slot import idle_slot
with idle_slot(slug+'-final-audio-check') as available:
    os.environ['VIDEO_BATCH_ASR_DEVICE']='cuda' if available else 'cpu'
    record=ap.full_asr(file,L/'full-encoded-asr.json',final=True)
assert record['completeAudioSubmitted'] and record['noExpectedPrompt']
def norm(txt):
 text=re.sub(r'\s+','',txt.lower())
 aliases={'예순':'60','열두':'12','영점이':'02','언리얼엔진오':'언리얼엔진5','액터':'actor','엑터':'actor','컨트롤러':'controller','버스':'verse','벌스':'verse','씨플러스플러스':'cpp','c++':'cpp','블루프린트':'blueprint','폰':'pawn','프레임':'frame','엔진식스':'엔진6','버추어':'버추얼'}
 for k,v in aliases.items():text=text.replace(k,v)
 return re.sub(r'[^a-z0-9가-힣]','',text)
expected=norm(' '.join(c['ko'] for c in read(L/'cue-review.json')));heard=norm(record['text'])
m=difflib.SequenceMatcher(None,expected,heard,autojunk=False)
result={'completeAudioSubmitted':True,'noPrompt':True,'humanListening':False,'aacSha256':sha(L/'audio.m4a'),'coverage':sum(b.size for b in m.get_matching_blocks())/len(expected),'differences':[(expected[i:j],heard[k:l]) for code,i,j,k,l in m.get_opcodes() if code!='equal']}
(L/'encoded-text-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(slug,result['coverage'],flush=True)
checkpoint=P/'production'/revision/'checkpoint.json'
pending=L/'picture-checked-delivery.json'
if revision=='series-v1' and (pending.is_file() or checkpoint.is_file()):
    ledger=read(pending if pending.is_file() else checkpoint)
    ep=ledger['episode']
    if ep in {f'A{x:02}' for x in range(7,19)}:
        assert result['coverage']>=.94, f'{ep}: inspect the encoded speech differences before registering'
    if pending.is_file():
        audio_hash=subprocess.check_output(['ffmpeg','-v','error','-i',L/'audio.m4a','-map','0:a','-c:a','copy','-f','hash','-hash','sha256','-']).decode().strip()
        assert audio_hash==ledger['technicalChecks']['masters']['captioned']['audio']
    # Keep the small final-AAC evidence with its master while the raw recording stays local.
    ledger['encodedNarrationReadback']={key:result[key] for key in ('aacSha256','coverage','noPrompt','humanListening')}
    temp=checkpoint.with_suffix('.writing')
    temp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n','utf-8')
    temp.replace(checkpoint)
    if ep in {f'A{x:02}' for x in range(7,19)}:
        registered=next(row for row in read(R/'shared/publishing/video-worklist.json')['rows'] if row['id']==ep)
        if registered.get('captionedMasterSha256')!=ledger['captionedMasterSha256']:
            registrar=[sys.executable,'-X','utf8',H/'register_local.py']
            subprocess.run([*registrar,'--prepare',ep],cwd=R,check=True)
            spec=L/'commit-spec.json'
            subprocess.run([*registrar,'--spec',spec,'--apply-shared'],cwd=R,check=True)
            subprocess.run([*registrar,'--spec',spec,'--execute','--push','--message',f'Deliver the reviewed {ep} animation masters for local screening'],cwd=R,check=True)
