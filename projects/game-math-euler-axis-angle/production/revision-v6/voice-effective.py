"""CPU provenance mapping for preserved source audio and contextual ASR fixes.

Never synthesize/alter PCM or rewrite original41 ASR. Only independently
recognized complete contexts replace their own raw-time interval in a new
alignment sidecar. Retakes promote only after explicit direct-text records.
"""
from pathlib import Path
import argparse,importlib.util,json
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v6_voice_base',H/'voice-review.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
v=a.v;R,P,V=a.R,a.P,a.O
CONTEXTS={'v6-13':'v6-13.word','v6-36':'v6-36.overlap','v6-41':'v6-41.overlap'}
def contextual_sidecar(sid,context_id):
 original_file=V/'asr'/f'{sid}.json';original=v.read(original_file);context_file=V/'ambiguities'/(context_id+'.asr.json');context=v.read(context_file)
 assert len(context['parts'])==1 and context['parts'][0]['scene']==sid
 part=context['parts'][0];assert part['sourceSha256']==original['audio_sha256']
 low,high=part['sourceStartSample']/24000,part['sourceEndSample']/24000
 # Keep a preceding word whose end crosses the selected context boundary.
 # A contextual word begins no earlier than this actual extracted interval;
 # its own ASR timestamps are shifted, never invented or set from the script.
 prefix=[w for w in original['words'] if w['timestamp'][0] is not None and w['timestamp'][0]<low]
 suffix=[w for w in original['words'] if w['timestamp'][0] is not None and w['timestamp'][0]>=high]
 changed=[]
 for word in context['words']:
  start,end=word['timestamp'];assert start is not None and end is not None and end>=start
  changed.append(dict(text=word['text'],timestamp=[start+low,end+low]))
 words=prefix+changed+suffix
 assert all(x['timestamp'][0]<=y['timestamp'][0] for x,y in zip(words,words[1:])),'An unresolved timestamp backtrack must not enter alignment'
 report=dict(original,words=words,text=''.join(w['text'] for w in words),alignmentSidecar=True,
  originalAsrFile=original_file.relative_to(R).as_posix(),originalAsrSha256=v.sha(original_file),originalRecognizedText=original['text'],
  contextCorrection=dict(file=context_file.relative_to(R).as_posix(),sha256=v.sha(context_file),sourceInterval=[low,high],expectedTextPrompt=False,
   method='Replace this same source-time interval with independent complete-context recognition; original raw cache/audio preserved',newTimestampOffsetSeconds=low),humanListening='pending')
 output=V/'asr-effective'/f'{sid}.json';output.parent.mkdir(exist_ok=True)
 if output.exists():assert v.read(output)==report,'Preserve an existing different alignment correction'
 else:v.save(output,report)
 return output
def main():
 ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group();group.add_argument('--promote-retakes',action='store_true');group.add_argument('--promote-protected-openings',action='store_true');args=ap.parse_args();v.selected();a.v.validate()
 assert v.read(V/'ambiguities/execution.json')['status']=='complete-direct-context-review-pending'
 sides={sid:contextual_sidecar(sid,cid) for sid,cid in CONTEXTS.items()};done=v.read(V/'tts-current.json');rows=[]
 promoted=args.promote_retakes or args.promote_protected_openings
 retake_dir=V/'effective-openings' if args.promote_protected_openings else V/'retakes/openings-v1';retake={}
 if args.promote_protected_openings:
  review=v.read(retake_dir/'direct-review.json');take=v.read(retake_dir/'compositions.json')
  assert review['complete'] and review['fullExpectedAndRecognizedTextDirectlyRead'] and review['sceneCount']==2
  assert take['original41PcmAndAsrPreserved'] and take['earlierTakesPreserved'] and len(take['scenes'])==2
  for item in take['scenes']:
   note=next(x for x in review['scenes'] if x['id']==item['id']);asr=R/item['asrFile']
   assert note['sourceSha256']==item['sha256'] and note['asrSha256']==v.sha(asr) and note['acceptedForWordAlignment']
   assert item['exactSelectedFragmentsEqual'] and item['prefixNotRepeated']
   for fragment in item['fragments']:
    assert v.sha(R/fragment['file'])==fragment['sha256'] and v.sha(R/fragment['asrFile'])==fragment['asrSha256']
   retake[item['id']]=item
 if args.promote_retakes:
  review=v.read(retake_dir/'direct-review.json');assert review['complete'] and review['currentSourceTextReview']=='complete-full-text-review-with-noted-ASR-orthography;human-listening-pending'
  take=v.read(retake_dir/'retake-current.json');assert len(take['scenes'])==2
  for item in take['scenes']:
   r=next(x for x in review['scenes'] if x['id']==item['id']);asr=retake_dir/'asr'/f'{item["id"]}.json'
   assert r['sourceSha256']==item['sha256'] and r['asrSha256']==v.sha(asr) and r['acceptedForWordAlignment']
   retake[item['id']]=item
 for original in done['scenes']:
  sid=original['id'];item=retake.get(sid,original);file=R/item['file'];assert v.sha(file)==item['sha256']
  baseline=V/'asr'/f'{sid}.json';assert v.read(baseline)['audio_sha256']==original['sha256']
  asr=(R/item['asrFile'] if args.promote_protected_openings else retake_dir/'asr'/f'{sid}.json') if sid in retake else sides.get(sid,baseline)
  assert v.read(asr)['audio_sha256']==item['sha256']
  rows.append(dict(id=sid,file=item['file'],sha256=item['sha256'],samples=item['samples'],sampleRate=item['sampleRate'],seconds=item['seconds'],
   asrFile=asr.relative_to(R).as_posix(),asrSha256=v.sha(asr),origin=('protected-opening-fragment-composition' if args.promote_protected_openings else 'same-text-retake') if sid in retake else 'original-v6-PCM',
   originalFile=original['file'],originalSha256=original['sha256'],originalAsrFile=baseline.relative_to(R).as_posix(),originalAsrSha256=v.sha(baseline),humanListening='pending'))
 report=dict(schemaVersion=1,revision='article-flow-v6',status='current41-ready-for-word-alignment' if promoted else 'original41-baseline;10/32-retakes-pending',
  inputs=dict(koSha256=v.sha(P/'script/revision-v6-article-flow/narration.ko.json'),originalTtsReceiptSha256=v.sha(V/'tts-current.json'),originalWholeAsrSha256=v.sha(V/'euler-article-flow-v6.asr-review.json'),
   contextualResultsSha256=v.sha(V/'ambiguities/results.json'),retakeDirectReviewSha256=v.sha(retake_dir/'direct-review.json') if promoted else None,protectedOpeningCompositionSha256=v.sha(retake_dir/'compositions.json') if args.promote_protected_openings else None,implementationSha256=v.sha(Path(__file__))),
  scenes=rows,sceneCount=41,unchangedOriginalPcmCount=39 if promoted else 41,retakenSceneIds=sorted(retake),allOriginal41PcmAndAsrPreserved=True,humanWholeListening='pending')
 target=V/('current-pcm.json' if promoted else 'baseline-pcm-mapping.json')
 if target.exists():assert v.read(target)==report,'Do not silently replace a different source mapping'
 else:v.save(target,report)
 print('CPU effective-source mapping:',report['status'],';3 independent ASR alignment sidecars; original audio/cache untouched')
if __name__=='__main__':main()
