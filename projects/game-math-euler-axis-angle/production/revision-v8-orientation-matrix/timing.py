"""Single24kHz PCM/60fps clock for all V8 video layers and captions."""
from pathlib import Path
import argparse,hashlib,importlib.util,math
H=Path(__file__).parent
def mod(name,file):
 sp=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
c=mod('v8_clock_common','common.py')
def normalizer():return mod('v8_clock_normalize','voice-normalize.py').normalized
def make_timeline():
 c.authorized();al=c.read(c.O/'audio/source-alignment.json');ko=c.read(c.S/'narration.ko.json');norm=normalizer()
 assert len(al['scenes'])==len(ko['scenes'])==13
 pos=120;scenes=[]
 for s,a in zip(ko['scenes'],al['scenes']):
  assert s['id']==a['id'] and a['sampleRate']==24000
  assert c.sha(c.R/a['sourceFile'])==a['sourceSha256']
  frames=math.ceil(a['samples']/400);lines=[]
  assert len(s['paragraphs'])==len(a['lines'])
  for i,(p,line) in enumerate(zip(s['paragraphs'],a['lines']),1):
   assert len(norm(p))==len(line['characterStarts'])==len(line['characterEnds'])
   lines.append(dict(line=i,paragraphId=f'{s["id"]}.L{i:02}',rawStart=line['rawStart'],rawEnd=line['rawEnd'],globalStart=pos/60+line['rawStart'],globalEnd=pos/60+line['rawEnd'],startFrame=round(pos+line['rawStart']*60),endFrame=round(pos+line['rawEnd']*60),sourceTextSha256=hashlib.sha256(p.encode()).hexdigest()))
  scenes.append(dict(id=s['id'],title=s['title'],section=s['section'],startFrame=pos,endFrame=pos+frames,frames=frames,start=pos/60,end=(pos+frames)/60,rawVoiceFile=a['sourceFile'],rawVoiceSha256=a['sourceSha256'],rawVoiceSamples=a['samples'],sampleRate=24000,tailPadSamples=frames*400-a['samples'],sourceSpeed=1,insertedObservationFrames=0,lines=lines));pos+=frames
 intro='projects/game-reward-planning/production/local/reference-preserving-v2/edit/branding.mp4'
 result=dict(schemaVersion=1,revision='orientation-matrix-v8',fps=60,width=1920,height=1080,introFrames=120,outroFrames=600,bodyStartFrame=120,bodyEndFrame=pos,totalFrames=pos+600,duration=(pos+600)/60,insertedObservationFrames=0,sceneGapFrames=0,voiceRate=1,tailPaddingOnly=True,paneLayout=dict(unity=[40,180,1000,700],math=[1080,180,800,700],game=[40,250,1000,562],gamePairUnity=[1080,220,800,560]),branding=dict(intro=dict(file=intro,frames=120),membership=dict(file=intro.replace('branding.mp4','membership.mp4'),frames=600,startFrame=pos)),inputs=dict(koSha256=c.sha(c.S/'narration.ko.json'),enSha256=c.sha(c.S/'narration.en.json'),alignmentSha256=c.sha(c.O/'audio/source-alignment.json')),scenes=scenes,humanFinalReview='pending')
 assert sum(len(s['lines'])for s in scenes)==76;c.save(H/'timeline.json',result);print('Timeline',result['duration'],'seconds',result['totalFrames'],'frames');return result
class Clock:
 def __init__(self):
  self.timeline=c.read(H/'timeline.json');self.alignment=c.read(c.O/'audio/source-alignment.json');self.scenes={x['id']:x for x in self.timeline['scenes']};self.raw={x['id']:x for x in self.alignment['scenes']};self.script={s['id']:s for s in c.read(c.S/'narration.ko.json')['scenes']};self.normalize=normalizer()
  assert self.timeline['inputs']['alignmentSha256']==c.sha(c.O/'audio/source-alignment.json')
 def word(self,sid,line,offset,end=False):
  text=self.script[sid]['paragraphs'][line-1];data=self.raw[sid]['lines'][line-1];n=len(self.normalize(text[:offset]));array=data['characterEnds'] if end else data['characterStarts'];local=array[n-1] if end else array[n];return self.scenes[sid]['start']+local
 def frame(self,sid,line,offset,end=False):return round(self.word(sid,line,offset,end)*60)
 def literal(self,sid,line,value,end=False,after=0):
  text=self.script[sid]['paragraphs'][line-1];at=text.index(value,after);return self.word(sid,line,at+len(value)if end else at,end)
 def cueframe(self,sid,line,value,end=False):return round(self.literal(sid,line,value,end)*60)
 def paragraph(self,sid,line):
  s=self.scenes[sid];start=s['startFrame']if line==1 else s['lines'][line-1]['startFrame'];end=s['lines'][line]['startFrame']if line<len(s['lines'])else s['endFrame'];return start,end
if __name__=='__main__':make_timeline()
