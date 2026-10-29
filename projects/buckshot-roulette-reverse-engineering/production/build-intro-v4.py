"""Native-motion comparison for the revised thesis; no synthetic original play."""
from __future__ import annotations
import argparse
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from assemble_documentary import PROJECT, digest, ff, load, probe, save, now, video_stream

OUT=PROJECT/'production/local/workflow-v4'
TIMING=PROJECT/'production/local/audio-v4/narration.timing.json'
BASE=PROJECT/'production/local/revision-v3-inputs/timeline.json'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
    plan=load(BASE); timing=load(TIMING); entries=timing['entries']
    first=entries[0]; boundary=entries[1]['start']; frames=round(boundary*60)
    if first['scene_id']!='01' or first['paragraph']!=1 or not 12<frames/60<33.166:
        raise ValueError('Inspect changed intro timing before choosing native-motion cuts')
    original=PROJECT/plan['sources']['second']['file']; own=PROJECT/plan['sources']['prototype-intro']['file']
    for sid,p in [('second',original),('prototype-intro',own)]:
        if digest(p)!=plan['sources'][sid]['sha256']:raise ValueError('Reviewed source changed')
    OUT.mkdir(parents=True,exist_ok=True)
    overlay=Image.new('RGBA',(1920,1080),(0,0,0,0)); d=ImageDraw.Draw(overlay)
    title=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',60)
    label=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',48)
    d.text((960,62),'분석한 규칙으로, 새로운 프로토타입',font=title,fill='#E8CF83',anchor='mt')
    d.text((480,155),'벅샷 룰렛 · 직접 플레이',font=label,fill='#FFFFFF',anchor='mt')
    d.text((1440,155),'NEON CHAMBER · 자체 구현',font=label,fill='#73C7C2',anchor='mt')
    d.line((960,238,960,778),fill='#73C7C2',width=4)
    overlay.save(OUT/'intro-comparison-labels.png')
    # Prototype already identifies itself in its native header; preserve that UI.
    full=Image.new('RGBA',(1920,1080),(0,0,0,0))
    full.save(OUT/'intro-prototype-label.png')
    decision={'createdAt':now(),'durationFrames':frames,'durationSeconds':frames/60,
      'voiceParagraph':first,'bodyOffset':0,'comparisonSeconds':12,
      'originalCuts':[{'source':str(original),'in':13,'out':20},{'source':str(original),'in':37,'out':42}],
      'prototypeCut':{'source':str(own),'in':0,'out':frames/60},
      'beforeActionResult':'Original self-blank discharge and next target choice beside our magnifier/self-blank prototype; then continued native prototype action.',
      'selectionEvidence':'planning/original-footage-audit.json; existing v3 b01/b02 and prototype-demo-fhd capture evidence',
      'audioChoice':'Original gameplay sound only during split; prototype sound afterward; no competing gunshot layers.',
      'captionZone':[150,892,1784,1060],'motionAltered':False,'originalSourceSha256':digest(original),'prototypeSourceSha256':digest(own),
      'visualReview':'pending revised comparison inspection; prior source review reused'}
    save(OUT/'intro-comparison-plan.json',decision)
    if not args.render:print('Prepared intro',frames/60);return
    dst=OUT/'intro-comparison.mp4'
    if dst.exists():raise FileExistsError('Preserve existing intro; review receipt before rerender')
    tail=frames/60-12
    filters=(
      '[0:v]setpts=PTS-STARTPTS,scale=960:540,setsar=1,fps=60[o1];'
      '[1:v]setpts=PTS-STARTPTS,scale=960:540,setsar=1,fps=60[o2];'
      '[o1][o2]concat=n=2:v=1:a=0[ol];'
      '[2:v]trim=duration=12,setpts=PTS-STARTPTS,scale=960:540,setsar=1,fps=60[pr];'
      '[ol][pr]hstack=inputs=2,pad=1920:1080:0:238:color=black[split];'
      '[split][3:v]overlay=0:0:shortest=1[head];'
      f'[4:v]trim=duration={tail:.9f},setpts=PTS-STARTPTS,scale=1920:860:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=1920:1080:(ow-iw)/2:0:color=black,setsar=1,fps=60[tailbase];'
      '[tailbase][5:v]overlay=0:0:shortest=1[tail];'
      '[head][tail]concat=n=2:v=1:a=0,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[v];'
      '[0:a]aresample=48000,asetpts=PTS-STARTPTS,volume=12dB,apad,atrim=end_sample=336000[a0];'
      '[1:a]aresample=48000,asetpts=PTS-STARTPTS,volume=12dB,apad,atrim=end_sample=240000[a1];'
      f'[4:a]aresample=48000,asetpts=PTS-STARTPTS,volume=4.5dB,apad,atrim=end_sample={(frames-720)*800}[a2];'
      '[a0][a1][a2]concat=n=3:v=0:a=1[a]')
    ff(plan,['-ss','13','-t','7','-i',original,'-ss','37','-t','5','-i',original,
      '-i',own,'-loop','1','-framerate','60','-i',OUT/'intro-comparison-labels.png',
      '-ss','12','-i',own,'-loop','1','-framerate','60','-i',OUT/'intro-prototype-label.png',
      '-filter_complex',filters,'-map','[v]','-map','[a]','-frames:v',str(frames),'-t',f'{frames/60:.9f}',
      '-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
      '-video_track_timescale','90000','-movflags','+faststart',dst],OUT/'logs/intro-comparison.log')
    meta=probe(dst,plan,True);v=video_stream(meta)
    if (v['width'],v['height'],int(v['nb_read_frames']))!=(1920,1080,frames):raise ValueError('Intro frame dimensions/count differ')
    decision.update(output=str(dst),sha256=digest(dst),actualFrames=int(v['nb_read_frames']),audioEncoding='AAC intermediary; final shared limiter handles headroom')
    save(OUT/'intro-comparison-receipt.json',decision)
    print('Rendered',frames,'frames')

if __name__=='__main__':main()
