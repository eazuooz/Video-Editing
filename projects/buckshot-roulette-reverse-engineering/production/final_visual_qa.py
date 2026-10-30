"""Prepare and, only on --extract, decode final caption/cut QA frames.

No video encoding, footage edits, new ASR or GPU work. The helper never marks a
frame visually reviewed or writes a passing visual-review.json. That requires
the reviewing agent to actually inspect the generated encoded-frame evidence.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import html
import json
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from assemble_documentary import (
    PROJECT,caption_ass,command,digest,load,now,probe,read_srt,resolve,save,
    shape,tool,video_stream,
)

FPS=60
CAPTION_RECT=[150,892,1784,1060]
FONT=Path('C:/Windows/Fonts/malgun.ttf')
MONO=Path('C:/Windows/Fonts/consola.ttf')


def relative(path):
    return str(Path(path).relative_to(PROJECT)).replace('\\','/')


def intersect(a,b):
    return min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1])


def time_label(seconds):
    return f'{int(seconds)//60:02}:{seconds%60:05.2f}'


def balanced_sum(terms):
    # FFmpeg's expression parser has a recursion limit: a flat 170-term sum
    # becomes a deeply left-nested tree. This tree needs only log2(N) levels.
    if len(terms)==1:return terms[0]
    midpoint=len(terms)//2
    return '('+balanced_sum(terms[:midpoint])+')+('+balanced_sum(terms[midpoint:])+')'


def wrap(text,font,width):
    lines=[];current=''
    for char in text:
        if current and font.getlength(current+char)>width:
            lines.append(current);current=char
        else:
            current+=char
    if current:lines.append(current)
    return lines or ['']


def marker_bounds(mark):
    if mark['type']=='text':
        size=mark.get('fontSize',48);font=ImageFont.truetype(str(FONT),size)
        return [mark['x'],mark['y'],mark['x']+font.getlength(mark['text']),mark['y']+size*1.25]
    if mark['type']=='code':
        return None  # The compositor owns detailed token bounds for code overlays.
    try:
        return list(shape(mark)[1])
    except (KeyError,ValueError):
        return None


def build_plan(timeline,timeline_path,out):
    if (timeline.get('width'),timeline.get('height'),timeline.get('fps'))!=(1920,1080,60):
        raise ValueError('Expected final FHD60 timeline')
    ko_source=resolve(timeline['narration']['koSrt'])
    original_cues=read_srt(ko_source)
    cues=[dict(c,start=c['start']+2,end=c['end']+2) for c in original_cues]
    selections={}
    cuts=[];position=120
    def add(frame,reason):
        frame=int(frame)
        if not 0<=frame<total_frames:
            raise ValueError('Frame outside final master')
        item=selections.setdefault(frame,{'frameIndex':frame,'seconds':frame/FPS,'requests':[]})
        if reason not in item['requests']:item['requests'].append(reason)
        return frame
    body_frames=sum(b['frames'] for b in timeline['beats'])
    if body_frames!=timeline.get('bodyFrameCount',body_frames):
        raise ValueError('Body length differs from current timeline')
    total_frames=body_frames+720
    for index,beat in enumerate(timeline['beats']):
        end=position+beat['frames']
        cuts.append({'id':beat['id'],'index':index+1,'startFrame':position,'endFrame':end,
                     'beat':beat,'source':timeline['sources'][beat['source']]})
        add(position-1,{'kind':'cut-boundary-before','cut':beat['id']})
        add(min(end-1,position+1),{'kind':'cut-boundary-after','cut':beat['id']})
        if beat['id'].startswith('intro-'):
            for frame in range(position, end, 30):
                add(frame,{'kind':'intro-motion-sequence-2fps','cut':beat['id']})
        position=end
    add(position-1,{'kind':'body-end-before-membership'})
    add(position+1,{'kind':'membership-start'})
    add(total_frames-2,{'kind':'final-frame'})
    add(60,{'kind':'branding-midpoint'})
    # Existing boundary frames may also serve a caption when nearly coincident.
    cue_samples=[]
    for cue in cues:
        first=math.ceil(cue['start']*FPS)
        last=math.ceil(cue['end']*FPS)-1
        if first>last:raise ValueError('Caption shorter than one visible frame')
        midpoint=min(last,max(first,round((cue['start']+cue['end'])*FPS/2)))
        nearby=[f for f in selections if first<=f<=last and abs(f-midpoint)<=2]
        frame=min(nearby,key=lambda f:abs(f-midpoint)) if nearby else midpoint
        add(frame,{'kind':'caption-midpoint','cue':cue['id']})
        cue_samples.append({'cue':cue['id'],'text':cue['text'],'start':cue['start'],'end':cue['end'],'frameIndex':frame})
    # Sample each distinct real annotation window near onset, middle and removal.
    for cut in cuts:
        intervals={}
        for number,mark in enumerate(cut['beat'].get('overlays',[])):
            pair=(float(mark.get('start',0)),float(mark.get('end',(cut['endFrame']-cut['startFrame'])/FPS)))
            intervals.setdefault(pair,[]).append(number)
        for (a,z),numbers in intervals.items():
            first=cut['startFrame']+math.ceil(a*FPS)
            last=cut['startFrame']+math.ceil(z*FPS)-1
            for role,frame in [('onset',min(last,first+2)),('middle',round((first+last)/2)),
                               ('before-hide',last),('after-hide',last+2)]:
                frame=min(cut['endFrame']-1,max(cut['startFrame'],frame))
                add(frame,{'kind':'annotation-'+role,'cut':cut['id'],'overlayIndices':numbers})
    # Reuse the compositor's exact caption geometry, without invoking FFmpeg.
    caption_layout=caption_ass(out/'expected-captions.ass',original_cues,2,timeline.get('captionEmphasis',{}))
    layouts={x['cue']:x for x in caption_layout}
    for item in selections.values():
        sec=item['seconds'];active=[c for c in cues if c['start']<=sec<c['end']]
        if len(active)>1:raise ValueError('Multiple simultaneous KO captions')
        item.update({'expectedCueIds':[c['id'] for c in active],'expectedCaption':' / '.join(c['text'] for c in active),
                     'expectedCaptionGeometry':[layouts[c['id']] for c in active],
                     'reviewStatus':'pending-direct-inspection','criticalReasons':[]})
        cut=next((c for c in cuts if c['startFrame']<=item['frameIndex']<c['endFrame']),None)
        if cut is None:
            item.update({'cutId':None,'sourceKind':'branding' if item['frameIndex']<120 else 'membership',
                         'activeAnnotations':[],'predictedCaptionIntersections':[]})
        else:
            local=(item['frameIndex']-cut['startFrame'])/FPS;beat=cut['beat'];marks=[]
            item.update({'cutId':cut['id'],'cutIndex':cut['index'],'sourceId':beat['source'],
                         'sourceKind':cut['source']['kind'],'sourceSeconds':beat['sourceInSeconds']+local*beat.get('speed',1),
                         'observedAction':beat['observedAction'],'narrationConnection':beat['narrationConnection']})
            for i,m in enumerate(beat.get('overlays',[])):
                if m.get('start',0)<=local<m.get('end',beat['frames']/FPS):
                    marks.append({'index':i,'type':m['type'],'label':m.get('text'),
                                  'role':m.get('role'),'predictedBounds':marker_bounds(m)})
            item['activeAnnotations']=marks
            intersections=[]
            for m in marks:
                if m['predictedBounds'] and intersect(m['predictedBounds'],CAPTION_RECT):intersections.append(m['index'])
            item['predictedCaptionIntersections']=intersections
            if marks:item['criticalReasons'].append('active-footage-annotation')
            if beat['source'].startswith('06-'):item['criticalReasons'].append('owned-code-or-integration-explanation')
            if beat['source'].startswith('05-'):item['criticalReasons'].append('AI-branch-and-small-labels')
        if any(len(c['lines'])>1 for c in item['expectedCaptionGeometry']):
            item['criticalReasons'].append('two-line-caption')
    rows=[selections[k] for k in sorted(selections)]
    if any(r['predictedCaptionIntersections'] for r in rows):
        raise ValueError('Expected annotation bounds overlap caption region; fix before extraction')
    master=resolve(timeline['outputDirectory'])/(timeline['outputStem']+'.captioned.mp4')
    return {'schemaVersion':1,'preparedAtUtc':now(),'status':'prepared-not-extracted',
            'timelinePath':str(timeline_path.resolve()),'timelineSha256':digest(timeline_path),
            'master':str(master),'koSourceSrt':str(ko_source),'koSourceSrtSha256':digest(ko_source),
            'brandingOffsetSeconds':2,'fps':FPS,'width':1920,'height':1080,
            'totalFrames':total_frames,'captionCueCount':len(cues),'cutCount':len(cuts),
            'uniqueSelectedFrames':len(rows),'captionSamples':cue_samples,'frames':rows,
            'cutCoverage':[{'id':c['id'],'startFrame':c['startFrame'],'endFrame':c['endFrame'],
                            'selectedFrames':[r['frameIndex'] for r in rows if r.get('cutId')==c['id']]} for c in cuts],
            'layoutEvidence':'Predicted bounds checked against compositor caption geometry; actual pixels still require review',
            'humanReview':False,'humanListening':False,'fullRealtimePlaybackReviewed':False}


def verify_final_srt(timeline,selection):
    final_srt=resolve(timeline['outputDirectory'])/(timeline['outputStem']+'.ko.srt')
    actual=read_srt(final_srt)
    expected=selection['captionSamples']
    if len(actual)!=len(expected):raise ValueError('Final SRT cue count differs')
    for a,b in zip(actual,expected):
        if a['text']!=b['text'] or abs(a['start']-b['start'])>.002 or abs(a['end']-b['end'])>.002:
            raise ValueError(f'Final SRT differs at cue {a["id"]}; regenerate selection')
    return final_srt


def extract(timeline,selection,out,allow_audio_mismatch=False):
    progress_path=resolve(timeline['workDirectory'])/'render-progress.json'
    if not progress_path.is_file() or not load(progress_path).get('complete'):
        raise ValueError('Final render is not marked complete; do not read the in-progress master')
    master=Path(selection['master'])
    if not master.is_file():raise FileNotFoundError(master)
    final_srt=verify_final_srt(timeline,selection)
    before=master.stat();master_hash=digest(master)
    meta=probe(master,timeline);v=video_stream(meta)
    if (v['width'],v['height'],Fraction(v['avg_frame_rate']))!=(1920,1080,60):
        raise ValueError('Final master format differs from requested FHD60')
    if v.get('nb_frames') and int(v['nb_frames'])!=selection['totalFrames']:
        raise ValueError('Final master frame count differs from timeline')
    expected_duration=selection['totalFrames']/FPS
    video_duration=float(v.get('duration',meta['format']['duration']))
    if abs(video_duration-expected_duration)>.05:
        raise ValueError('Final video stream duration differs from timeline')
    audio_durations=[float(s.get('duration',meta['format']['duration'])) for s in meta['streams'] if s['codec_type']=='audio']
    duration_mismatch=any(abs(d-expected_duration)>.05 for d in audio_durations)
    if duration_mismatch and not allow_audio_mismatch:
        raise ValueError('Final audio duration differs from video; visual-only override requires explicit parent direction')
    frame_dir=out/'frames'/master_hash[:16];frame_dir.mkdir(parents=True,exist_ok=True)
    packet_hash=frame_dir/'video-packet-sha256.txt'
    command([tool('ffmpeg',timeline),'-hide_banner','-v','warning','-nostdin','-y','-i',str(master),
             '-map','0:v:0','-an','-c:v','copy','-f','hash','-hash','sha256',str(packet_hash)],frame_dir/'packet-hash.log')
    video_packet_hash=packet_hash.read_text(encoding='utf-8').strip().split('=',1)[-1]
    selected=selection['frames']
    expression=balanced_sum([f'eq(n\\,{r["frameIndex"]})' for r in selected])
    selection_key=digest(out/'selection.json')
    cache=frame_dir/'decode-receipt.json'
    reuse=False
    if cache.is_file():
        prior=load(cache)
        reuse=(prior.get('masterSha256')==master_hash and prior.get('selectedFrames')==[r['frameIndex'] for r in selected]
               and all((frame_dir/f'decoded-{i+1:05}.png').is_file() for i in range(len(selected))))
    if not reuse:
        args=[tool('ffmpeg',timeline),'-hide_banner','-v','warning','-nostdin','-y','-threads','2','-filter_threads','1',
              '-i',str(master),'-map','0:v:0','-an','-vf','select='+expression,'-fps_mode','vfr',
              '-frames:v',str(len(selected)),'-threads','1',str(frame_dir/'decoded-%05d.png')]
        command(args,frame_dir/'decode.log')
        save(cache,{'decodedAtUtc':now(),'masterSha256':master_hash,'selectedFrames':[r['frameIndex'] for r in selected],
                    'command':args,'kind':'sparse PNG extraction only; no video encode'})
    after=master.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise ValueError('Master changed during extraction; do not review mixed versions')
    for i,row in enumerate(selected):
        png=frame_dir/f'decoded-{i+1:05}.png'
        image=Image.open(png).convert('RGB')
        if image.size!=(1920,1080):raise ValueError('Decoded frame size differs')
        mobile=frame_dir/f'decoded-{i+1:05}.mobile.png'
        image.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
        row.update({'image':relative(png),'imageSha256':digest(png),'mobileImage':relative(mobile),
                    'mobileImageSha256':digest(mobile)})
        if row['criticalReasons']:
            crop=frame_dir/f'decoded-{i+1:05}.caption.png'
            image.crop(tuple(CAPTION_RECT)).save(crop)
            row['nativeCaptionCrop']=relative(crop)
    selection.update({'status':'extracted-awaiting-direct-inspection','extractedAtUtc':now(),'masterSha256':master_hash,
                      'finalKoSrtSha256':digest(final_srt),'finalKoSrt':str(final_srt),
                      'probe':meta,'decodeCacheReused':reuse,'videoPacketSha256':video_packet_hash,
                      'videoStreamDurationSeconds':video_duration,'audioStreamDurationsSeconds':audio_durations,
                      'audioDurationMismatch':duration_mismatch,'overallTechnicalPass':False,
                      'audioRepairRequired':duration_mismatch,
                      'knownAudioIssueNote':'Parent-authorized visual-only inspection; bind to a repaired master only after stream-identity verification' if duration_mismatch else None})
    save(out/'sampling-report.json',selection)
    contacts(out,selection)


def contacts(out,selection):
    destination=out/'contact-sheets'/selection['masterSha256'][:16]
    destination.mkdir(parents=True,exist_ok=True)
    small=ImageFont.truetype(str(FONT),18);mono=ImageFont.truetype(str(MONO),18)
    pages=[]
    rows=selection['frames']
    for offset in range(0,len(rows),8):
        chosen=rows[offset:offset+8]
        # Eight frames per sheet: all are actual full-frame pixels, never crops.
        sheet=Image.new('RGB',(1920,740),'#202424');draw=ImageDraw.Draw(sheet)
        mobile_sheet=Image.new('RGB',(1500,602),'#202424');md=ImageDraw.Draw(mobile_sheet)
        for i,row in enumerate(chosen):
            x=i%4*480;y=i//4*370
            source=Image.open(PROJECT/row['image']).convert('RGB')
            label=f'F{row["frameIndex"]:05} {time_label(row["seconds"])} C{",".join(map(str,row["expectedCueIds"])) or "-"}'
            draw.text((x+8,y+4),label,font=mono,fill='white')
            draw.text((x+8,y+26),row.get('cutId') or row['sourceKind'],font=mono,fill='#E8CF83')
            sheet.paste(source.resize((480,270),Image.Resampling.LANCZOS),(x,y+50))
            for j,line in enumerate(wrap(row['expectedCaption'],small,464)[:2]):
                draw.text((x+8,y+321+j*23),line,font=small,fill='white')
            mx=i%4*375;my=i//4*301
            md.text((mx+5,my+4),label,font=mono,fill='white')
            md.text((mx+5,my+25),row.get('cutId') or row['sourceKind'],font=mono,fill='#E8CF83')
            mobile_sheet.paste(Image.open(PROJECT/row['mobileImage']),(mx,my+48))
            for j,line in enumerate(wrap(row['expectedCaption'],small,365)[:2]):
                md.text((mx+5,my+260+j*19),line,font=small,fill='white')
        page=destination/f'page-{offset//8+1:03}.jpg';mobile_page=destination/f'page-{offset//8+1:03}.mobile.png'
        sheet.save(page,quality=95);mobile_sheet.save(mobile_page)
        pages.append({'page':offset//8+1,'path':relative(page),'mobilePath':relative(mobile_page),
                      'frames':[r['frameIndex'] for r in chosen],'reviewStatus':'pending-direct-inspection'})
    save(out/'contact-sheet-index.json',{'masterSha256':selection['masterSha256'],'pages':pages,
         'instruction':'Inspect all pages and critical native frames. Record what was actually viewed in a separate visual-review.json; do not infer human playback.'})
    links=''.join(f'<li><a href="../../../../{html.escape(p["path"])}">Page {p["page"]}</a></li>' for p in pages)
    # Relative links are generated from exact paths instead of assuming a server root.
    import os
    links=''.join(f'<li><a href="{html.escape(os.path.relpath(PROJECT/p["path"],out).replace(chr(92),"/"))}">Page {p["page"]}</a> · '
                  f'<a href="{html.escape(os.path.relpath(PROJECT/p["mobilePath"],out).replace(chr(92),"/"))}">375px sheet</a></li>' for p in pages)
    title='최종 인코딩 화면 검수'
    body=f'<!doctype html><html lang="ko"><meta charset="utf-8"><title>{title}</title><style>body{{background:#101414;color:#eee;font:18px/1.6 system-ui;max-width:1100px;margin:40px auto}}a{{color:#73c7c2}}h1{{color:#e8cf83}}</style><h1>{title}</h1><p>자막 {selection["captionCueCount"]}개 · 컷 {selection["cutCount"]}개 · 고유 프레임 {len(rows)}장</p><p>실제 완성본에서 추출한 정지 프레임 검수입니다. 전체 재생·청취나 사용자 검수를 뜻하지 않습니다.</p><ul>{links}</ul></html>'
    (out/'index.html').write_text(body,encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--timeline',type=Path,default=PROJECT/'production/timeline.json')
    ap.add_argument('--out',type=Path,default=PROJECT/'production/local/final-qa')
    ap.add_argument('--extract',action='store_true',help='Run only after parent signals the final master is complete')
    ap.add_argument('--allow-audio-mismatch-for-visual-qa',action='store_true',
                    help='Parent-directed video-only inspection while a known audio remux repair is pending')
    args=ap.parse_args();out=args.out.resolve()
    if not out.is_relative_to((PROJECT/'production/local').resolve()):
        raise ValueError('QA output must remain in this project ignored production/local')
    out.mkdir(parents=True,exist_ok=True)
    timeline=load(args.timeline)
    selection=build_plan(timeline,args.timeline,out)
    save(out/'selection.json',selection)
    print(f'Prepared {selection["captionCueCount"]} caption samples, {selection["cutCount"]} cuts, '
          f'{selection["uniqueSelectedFrames"]} unique frames; no inspection claimed')
    if args.extract:
        extract(timeline,selection,out,args.allow_audio_mismatch_for_visual_qa)
        print(f'Extracted frames + eight-per-page contact sheets: {out}; direct review is pending')


if __name__=='__main__':
    main()
