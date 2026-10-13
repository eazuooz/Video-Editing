from pathlib import Path
P=Path(__file__).resolve().parent;N=P.parent/'reference-preserving-v1';R=P.parents[3]
import hashlib
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(N/'build-current-v1.py').read_text(encoding='utf-8')
s=s.replace("'575c807611d8c60040db51764cd805cf712fae48fd0037525f8591c753f50070'",repr(sha(R/'projects/hierarchical-game-outlines/project.json')))
s=s.replace("'reference-preserving-v1/' in cmd", "'pokemon-opening-v2/' in cmd").replace("'render-reference.cjs'","'render-pokemon.cjs'")
s=s.replace("'build-current-v1.py']", "'build-current-v1.py','render-voice-v1.py']")
s=s.replace("mode=sys.argv[1];", "sys.stdout.reconfigure(encoding='utf-8')\nmode=sys.argv[1];")
a=s.index(" if mode in ['preflight','visuals']:");b=s.index(" if mode=='mix':")
s=s[:a]+''' if mode=='visuals':
  ppt=read(P/'white-cpu-execution.json');assert ppt['status']=='rendered-pending-direct-pixels-and-full-decode' and len(ppt['completed'])==2
  dest=P/'pieces-local';dest.mkdir(exist_ok=True)
  prev=ROOT/'projects/hierarchical-game-outlines/production/reference-preserving-v1'
  pieces=[prev/'pieces-local/intro.mp4']
  for i,cut in enumerate(plan['pieces']):
   if cut.get('reuseVisual'):
    target=ROOT/cut['reuseVisual'];assert sha(target)==cut['reuseVisualSha256'];pieces.append(target);continue
   target=dest/f'{i:02}-{cut["scene"]}-{cut["kind"]}.mp4'
   if cut['kind'].startswith('ex'):
    ff(['-threads','2','-ss',str(cut.get('sourceStart',0)),'-i',str(ROOT/cut['path']),'-vf','setpts=PTS-STARTPTS,setsar=1','-frames:v',str(cut['frames']),*enc,str(target)])
   elif cut['kind']=='pokemon':
    # Preserve the complete 10:9 original and all English game UI above fixed captions.
    f='[0:v]split=2[bg][fg];[bg]scale=1920:1080:flags=neighbor,boxblur=32:2[blur];[fg]scale=960:864:flags=neighbor[front];[blur][front]overlay=480:12,setsar=1,fps=60[v]'
    ff(['-threads','2','-ss',str(cut['sourceStart']),'-i',str(ROOT/cut['path']),'-filter_complex_threads','1','-filter_complex',f,'-map','[v]','-frames:v',str(cut['frames']),*enc,str(target)])
   else:raise AssertionError('Unexpected new cut '+str(cut))
   v=next(x for x in probe(target)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==cut['frames']
   pieces.append(target);done(dict(cut=i,frames=cut['frames'],path=target.relative_to(ROOT).as_posix(),sha256=sha(target)))
  pieces.append(prev/'pieces-local/outro.mp4')
  concat=P/'silent-concat-local.txt';concat.write_text('\\n'.join("file '"+p.as_posix()+"'" for p in pieces)+'\\n',encoding='utf-8')
  target=P/'current-silent-v1.mp4';ff(['-f','concat','-safe','0','-i',str(concat),'-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(target)])
  v=next(x for x in probe(target)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==plan['totalFrames']
  done(dict(path=target.relative_to(ROOT).as_posix(),frames=int(v['nb_frames']),sha256=sha(target)))
''' +s[b:]
# Reuse the prior accepted -1.05dB headroom treatment before final AAC encoding.
s=s.replace("sf.write(P/'current-mix-prelimit-local.wav',mix,sr,subtype='FLOAT')", "mix*=10**(-1.05/20)\n  state['finalHeadroomDb']=-1.05\n  sf.write(P/'current-mix-prelimit-local.wav',mix,sr,subtype='FLOAT')")
s=s.replace("done(dict(path=(P/'current-mix-v1.m4a')", "write(P/'mix-final-inputs-v1.json',dict(audio=(P/'current-mix-v1.m4a').relative_to(ROOT).as_posix(),sha256=sha(P/'current-mix-v1.m4a'),scenes=[dict(id=sc['id'],path=(d/f'{sc[\"id\"]}.wav').relative_to(ROOT).as_posix(),sha256=sha(d/f'{sc[\"id\"]}.wav')) for sc in plan['scenes']]))\n  done(dict(path=(P/'current-mix-v1.m4a')")
s=s.replace("ff(['-threads','2','-i',str(P/'current-silent-v1.mp4')", "ff(['-threads','2','-reinit_filter','0','-i',str(P/'current-silent-v1.mp4')")
s=s.replace("'[0:v][1:v]overlay=0:0:shortest=1[v]'", "'[0:v]setsar=1[base];[base][1:v]overlay=0:0:shortest=1[v]'")
s=s.replace("if cut['kind']=='ex':samples.update", "if cut['scene'] in ['01','01a'] and cut['kind']=='ex':samples.update")
# Every caption/cut is inspected. Only the new explanation motion requires additional
# dense samples; unchanged body motion is bound to the exact retained silent assets.
(P/'build-current-v1.py').write_text(s,encoding='utf-8')
print('Prepared current assembler; retained body visual assets are hash-bound.')
