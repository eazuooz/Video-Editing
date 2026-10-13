from pathlib import Path
import json,datetime,hashlib
P=Path(__file__).resolve().parent;R=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'voice-repair08-execution-v1.json').exists()
line='영상 주제에 세부 설명을 더하거나, 공부할 내용과 질문을 정리할 때도 사용할 수 있습니다.'
write(P/'voice-repair08-request.json',dict(scenes=[dict(id='08p01s02',title='적용 범위',lines=[line])]))
m=read(P/'voice-manifest.json');m['paths']['script']=(P/'voice-repair08-request.json').relative_to(R).as_posix();m['tts'].update(outputDir=(P/'repair08-narration').relative_to(R).as_posix(),filenameStem='hierarchical-pokemon-08-repair',maxRenderAttempts=1);write(P/'voice-repair08-manifest.json',m)
write(P/'voice-repair08-reason.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Both whole and independent second-sentence ASR returned 묻거나 for 묶거나. No claim of a human listening failure; choose an unambiguous equivalent before delivery.',originalPreserved=True,replaceOnly='08p01 second sentence',unchangedFirstSentenceSourceRangeSeconds=[0,3.08],newText=line,oldVoiceAsr='voice-asr-v1.json',independent='voice-ambiguity.json',humanPronunciationApproved=False))
s=(P/'render-voice-v1.py').read_text(encoding='utf-8').replace("STATE = OUT / 'voice-execution-v1.json'", "STATE = OUT / 'voice-repair08-execution-v1.json'").replace("'voice-manifest.json'", "'voice-repair08-manifest.json'").replace("'generated-narration/chunks'", "'repair08-narration/chunks'").replace('len(items)==5','len(items)==1').replace("'voice-resource-v1.json'", "'voice-repair08-resource.json'")
(P/'render-repair08.py').write_text(s,encoding='utf-8')
print('Prepared one replacement sentence; unchanged first sentence remains byte-identical.')
