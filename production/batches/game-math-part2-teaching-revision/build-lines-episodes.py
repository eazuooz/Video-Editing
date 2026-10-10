"""Preserved original clips plus separately authored additions, narration only.

Every actual cut requires an editable observed track. Render/QA is distinct
from moving-pixel, human-listening, rights and publishing review.
"""
from pathlib import Path
import argparse,json,hashlib,importlib.util,shutil,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision/lines'
parser=argparse.ArgumentParser();parser.add_argument('slug',choices=['game-math-lines-circles-v2','game-math-bounds-transform-v2']);parser.add_argument('stage',choices=['render','mix','burn','qa']);parser.add_argument('--scenes');args=parser.parse_args()
spec=importlib.util.spec_from_file_location('caption_tools',ROOT/'projects/game-math-polar-sample/production/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.BASE=ROOT/'projects'/args.slug;b.WORK=ROOT/'shared/output'/args.slug;b.MC=ROOT/'motion-canvas/src/projects'/args.slug;b.MF=b.BASE/'project.json';b.WORK.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(B));spec=importlib.util.spec_from_file_location('game_overlay',B/'create-lines-overlay.py');overlay=importlib.util.module_from_spec(spec);spec.loader.exec_module(overlay)
m=b.read(b.MF);p=b.read(b.BASE/'production/timeline.json');assert p['ratioErrorFrames']==0 and p['actualShare']==.4 and p['explanationShare']==.6
ENC=['-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart']
def verify(path,frames):
 v=next(s for s in b.probe(path)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==frames and v['r_frame_rate']=='60/1' and (v['width'],v['height'])==(1920,1080),(path,v)
def render():
 selected=set(args.scenes.split(',')) if args.scenes else None
 out=b.WORK/'clips';out.mkdir(exist_ok=True);assets=b.MC/'assets';assets.mkdir(parents=True,exist_ok=True)
 ledger=b.WORK/'clip-receipts.json';receipts=b.read(ledger) if ledger.exists() else {}
 for ident,count in [('intro',120),('outro',600)]:
  src=ROOT/f'shared/output/game-math-lines-bounds/clips/{ident}.mp4';dst=out/f'{ident}.mp4';shutil.copy2(src,dst);verify(dst,count);assert b.sha(src)==b.sha(dst)
  shutil.copy2(dst,assets/dst.name)
 for slot in p['scenes']:
  ident=slot['id']
  if selected and ident not in selected:continue
  target=out/f'{ident}.mp4';count=slot['frames'];fingerprint={k:slot.get(k) for k in ['id','frames','seconds','voiceSha256','lineStarts','preservedSamplesSha256','cut']}
  if slot['classification']=='actual':
   ass=overlay.write_overlay(args.slug,ident);fingerprint['overlaySha256']=b.sha(ass)
   track=overlay.read(B/'lines-annotation-tracks.json')['scenes'][ident]
   fingerprint['trackSha256']=[b.sha(ROOT/x) for x in track['landmarkSources']]
  elif not slot['preservedOriginal']:
   kind='lines_additions';receipt=b.read(O/f'caption-safe-{kind}-receipts.json')[ident]
   assert receipt['voiceSha256']==slot['voiceSha256'] and receipt['lineStarts']==slot['lineStarts'],'Rerender explanation after new audio'
   source=O/f'caption-safe-v2/videos/{kind}/1080p60/{ident}.mp4';assert b.sha(source)==receipt['videoSha256']
   fingerprint['sourceSha256']=receipt['videoSha256'];assert 0<=count-receipt['frames']<=3,(ident,count,receipt['frames'])
  digest=hashlib.sha256(json.dumps(fingerprint,sort_keys=True).encode()).hexdigest()
  if target.exists() and receipts.get(ident,{}).get('fingerprint')==digest and receipts[ident]['sha256']==b.sha(target):verify(target,count);print('Retained current clip',ident,flush=True);continue
  if slot['preservedOriginal']:
   source=ROOT/slot['baselineClip']
   if slot['classification']=='actual':b.ff(['-i',source,'-vf',f'ass={b.rel(ass)}','-frames:v',count,*ENC,target],f'clip-{ident}.log')
   else:shutil.copy2(source,target)
  elif slot['classification']=='explanation':
   b.ff(['-i',source,'-vf','fps=60,setsar=1,tpad=stop_mode=clone:stop_duration=0.05','-frames:v',count,*ENC,target],f'clip-{ident}.log')
  else:
   segments=slot['cut']['segments'];parts=[]
   for index,segment in enumerate(segments):
    part=out/f'{ident}-source-{index+1}.mp4'
    b.ff(['-ss',segment['in'],'-i',ROOT/segment.get('sourceFile',slot['cut']['sourceFile']),'-vf','scale=1920:1080,setsar=1,fps=60','-frames:v',segment['frames'],*ENC,part],f'clip-{ident}-source-{index+1}.log');verify(part,segment['frames']);parts.append(part)
   raw=out/f'{ident}-unannotated.mp4'
   if len(parts)==1:shutil.copy2(parts[0],raw)
   else:
    listing=out/f'{ident}-sources.txt';b.write(listing,'\n'.join("file '"+f.as_posix()+"'" for f in parts)+'\n');b.ff(['-f','concat','-safe','0','-i',listing,'-c:v','copy','-an',raw],f'clip-{ident}-concat.log')
   b.ff(['-i',raw,'-vf',f'ass={b.rel(ass)}','-frames:v',count,*ENC,target],f'clip-{ident}-overlay.log')
  verify(target,count);shutil.copy2(target,assets/target.name)
  receipts[ident]={'fingerprint':digest,'sha256':b.sha(target),'frames':count,'baselinePixelLayerPreserved':slot['preservedOriginal'],'annotationAndCaptionMovingReview':False};b.write(ledger,receipts)
  print('Verified clip',ident,count,'frames; moving review pending',flush=True)
def mix():
 # Refuse a technically valid but stale clip after a mid-render plan edit.
 lesson={s['id']:s for s in b.read(b.BASE/'production/lesson.json')['scenes']}
 for slot in p['scenes']:
  if slot['classification']=='actual' and not slot['preservedOriginal']:
   chosen=[[seg['in'],seg['in']+seg['maxSeconds']] for seg in slot['cut']['sourceSegments']]
   intended=lesson[slot['id']]['intervals']
   assert len(chosen)==len(intended) and all(abs(a-c)<1e-8 and abs(z-d)<1e-8 for (a,z),(c,d) in zip(chosen,intended)),f'Replan the revised source interval before mixing: {slot["id"]}'
 ledger=b.read(b.WORK/'clip-receipts.json')
 for slot in p['scenes']:
  ident=slot['id'];fingerprint={k:slot.get(k) for k in ['id','frames','seconds','voiceSha256','lineStarts','preservedSamplesSha256','cut']}
  if slot['classification']=='actual':
   ass=overlay.write_overlay(args.slug,ident);fingerprint['overlaySha256']=b.sha(ass)
   track=overlay.read(B/'lines-annotation-tracks.json')['scenes'][ident]
   fingerprint['trackSha256']=[b.sha(ROOT/x) for x in track['landmarkSources']]
  elif not slot['preservedOriginal']:
   kind='lines_additions';receipt=b.read(O/f'caption-safe-{kind}-receipts.json')[ident]
   assert receipt['voiceSha256']==slot['voiceSha256'] and receipt['lineStarts']==slot['lineStarts']
   if not slot['preservedOriginal']:
    assert receipt['sourceSha256']==b.sha(ROOT/'manim/projects/game-math-part2-teaching-revision/lines_additions.py'),'Render the current numeric explanation code before mixing'
   fingerprint['sourceSha256']=receipt['videoSha256']
  digest=hashlib.sha256(json.dumps(fingerprint,sort_keys=True).encode()).hexdigest()
  assert ledger.get(ident,{}).get('fingerprint')==digest,f'Rerender current scene before mixing: {ident}'
  assert ledger[ident]['sha256']==b.sha(b.WORK/f'clips/{ident}.mp4'),f'Changed clip after receipt: {ident}'
 clips=[b.WORK/'clips/intro.mp4',*[b.WORK/f'clips/{s["id"]}.mp4' for s in p['scenes']],b.WORK/'clips/outro.mp4']
 for clip,count in zip(clips,[120,*[s['frames'] for s in p['scenes']],600]):verify(clip,count)
 for key in ['editorAudioMix','audioMix','videoClean']: (ROOT/m['paths'][key]).parent.mkdir(parents=True,exist_ok=True)
 lv=b.loudness(ROOT/m['paths']['narration'],-16,-1.7)
 filt=f'loudnorm=I=-16:TP=-1.7:LRA=11:measured_I={lv["input_i"]}:measured_TP={lv["input_tp"]}:measured_LRA={lv["input_lra"]}:measured_thresh={lv["input_thresh"]}:offset={lv["target_offset"]}:linear=true,aresample=48000,aformat=channel_layouts=stereo'
 pcm=ROOT/m['paths']['editorAudioMix'];encoded=ROOT/m['paths']['audioMix'];b.ff(['-i',ROOT/m['paths']['narration'],'-af',filt,'-c:a','pcm_s16le',pcm],'narration-only-master.log');corrections=[]
 for attempt in range(3):
  b.ff(['-i',pcm,'-c:a','aac','-b:a','192k',encoded],'audio-aac.log');measure=b.loudness(encoded,-16,-1.5)
  if abs(float(measure['input_i'])+16)<=.35:break
  gain=-16-float(measure['input_i']);assert abs(gain)<=6 and float(measure['input_tp'])+gain<=-1.7
  changed=b.WORK/f'gain-correction-{attempt+1}.wav';b.ff(['-i',pcm,'-af',f'volume={gain}dB','-c:a','pcm_s16le',changed]);shutil.copy2(changed,pcm);corrections.append({'encodedBefore':measure,'gainDb':gain})
 assert abs(float(measure['input_i'])+16)<=.65 and float(measure['input_tp'])<=-1.45
 samples,sr=sf.read(pcm);assert np.max(np.abs(samples[:int(1.8*sr)]))==0 and np.max(np.abs(samples[-int(9*sr):]))==0
 b.write(b.BASE/'audio/mix-measurements.json',{'voiceInput':lv,'encodedGainCorrections':corrections,'final':measure,'audioInputs':[m['paths']['narration']],'backgroundMusic':False,'sourceAudioUsed':False,'brandingOutroSilenceVerified':True,'humanListening':'pending','seconds':p['seconds']})
 # Preserved baseline clips use 90k ticks; newly encoded clips use 15360.
 # Concat-copy requires one time base. Remux copies H.264 packets unchanged.
 normalized=[];remux=b.WORK/'timebase-normalized';remux.mkdir(exist_ok=True)
 for clip in clips:
  dst=remux/clip.name;receipt=dst.with_suffix('.json');source_sha=b.sha(clip)
  if not dst.exists() or not receipt.exists() or b.read(receipt).get('sourceSha256')!=source_sha:
   b.ff(['-i',clip,'-map','0:v:0','-c:v','copy','-an','-video_track_timescale','90000',dst],f'timebase-{clip.stem}.log')
   packet=lambda file:b.run(['ffmpeg','-v','error','-i',file,'-map','0:v:0','-c','copy','-f','md5','-']).strip()
   assert packet(clip)==packet(dst),'Remux must retain the original encoded pixels'
   b.write(receipt,{'sourceSha256':source_sha,'timeBase':'1/90000','videoPacketsPreserved':True})
  assert next(s for s in b.probe(dst)['streams'] if s['codec_type']=='video')['time_base']=='1/90000'
  normalized.append(dst)
 listing=b.WORK/'concat.txt';b.write(listing,'\n'.join("file '"+f.as_posix()+"'" for f in normalized)+'\n')
 b.ff(['-f','concat','-safe','0','-i',listing,'-i',encoded,'-map','0:v','-map','1:a','-c','copy','-t',p['seconds'],'-movflags','+faststart',ROOT/m['paths']['videoClean']],'final-clean.log')
 print('Narration-only clean master assembled; captions and QA still required',flush=True)
def qa():
 videos={}
 for key in ['videoClean','videoBurnedCaptions']:
  file=ROOT/m['paths'][key];b.ff(['-v','error','-i',file,'-f','null','-'],f'decode-{key}.log');verify(file,p['frames']);info=b.probe(file);assert abs(float(info['format']['duration'])-p['seconds'])<=.03
  packet=b.run(['ffmpeg','-v','error','-i',file,'-map','0:a','-c','copy','-f','md5','-']).strip();videos[key]={'path':m['paths'][key],'sha256':b.sha(file),'frames':p['frames'],'fullDecode':True,'audioPacketMd5':packet}
 assert videos['videoClean']['audioPacketMd5']==videos['videoBurnedCaptions']['audioPacketMd5']
 assert [(c['start'],c['end']) for c in p['koCaptions']]==[(c['start'],c['end']) for c in p['enCaptions']]
 b.write(b.BASE/'production/qa.json',{'fullDecodePassed':True,'videos':videos,'frames':p['frames'],'seconds':p['seconds'],'bodyFrames':p['bodyFrames'],'actualFrames':p['actualFrames'],'explanationFrames':p['explanationFrames'],'actualShare':.4,'explanationShare':.6,'ratioErrorFrames':0,'koEnMatchingTimes':True,'captionCount':len(p['koCaptions']),'directVisualReview':'pending','humanListening':'pending','rightsReview':'Preserved recording permissions; game-IP/human review pending','upload':'not yet uploaded','backgroundMusic':False,'sourceAudioUsed':False})
 print('Decode, exact frames, bilingual timing and identical captioned audio verified; direct review pending',flush=True)
{'render':render,'mix':mix,'burn':b.burn,'qa':qa}[args.stage]()
