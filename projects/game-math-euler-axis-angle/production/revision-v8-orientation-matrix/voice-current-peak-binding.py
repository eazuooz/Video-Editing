"""Bind the preserved comparison to the one changed paragraph and current source.

Old whole-program comparison measurements remain explicitly old. Re-measure
the current whole body's input loudness/true peak separately and test the
new paragraph through the same ceiling; no production source is changed.
"""
from pathlib import Path
import importlib.util,json,math,subprocess
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_peak_binding_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_peak_binding_measure',H/'voice-ceiling-comparison.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 c.validate();current_file=c.O/'tts-current.json';current=c.read(current_file);old_file=c.O/'history/before-m07-L02-repair/tts-current.json';old=c.read(old_file)
 comparison_file=c.O/'diagnostics/ceiling-comparison.json';comparison=c.read(comparison_file);assert comparison['inputs']['sourceReceiptSha256']==c.sha(old_file)
 head_file=c.O/'source-headroom.json';head=c.read(head_file);assert head['inputs']['sourceReceiptSha256']==c.sha(current_file)
 oldby={s['id']:s for s in old['scenes']};unchanged=[]
 for scene in current['scenes']:
  assert c.sha(c.R/scene['file'])==scene['sha256']
  if scene['id']!='m07':assert scene['sha256']==oldby[scene['id']]['sha256'];unchanged.append(dict(id=scene['id'],sha256=scene['sha256']))
 scene=current['scenes'][6];previous=oldby['m07'];unchanged_lines=[]
 for before,after in zip(previous['lines'],scene['lines']):
  if after['line']!=2:
   assert after['takeSha256']==before['takeSha256']and after['gainDb']==before['gainDb'];unchanged_lines.append(dict(line=after['line'],takeSha256=after['takeSha256'],gainDb=after['gainDb']))
 selected=scene['lines'][1];assert selected['qaSelection']['pronunciationAlias']['displayPhrase']=='이분의 일입니다'
 gain=-16-head['currentBodyInputLufs'];limit=10**(-2.3/20);out=c.O/'diagnostics';base=out/'current-m07L02-global.float.wav';derived=out/'current-m07L02-ceiling.float.wav'
 assert not base.exists()and not derived.exists(),'Preserve a different current-paragraph test'
 graph=f'[0:a]volume={selected["gainDb"]:.12f}dB,aresample=48000,pan=stereo|c0=c0|c1=c0,volume={gain:.12f}dB,asplit=2[base][pre];[pre]aresample=192000,alimiter=limit={limit:.12f}:attack=5:release=80:level=false:latency=true,aresample=48000[limited]'
 command=['ffmpeg','-y','-hide_banner','-nostdin','-threads','2','-filter_complex_threads','2','-i',str(c.R/selected['takeFile']),'-filter_complex',graph,'-map','[base]','-c:a','pcm_f32le',str(base),'-map','[limited]','-c:a','pcm_f32le',str(derived)]
 run=subprocess.run(command,capture_output=True);(out/'current-m07L02-ceiling-build.log').write_bytes(run.stderr);assert run.returncode==0
 before=m.measure(base,out/'current-m07L02-global-measurement.log');after=m.measure(derived,out/'current-m07L02-ceiling-measurement.log')
 x,fs=sf.read(base,dtype='float32',always_2d=True);y,ys=sf.read(derived,dtype='float32',always_2d=True);assert fs==ys==48000 and x.shape==y.shape
 asr=c.read(c.R/scene['asrFile']);active=np.zeros(len(x),bool);origin=selected['startSample']/24000
 for w in asr['words']:
  a,b=w['timestamp']
  if a is not None and b is not None and b>a:active[max(0,round((a-origin)*fs)):max(0,min(len(x),round((b-origin)*fs)))]=True
 windows=[]
 for a in range(0,len(x)-19200+1,4800):
  b=a+19200;mask=active[a:b]
  if mask.sum()<7200:continue
  p,q=m.db(m.rms(x[a:b][mask])),m.db(m.rms(y[a:b][mask]));windows.append(dict(start=a/fs,end=b/fs,baselineDbfs=p,postCeilingDbfs=q,energyReductionDb=p-q))
 levels_file=c.O/'line-levels.json';levels=c.read(levels_file)
 report=dict(revision='orientation-matrix-v8',inputs=dict(sourceReceiptSha256=c.sha(current_file),currentWholeBodyHeadroomSha256=c.sha(head_file),
  originalComparisonSha256=c.sha(comparison_file),originalComparisonSourceReceiptSha256=c.sha(old_file),currentLineLevelsSha256=c.sha(levels_file),implementationSha256=c.sha(Path(__file__))),
  currentSourceReceipt=c.rel(current_file),originalComparison=dict(file=c.rel(comparison_file),sha256=c.sha(comparison_file),measurementsApplyTo='Preserved pre-m07-repair1492.2804s source; not relabeled as current'),
  unchangedSceneCount=len(unchanged),unchangedSceneHashes=unchanged,changedScene='m07',unchangedParagraphsWithinChangedScene=unchanged_lines,
  changedParagraph=dict(scene='m07',line=2,rawTakeFile=selected['takeFile'],rawTakeSha256=selected['takeSha256'],lineGainDb=selected['gainDb'],seconds=len(x)/fs,
   normalizedSamplePeakDbfs=m.db(selected['processedFloatPeak']),pronunciationAlias=selected['qaSelection']['pronunciationAlias'],
   comparisonBaseline=dict(file=c.rel(base),sha256=c.sha(base),measurement=before),comparisonDerived=dict(file=c.rel(derived),sha256=c.sha(derived),measurement=after),
   windows400ms=windows,maximum400msEnergyReductionDb=max(w['energyReductionDb']for w in windows)),
  currentBody=dict(sourceHeadroom=c.rel(head_file),sourceHeadroomSha256=c.sha(head_file),inputLufs=head['currentBodyInputLufs'],inputTruePeakDbtp=head['currentBodyTruePeakDbtp'],
   targetGlobalGainDb=gain,targetGainTruePeakPredictionDbtp=head['currentBodyTruePeakDbtp']+gain,seconds=head['sourceBodySeconds'],normalizedFloatPeaksAboveOne=sum(r['processedFloatPeak']>1 for r in levels['lines'])),
  reuseBoundary='All12 other scenes and4 otherm07 paragraphs are unchanged PCM/gains. The old comparison proves limiter behavior only for that prior program; its exact attenuation statistics are retained as prior evidence. Current full-body inputI/TP and changedparagraph limiter output are newly measured. Actual placed finalstem/AAC still require final measurements.',
  filter=dict(lookaheadMs=5,releaseMs=80,ceilingDbfs=-2.3,processingRate=192000,outputRate=48000,autoLevel=False,latencyCompensated=True),
  sourceChangedByThisJob=False,sourceSpeed=1,humanListening='pending',actualFinalStem='pending',finalEncodedAac='pending')
 assert len(unchanged)==12 and len(unchanged_lines)==4;c.save(c.O/'current-source-peak-binding.json',report)
 print(json.dumps(dict(currentBody=report['currentBody'],changedParagraphBefore=before,changedParagraphAfter=after),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
