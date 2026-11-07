"""Verify complete bilingual cue preservation and insertion accounting."""
from pathlib import Path
import json,re,sys,datetime
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=B/'local/pacing-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def cues(p):
 result=[]
 for block in re.split(r'\n\s*\n',p.read_text('utf-8-sig').strip()):
  lines=block.splitlines()
  def sec(t):
   h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
  a,b=map(sec,lines[1].split(' --> '));result.append((a,b,'\n'.join(lines[2:])))
 return result
rows=read(B/'real-clips-v2/review-manifest.json')['records'];result={}
for row in rows:
 ep=row['id']
 if ep=='A02' or (len(sys.argv)>1 and ep not in sys.argv[1:]):continue
 P=R/'projects'/row['slug'];plan=read(P/'production/pacing-v3/edit-plan.json');D=R/plan['outputDirectory']
 if not (D/'delivery-manifest.json').exists():continue
 out=read(D/'delivery-manifest.json');ev=out['events'];languages={}
 assert plan['totalFrames']==plan['baselineFrames']+sum(e['frames'] for e in ev)
 assert round(out['durationSeconds']*60)==plan['totalFrames']
 for language in ['ko','en']:
  kind=language+'.srt'
  before=cues(R/next(f['path'] for f in row['files'] if f['kind']==kind))
  after=cues(R/next(f['path'] for f in out['files'] if f['kind']==kind))
  assert len(before)==len(after),(ep,language,'cue count')
  maximum=0
  for old,new in zip(before,after):
   a,b,txt=old;c,d,newtxt=new;assert txt==newtxt,(ep,language,'changed text')
   assert not any(a+.00001<e['audioAt']/60<b-.00001 for e in ev)
   expectedA=a+sum(e['frames']/60 for e in ev if e['audioAt']/60<=a+.00001)
   expectedB=b+sum(e['frames']/60 for e in ev if e['audioAt']/60<b-.00001)
   error=max(abs(c-expectedA),abs(d-expectedB));maximum=max(maximum,error)
   assert error<=.0011,(ep,language,'cue timing',old,new,error)
  languages[language]=dict(cues=len(before),allCueTextPreserved=True,maximumRoundingSeconds=maximum)
  if language=='ko':
   for e in ev:
    preceding=[c for c in before if c[1]<=e['audioAt']/60+.001]
    assert not preceding or re.search(r'[.!?][”"’\']?$',preceding[-1][2]),(ep,e['key'],'incomplete sentence before inserted observation',preceding[-1][2])
   languages[language]['allObservationInsertionsAfterCompleteSentence']=True
 result[ep]=dict(languages=languages,baselineFrames=plan['baselineFrames'],insertedFrames=sum(e['frames'] for e in ev),totalFrames=plan['totalFrames'],maximumPictureAudioBoundaryOffsetSeconds=max(abs(e['pictureAt']-e['audioAt'])/60 for e in ev),checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
target=L/'preservation-audit.json';data=read(target) if target.exists() else {};data.update(result);target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(result,ensure_ascii=False))
