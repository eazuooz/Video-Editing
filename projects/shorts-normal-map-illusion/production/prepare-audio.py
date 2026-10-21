"""Derive speech-only aliases and validate this new Short's exact current text before TTS."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re,unicodedata
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return re.sub(r'[^0-9a-z가-힣]','',unicodedata.normalize('NFC',t).lower())
def main():
 c=read(R/'shared/publishing/video-production-control.json');assert c.get('selectedShortVideo')==P.name and c['shortsDirectSelection']['selectedRevision']=='normal-map-v1'
 raw=read(P/'script/narration.ko.json');cl=read(P/'script/clauses.json');aliases=cl.get('pronunciationAliases',{})
 assert aliases=={'3D':'쓰리디','2D':'투디'},'Review changes to approved speech/display aliases'
 def spoken(t):
  for display,speech in sorted(aliases.items(),key=lambda item:-len(item[0])):t=re.sub(re.escape(display),lambda match:speech,t,flags=re.I)
  return t
 original=[line for sc in raw['scenes'] for line in sc['lines']];lines=[spoken(line) for line in original]
 assert norm((P/'script/narration.ko.txt').read_text(encoding='utf8'))==norm(''.join(original))
 clauses=cl['clauses'];assert len(original)==12 and len(clauses)==27
 assert [x['lineIndex'] for x in clauses]==sorted(x['lineIndex'] for x in clauses)
 for i,line in enumerate(lines):
  expected=''.join(x['spoken'] for x in clauses if x['lineIndex']==i)
  assert norm(expected)==norm(line),f'Spoken clauses omit/change line{i}: {expected} versus {line}'
  display=''.join(x['ko'] for x in clauses if x['lineIndex']==i)
  assert norm(display)==norm(original[i]),f'Display captions changed useful original wording atline{i}'
 for x in clauses:
  e=x.get('emphasis')
  if e:assert x['ko'].count(e['text'])==1 and e['role'] in ['term','result','problem']
 doc=copy.deepcopy(raw)
 for sc in doc['scenes']:sc['lines']=[spoken(line) for line in sc['lines']]
 doc['derivation']={'displayScript':'script/narration.ko.json','displayScriptSha256':sha(P/'script/narration.ko.json'),'clausesSha256':sha(P/'script/clauses.json'),'pronunciationAliases':aliases,'displayWordingPreserved':True,'speechSpeed':1,'sceneGapSeconds':0,'forcedObservationHolds':0}
 voice=L/'voice/normal-map-v1.wav';target=P/'script/narration.spoken.ko.json';text=json.dumps(doc,ensure_ascii=False,indent=2)+'\n'
 if voice.exists() and (not target.exists() or target.read_text(encoding='utf8')!=text):raise RuntimeError('Voice exists: preserve it, do not revise its derived input silently.')
 target.write_text(text,encoding='utf8');(P/'script/narration.spoken.ko.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
 spec=importlib.util.spec_from_file_location('caption_preflight',P/'production/time-captions.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 from PIL import ImageFont
 f=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',60);layout=[{'id':x['id'],'koLines':m.wrap(x['ko'],f),'enLines':m.wrap(x['en'],f)} for x in clauses]
 def luminance(hex):
  values=[int(hex[i:i+2],16)/255 for i in (0,2,4)];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values];return sum(x*y for x,y in zip(linear,[.2126,.7152,.0722]))
 roles={k:{'foreground':v,'contrast':1.05/(luminance(v)+.05)} for k,v in {'term':'005059','result':'005221','problem':'A53131'}.items()};assert min(x['contrast'] for x in roles.values())>=4.5
 manifest=read(P/'production/tts-manifest.json');assert manifest['paths']['script']==str(target.relative_to(R)).replace('\\','/')
 report={'status':'currentdisplay→spoken aliases/27completeclauses validated; actualpreview/TTS pending','displayScriptSha256':sha(P/'script/narration.ko.json'),'derivedSpokenSha256':sha(target),'clausesSha256':sha(P/'script/clauses.json'),'ttsManifestSha256':sha(P/'production/tts-manifest.json'),'approvedReferenceSha256':sha(R/manifest['tts']['reference']),'approvedReferenceTextSha256':sha(R/manifest['tts']['referenceText']),'lines':12,'clauses':27,'sceneCount':len(doc['scenes']),'oneContinuousScene':len(doc['scenes'])==1,'pronunciationAliases':aliases,'spokenHangulSyllables':len(re.findall('[가-힣]',''.join(lines))),'captionLayoutPreflight':layout,'captionRoleColors':roles,'fixedCaptionCenter':[510,1380],'captionMaxLines':2,'gpuAllocatorCapMiB':6144,'gpuMinimumFreeMiB':7500,'gpuSafetyReserveMiB':1356,'costlyJobsStarted':0,'actualPaceHumanListening':'pending','sourcePcmGenerated':False}
 L.mkdir(parents=True,exist_ok=True);(L/'audio-input-preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:report[k] for k in ['status','lines','clauses','spokenHangulSyllables','costlyJobsStarted']},ensure_ascii=False))
if __name__=='__main__':main()
