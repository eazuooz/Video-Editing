"""Finite v4 pixel delta extraction; run only after the v4 pair completes.

Default writes a NEW edit/qa/final-v4-delta evidence tree; v2 QA is untouched.
--dry-run validates the sampling schedule without opening/decoding any video.
Native1920-pixel and375px boards cover only the eight changed cuts, joins,
retry states, captions80–83/90–93 and all corrected actual-mark anchors. Actual
mark samples also get original native source-frame comparisons. No model/ASR.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import json
import math
import re
import subprocess
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as audio
import video_pipeline as video

HERE=Path(__file__).resolve().parent


def balanced(terms):
    if len(terms)==1:return terms[0]
    m=len(terms)//2
    return '('+balanced(terms[:m])+'+'+balanced(terms[m:])+')'


def schedule(plan,captions):
    ids=plan['visualPatchV4']['pixelChangedBodyCutIds']
    if len(ids)!=8 or plan['totalFrames']!=17408:
        raise ValueError('Expected exactly the selected eight-cut v4 delta')
    cuts={c['id']:c for c in plan['cuts']};groups={k:[] for k in
        ['changed-cuts','joins','retry-states','examples80-83','examples90-93','world-handoff','actual-marks']}
    points={};native={}
    def add(n,group,label,**data):
        n=max(0,min(plan['totalFrames']-1,int(n)))
        row={'group':group,'label':label,'frame':n,'time':n/60,**data}
        groups[group].append(row);points.setdefault(n,[]).append(row)
        return row
    def at(t,group,label,**data):return add(round(t*60),group,label,**data)
    boundaries=set()
    for cid in ids:
        c=cuts[cid];a,b=c['startFrame'],c['endFrame'];boundaries.update([a,b])
        for tag,n in [('begin',a+8),('middle',(a+b)//2),('end',b-8)]:
            add(n,'changed-cuts',cid+' '+tag,cut=cid)
    for n in sorted(boundaries):
        for delta in [-6,-1,0,6]:
            add(n+delta,'joins',f'f{n} {delta:+d}',boundaryFrame=n)
    for cid in ['cut006','cut007']:
        c=cuts[cid];start=c['startFrame']/60;a,b=c['cues'][1:3];span=b-a
        for tag,t in [('before',a-.05),('approach',a+.20*span),('blocked',a+.33*span),
                      ('retry',a+.46*span),('detour-start',a+.51*span),('detour',a+.74*span),('goal',b+.05)]:
            at(start+t,'retry-states',cid+' '+tag,cut=cid,
               phaseBasis='Existing complete-mode u transitions .28/.42/.50; no invented game measurement')
    cue_by_id={c['cue']:c for c in captions}
    for numbers,group in [(range(80,84),'examples80-83'),(range(90,94),'examples90-93')]:
        for number in numbers:
            cue=cue_by_id[number]
            for tag,t in [('reveal',cue['start']+.15),('visible',min(cue['end']-.05,cue['start']+.65)),('end',cue['end']-.05)]:
                at(t,group,f'Cue{number:03d} '+tag,cue=number,ko=cue['ko'],en=cue['en'])
    for label,t in [('mining-last',208.14),('world-first',208.15),('world-voice',208.4),
                    ('world-result',210.76),('same-word',211.02),('diagram-first',211.35),
                    ('course-word',211.38),('side-by-side-word',211.86)]:
        at(t,'world-handoff',label,
           evidence='Root-reviewed source ASR word handoff and unchanged caption80–83 clock')
    for cid in ['cut018','cut022']:
        c=cuts[cid];fps=Fraction(c['sourceNativeFps']);source=c['source']
        for mark in c['marks']:
            local_times={key['t'] for key in mark.get('keyframes',[])}
            local_times.update([mark['t0']+.05,(mark['t0']+mark['t1'])/2,mark['t1']-.02])
            for t in sorted(local_times):
                if not mark['t0']<=t<mark['t1']:continue
                n=round(c['startFrame']+t*60)
                # Use the exact sampled OUTPUT frame's native playback time.
                native_time=c['sourceStart']+(n-c['startFrame'])/60
                source_frame=round(native_time*float(fps))
                row=add(n,'actual-marks',cid+' '+mark['id'].split('.')[-1],cut=cid,
                    mark=mark['id'],sourceId=source,sourceFrame=source_frame,
                    sourceTime=source_frame/float(fps),sourceFile=c['sourceFile'],
                    sourceSha256=c['sourceSha256'],viewport=c['viewport'])
                record=native.setdefault(source,{'path':c['sourceFile'],'sha256':c['sourceSha256'],
                    'fps':str(fps),'frames':{}})
                record['frames'].setdefault(source_frame,[]).append(row)
    return groups,points,native


def extract(file,numbers,directory,binary):
    directory.mkdir(parents=True,exist_ok=True)
    if any(directory.iterdir()):raise ValueError('Preserve existing/incomplete extraction; choose a new --version')
    ordered=sorted(numbers)
    expression=balanced([f'eq(n,{n})' for n in ordered])
    subprocess.run([binary,'-hide_banner','-nostdin','-loglevel','error','-threads','2',
        '-i',str(file),'-vf',"select='"+expression+"'",'-fps_mode','vfr','-frames:v',str(len(ordered)),
        '-compression_level','1','-threads','2','-n',str(directory/'%04d.png')],check=True)
    files=sorted(directory.glob('*.png'))
    if len(files)!=len(ordered):raise ValueError('Requested decoded frames were not all extracted')
    return dict(zip(ordered,files))


def board(records,mapping,qa,group,width):
    height=round(width*9/16);label_height=54 if width==1920 else 30
    per_page=4 if width==1920 else 8;rows=per_page//2
    font=ImageFont.truetype('C:/Windows/Fonts/NotoSansKR-VF.ttf',30 if width==1920 else 12)
    result=[]
    for offset in range(0,len(records),per_page):
        canvas=Image.new('RGB',(2*width,rows*(height+label_height)),'#151515');draw=ImageDraw.Draw(canvas)
        for i,row in enumerate(records[offset:offset+per_page]):
            x=(i%2)*width;y=(i//2)*(height+label_height)
            with Image.open(mapping[row['frame']]) as im:
                image=im.convert('RGB')
                if image.size!=(1920,1080):raise ValueError('Master evidence must remain native1920x1080')
                if width!=1920:image=image.resize((width,height),Image.Resampling.LANCZOS)
                canvas.paste(image,(x,y))
            label=f"{row['label']} | f{row['frame']} {row['time']:.3f}s"
            draw.text((x+5,y+height+4),label,font=font,fill='white')
        file=qa/f'{group}-{width}-{offset//per_page+1:02d}.jpg';canvas.save(file,quality=94)
        result.append(audio.artifact(file))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',default=str(HERE/'edit-plan-final-v4.json'))
    parser.add_argument('--version',default='final-v4-delta')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch(r'final-v4-delta(?:-[a-z0-9]+)*',args.version):
        raise ValueError('Only a separately versioned v4 delta QA directory is permitted')
    audio.require_authorized('selected v4 final pixel delta extraction')
    plan_file=audio.current_plan(args.plan);plan=audio.read(plan_file)
    local=audio.current_local_output(plan['outputDir']);caption_file=local/'captions.json'
    groups,points,native=schedule(plan,audio.read(caption_file)['cues'])
    qa=audio.current_local_output(local/'qa'/args.version)
    summary={'uniqueMasterFrames':len(points),'groups':{g:len(rows) for g,rows in groups.items()},
        'nativeSourceFrames':{s:len(r['frames']) for s,r in native.items()},
        'nativeBoardWidthPerFrame':1920,'mobileBoardWidthPerFrame':375,'directory':audio.relative(qa),
        'v2EvidenceDirectoryModified':False}
    if args.dry_run:
        print(json.dumps({'mode':'schedule-only-no-media-decode',**summary},ensure_ascii=False,indent=2));return
    master=local/(plan['outputStem']+'-captioned.mp4')
    video.assert_video(master,plan['totalFrames'])
    inputs={'master':audio.artifact(master),'plan':audio.artifact(plan_file),'captions':audio.artifact(caption_file),
        'helper':audio.artifact(Path(__file__)),'visualSource':plan['visualPatchV4']['visualSource'],
        'annotationSidecar':plan['visualPatchV4']['annotationSidecar']}
    receipt=qa/'frame-index.json'
    if receipt.exists():
        if audio.read(receipt)['inputs']!=inputs:raise ValueError('Existing QA belongs to different inputs; choose new --version')
        print('Identical v4 delta evidence reused');return
    qa.mkdir(parents=True,exist_ok=True)
    master_map=extract(master,points,qa/'frames',video.binary('ffmpeg'))
    boards=[]
    for group,records in groups.items():
        for width in [1920,375]:boards+=board(records,master_map,qa,group,width)
    source_records=[]
    for sid,record in native.items():
        source=audio.repo_path(record['path'])
        if audio.sha(source)!=record['sha256']:raise ValueError('Original source bytes changed')
        stream=video.video_stream(source)
        if stream['width']<1920 or stream['height']<1080:raise ValueError('Native source is below FHD')
        raw_map=extract(source,record['frames'],qa/('source-'+sid),video.binary('ffmpeg'))
        # Compare actual annotated final pixels to the corresponding untouched
        # native source. These are QA boards only, not new video assets.
        comparisons=[];comparison_map={};serial=0
        for n,records in sorted(record['frames'].items()):
            reference=records[0]
            for kind,file in [('encoded',master_map[reference['frame']]),('native',raw_map[n])]:
                comparisons.append({'frame':serial,'time':reference['time'],
                    'label':sid+' '+kind+f' source-f{n}'})
                comparison_map[serial]=file;serial+=1
            source_records.append({'sourceId':sid,'frame':n,'time':n/float(Fraction(record['fps'])),
                'file':audio.relative(raw_map[n]),'sha256':audio.sha(raw_map[n]),
                'masterFrame':reference['frame'],'sourceSha256':record['sha256']})
        for width in [1920,375]:boards+=board(comparisons,comparison_map,qa,'compare-'+sid,width)
    output={'status':'extracted-awaiting-direct-pixel-review','inputs':inputs,**summary,
        'groups':groups,'boards':boards,
        'frames':[{'frame':n,'time':n/60,'file':audio.relative(f),'sha256':audio.sha(f)} for n,f in sorted(master_map.items())],
        'nativeSourceComparisons':source_records,'actualHumanOrModelPixelReview':False,
        'wholeListening':False,'sourceOrMasterModified':False,'newAsrOrModelJob':False}
    audio.save(receipt,output)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
