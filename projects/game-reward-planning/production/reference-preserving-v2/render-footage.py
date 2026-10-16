"""Render only owned independent-source cuts; preserve speed and safe caption area."""
from pathlib import Path
import json,subprocess,hashlib,argparse
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';O=P/'production/local/reference-preserving-v2/edit';O.mkdir(exist_ok=True,parents=True)
plan=json.loads((P/'production/reference-preserving-v2/edit-plan.json').read_text(encoding='utf8'))
FONT="C\\:/Windows/Fonts/malgunbd.ttf"
def esc(s):return s.replace('\\','\\\\').replace(':','\\:').replace("'",'’').replace('%','\\%')
def run(args,log):
 with log.open('w',encoding='utf8') as f:
  p=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(log.read_text(encoding='utf8')[-3500:])
def render(c,force=False):
 output=O/(c['id']+'.mp4');signature=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();receipt=O/(c['id']+'.json')
 if not force and output.exists() and receipt.exists() and json.loads(receipt.read_text())['signature']==signature:
  print('Reuse',c['id'],flush=True);return
 d=c['frames']/60;filters=['fps=60','scale=1536:864:force_original_aspect_ratio=decrease:flags=lanczos','pad=1920:1080:(ow-iw)/2:0:color=0x05090b','setsar=1']
 if c['freeze']:filters.append('tpad=stop_mode=clone:stop_duration='+str(d))
 if c.get('analysisTail'):
  tail=c['analysisTail'];filters.extend([f"trim=end_frame={tail['startFrame']}",f"tpad=stop_mode=clone:stop_duration={d-tail['startFrame']/60}",f"drawtext=fontfile='{FONT}':text='{esc(tail['label'])}':fontsize=32:fontcolor=white:box=1:boxcolor=black@0.85:boxborderw=9:x=220:y=25:enable='gte(t,{tail['startFrame']/60})'"])
 credit=f"{c['game']} · Recording: {c['credit']}"
 filters.append(f"drawtext=fontfile='{FONT}':text='{esc(credit)}':fontsize=24:fontcolor=0xb1b8bd:x=192:y=870")
 if c['freeze']:
  filters.append(f"drawtext=fontfile='{FONT}':text='정지 화면 분석':fontsize=32:fontcolor=white:box=1:boxcolor=black@0.85:boxborderw=9:x=220:y=25")
 for m in c['marks']:
  en=f"between(t,{m['start']},{m['end']})";x,y,w,h=[m[k] for k in ['x','y','w','h']]
  filters += [f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black:t=13:enable='{en}'",f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0x{m['color']}:t=7:enable='{en}'",f"drawtext=fontfile='{FONT}':text='{esc(m['label'])}':fontsize=40:fontcolor=0x{m['color']}:box=1:boxcolor=black@0.8:boxborderw=9:x={m['labelX']}:y={m['labelY']}:enable='{en}'"]
 filt=O/(c['id']+'.filter.txt');filt.write_text(','.join(filters),encoding='utf8')
 args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-ss',str(c['sourceStart']),'-i',c['sourceFile']]
 if c['freeze']:args += ['-t',str(d)]
 args += ['-vf',','.join(filters),'-an','-frames:v',str(c['frames']),'-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-movflags','+faststart',str(output)]
 # For a frozen explanatory frame, read exactly one source frame before clone.
 if c['freeze']:
  filters.insert(0,'trim=end_frame=1');filt.write_text(','.join(filters),encoding='utf8');args[args.index('-vf')+1]=','.join(filters)
 if c.get('sourceSegments'):
  tail=args[args.index('-an'):];args=['ffmpeg','-y','-hide_banner','-loglevel','warning'];graph=[]
  for i,s in enumerate(c['sourceSegments']):
   args+=['-ss',str(s['start']),'-t',str(s['frames']/60),'-i',c['sourceFile']];graph.append(f'[{i}:v]fps=60,trim=end_frame={s["frames"]},setpts=PTS-STARTPTS[v{i}]')
  graph.append(''.join(f'[v{i}]' for i in range(len(c['sourceSegments'])))+f'concat=n={len(c["sourceSegments"])}:v=1:a=0[base]');graph.append('[base]'+','.join(filters)+'[out]')
  args+=['-filter_complex',';'.join(graph),'-map','[out]',*tail]
 run(args,O/(c['id']+'.log'))
 receipt.write_text(json.dumps({'signature':signature,'frames':c['frames'],'source':c['sourceFile'],'speed':1,'freezeAnalysis':c['freeze'],'output':str(output.relative_to(R)).replace('\\','/')},indent=2)+'\n')
 print('Rendered',c['id'],c['frames'],flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--cuts',default='');a.add_argument('--force',action='store_true');args=a.parse_args();selected=set(args.cuts.split(',')) if args.cuts else None
 for c in plan['cuts']:
  if 'sourceFile' in c and (not selected or c['id'] in selected):render(c,args.force)
