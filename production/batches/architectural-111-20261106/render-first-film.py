"""Finite CPU compositor for the first03.02 film; default is read-only validation.

The future ASR-aligned timeline is authored by build-first-timeline.py. This
module starts no process when imported or when validating. --execute is a
separate, explicit invocation: one fresh selected C-media attempt, one AAC
encode, two software video encoders and packet-copy muxes. No GPU encoder,
engine, model, app, platform, metadata, replacement or next-film operation.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = ROOT/'projects/shorts-leveldesign-03-02'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-03-02')
SLUG = 'shorts-leveldesign-03-02'
FPS = 60
SIZE = (1080, 1920)
CREATE = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def integer(value):
    return type(value) is int


def interval(row):
    start, end = row.get('startFrame'), row.get('endFrameExclusive')
    if not integer(start) or not integer(end) or not 0 <= start < end:
        raise ValueError('Exact integer, positive, end-exclusive frame interval required')
    return start, end


GUIDE_PARTS=('clearance','footprint','input')


def guide_request(section,frame):
    cues=[c for c in section.get('annotationCues',[]) if c.get('kind')=='native-guides' and c['startFrame']<=frame<c['endFrameExclusive']]
    if not cues:return dict(enabled=False,reviewedBundle=False,parts=())
    if any('guideParts' not in c for c in cues):
        return dict(enabled=True,reviewedBundle=True,parts=GUIDE_PARTS)
    parts=set(p for c in cues for p in c['guideParts'])
    return dict(enabled=True,reviewedBundle=False,parts=tuple(p for p in GUIDE_PARTS if p in parts))


def validate_structure(timeline):
    """Pure CPU contract validation; no files/processes and no proof invented."""
    if timeline.get('schemaVersion') != '03-02-final-timeline-v1':
        raise ValueError('Unsupported first-film timeline schema')
    if timeline.get('format') != dict(width=1080, height=1920, fps=60):
        raise ValueError('Exact1080x1920/60fps timeline required')
    total = timeline.get('totalFrames')
    if not integer(total) or total <= 0:
        raise ValueError('Positive exact totalFrames required')
    sections = timeline.get('sections')
    if not isinstance(sections, list) or not sections:
        raise ValueError('A complete ordered picture timeline is required')
    previous = 0
    moving = dict(narrow=[], wide=[])
    native_modes = set()
    game_intervals = {}
    ids = set()
    for section in sections:
        start, end = interval(section)
        if start != previous or end > total:
            raise ValueError('Picture cuts must cover every output frame once, without gaps/overlap')
        previous = end
        if not section.get('id') or section['id'] in ids:
            raise ValueError('Unique section ID required')
        ids.add(section['id'])
        kind = section.get('kind')
        if kind == 'gameplay':
            if section.get('rate') != 1 or isinstance(section.get('rate'), bool):
                raise ValueError('Actual gameplay must retain1x source motion')
            if section.get('holdPolicy') or section.get('loop') or section.get('interpolate'):
                raise ValueError('No held/looped/interpolated gameplay')
            pts = section.get('sourceLocalInPts')
            if isinstance(pts, bool) or not isinstance(pts, (int, float)) or not math.isfinite(pts) or pts < 0:
                raise ValueError('A finite decoded local source PTS is required')
            if not all(isinstance(section.get(key), str) and section[key] for key in ('sourceId','sourcePath','sourceSHA256')):
                raise ValueError('Gameplay source identity/path/hash required')
            window = (float(pts), float(pts)+(end-start)/FPS)
            for a, b in game_intervals.setdefault(section['sourceId'], []):
                if min(b, window[1])-max(a, window[0]) > .000001:
                    raise ValueError('Repeated gameplay source interval would create reused/looped motion')
            game_intervals[section['sourceId']].append(window)
        elif kind in ('native', 'illustration'):
            native = section.get('native', {})
            mode = native.get('mode')
            if mode not in moving or native.get('layout') not in ('dual','single-observer','single-top'):
                raise ValueError('Only the existing two native camera layouts are permitted')
            native_modes.add(mode)
            if native.get('playbackRate') != 1 or isinstance(native.get('playbackRate'), bool):
                raise ValueError('Native simulation playback is1x')
            first, count = native.get('startNativeFrame'), native.get('frameCount')
            if not integer(first) or not integer(count) or not 0 <= first < 270 or not 1 <= count <= 270-first:
                raise ValueError('Native frames must remain inside the actual0..269 capture')
            hold = native.get('holdPolicy')
            if hold is not None:
                if not isinstance(hold, dict) or hold.get('frame') != first or count != 1 or not isinstance(hold.get('reason'), str) or not hold['reason'].strip():
                    raise ValueError('Explanation still requires an exact actual frame and teaching reason')
            else:
                if kind == 'illustration' or count != end-start:
                    raise ValueError('Native1x moving duration must equal exact captured frame count')
                moving[mode].extend(range(first, first+count))
            if native['layout'] == 'dual' and section.get('catPose'):
                raise ValueError('Cat must not cover the two-camera comparison')
        else:
            raise ValueError('Only actual gameplay or the existing native scene is routable')
        if section.get('catPose') not in (None,'puzzled','realize','relief'):
            raise ValueError('Use an approved original cat pose')
        for cue in section.get('catCues', []):
            a,b=interval(cue)
            if not start<=a<b<=end or cue.get('pose') not in ('puzzled','realize','relief'):
                raise ValueError('Cat cue must remain within its own section')
            if section['kind']!='gameplay' and section['native']['layout']=='dual':
                raise ValueError('Cat cue cannot obscure a dual native view')
            if any(not integer(cue.get(k)) or not 0<=cue[k]<=b-a for k in ('easeInFrames','easeOutFrames')):
                raise ValueError('Explicit bounded reaction entrance/exit frames required')
        for chip in section.get('termChips', []):
            if chip.get('presentation') not in ('definition','chip') or not all(isinstance(chip.get(k), str) and chip[k].strip() for k in ('english','korean','meaning')):
                raise ValueError('Canonical term card requires English/Korean/plain meaning')
        illustration=section.get('illustrationOverlay')
        if illustration is not None:
            if kind!='illustration' or illustration.get('kind')!='purpose-contrast' or not all(
                isinstance(illustration.get(k),str) and illustration[k].strip()
                for k in ('heading','routeLabel','enemyLabel','resultLabel','narrowPurposeLabel',
                          'widePurposeLabel','narrowActionLabel','wideActionLabel')):
                raise ValueError('Only the explicitly labelled purpose-contrast concept overlay is supported')
        for cue in section.get('annotationCues', []):
            a, b = interval(cue)
            expected = 'opening-tracks' if kind == 'gameplay' else 'native-guides'
            if cue.get('kind') != expected or not start <= a < b <= end:
                raise ValueError('Unsupported annotation or cue outside its own source cut')
            if 'guideParts' in cue:
                parts=cue['guideParts']
                if expected!='native-guides' or not isinstance(parts,list) or not parts or len(parts)!=len(set(parts)) or any(p not in GUIDE_PARTS for p in parts):
                    raise ValueError('Native guide parts must name the supported same-geometry components')
    if previous != total:
        raise ValueError('Picture timeline ends before totalFrames')
    for mode in native_modes:
        if moving[mode] != list(range(270)):
            raise ValueError('Each used native moving clock must cover0..269 exactly once, in order')
    previous_cat_end=0
    for cue in timeline.get('catCues',[]):
        a,b=interval(cue)
        if a<previous_cat_end or b>total or cue.get('pose') not in ('puzzled','realize','relief'):
            raise ValueError('Global reaction cues must not overlap or leave the film')
        previous_cat_end=b
        if any(not integer(cue.get(k)) or not 0<=cue[k]<=b-a for k in ('easeInFrames','easeOutFrames')):
            raise ValueError('Global reaction entrance/exit needs exact bounded frames')
        for section in sections:
            if min(b,section['endFrameExclusive'])>max(a,section['startFrame']):
                if section['kind']!='gameplay' and section['native']['layout']=='dual':
                    raise ValueError('Global cat reaction would obscure a dual native view')
                if section.get('catPose'):
                    raise ValueError('Global reaction and static cat pose overlap')
    previous_end = 0
    for cue in timeline.get('captions', []):
        start, end = interval(cue)
        if start < previous_end or end > total:
            raise ValueError('Caption cues must be ordered, clear at cuts and never overlap')
        previous_end = end
        for lang in ('ko', 'en'):
            text = cue.get(lang)
            lines = cue.get(lang+'Lines')
            if not isinstance(text, str) or not text.strip() or not isinstance(lines, list) or not 1 <= len(lines) <= 2 or any(not isinstance(line, str) or not line.strip() for line in lines):
                raise ValueError('Every caption needs complete KO/EN clauses and one/two display lines')
            if ''.join(text.split()) != ''.join(''.join(lines).split()):
                raise ValueError('Caption line wrapping must preserve every actual word')
    if not timeline.get('captions'):
        raise ValueError('Timed complete KO/EN captions are required')
    return dict(totalFrames=total, durationSeconds=total/FPS,
                nativeMovingFrames={m:len(v) for m,v in moving.items()},
                gameIntervals=game_intervals, sections=len(sections), captions=len(timeline['captions']))


def bound_file(record, role):
    if not isinstance(record, dict) or not all(isinstance(record.get(k), str) and record[k] for k in ('path','sha256')):
        raise ValueError('Missing bound '+role)
    path = Path(record['path'])
    if not path.is_file() or sha(path) != record['sha256']:
        raise ValueError('Missing/changed '+role+': '+str(path))
    return path


def caption_emphasis(cue,lang='ko'):
    """Map one authored-clause span onto the actual wrapped display line."""
    emphasis=cue.get('emphasis')
    if emphasis is None:return None
    if isinstance(emphasis,dict):
        spans=emphasis.get(lang,[])
        if not spans:return None
        if len(spans)!=1:raise ValueError('At most one semantic caption emphasis is permitted')
        span=spans[0];start,end=span.get('start'),span.get('end');text=cue[lang]
        if not integer(start) or not integer(end) or not 0<=start<end<=len(text):
            raise ValueError('Caption emphasis must point into the authored clause')
        raw=[i for i,ch in enumerate(text) if not ch.isspace()]
        positions=[(row,column) for row,line in enumerate(cue[lang+'Lines']) for column,ch in enumerate(line) if not ch.isspace()]
        selected=[positions[i] for i,original in enumerate(raw) if start<=original<end]
        if not selected or len({p[0] for p in selected})!=1:
            raise ValueError('Caption emphasis must remain in one readable display line')
        return selected[0][0],selected[0][1],selected[-1][1]+1,span['role']
    if isinstance(emphasis,(list,tuple)) and len(emphasis)==4:
        return tuple(emphasis)
    raise ValueError('Unsupported caption emphasis shape')


def verify_inputs(timeline, require_mix=True):
    result = validate_structure(timeline)
    if timeline.get('status') != 'final-asr-aligned':
        raise ValueError('Current exact voice/ASR alignment is not ready')
    rows = timeline.get('inputs', [])
    for row in rows:
        bound_file(row, row.get('role','timeline input'))
    narration = [r for r in rows if r.get('role') == 'narration']
    if len(narration) != 1 or Path(narration[0]['path']).resolve() != (PROJECT/'narration-voice-v1.json').resolve():
        raise ValueError('Timeline must bind the current selected narration, not the superseded retake')
    if not any(r.get('role') in ('asr','blind-asr-evidence') for r in rows) or not any(r.get('role') in ('voice','voice-aggregate','voice-evidence') for r in rows):
        raise ValueError('Actual voice and blind ASR proof bindings are required')
    visual_roles={'layout':PROJECT/'visual-layout-v1.json',
        'native-helper':PROJECT/'production/composite-native-frame.py',
        'game-helper':PROJECT/'production/composite-game-frame.py'}
    for role,path in visual_roles.items():
        selected=[r for r in rows if r.get('role')==role]
        if len(selected)!=1 or Path(selected[0]['path']).resolve()!=path.resolve():
            raise ValueError('Missing current '+role+' visual binding')
    tracks=[r for r in rows if r.get('role')=='tracking']
    if len(tracks)!=1 or Path(tracks[0]['path']).resolve() not in {
            (PROJECT/'opening-cart-tracking-v1.json').resolve(),(PROJECT/'opening-cart-tracking-v2.json').resolve()}:
        raise ValueError('A checked project-local object track binding is required')
    for lang in ('ko','en'):
        bound_file(timeline.get('subtitles',{}).get(lang), lang+' SRT')
    # Catch overwide/invalid clauses before a costly encode. This measures the
    # actual shared font/box, without pretending to have watched encoded video.
    native=load_module('firstfilm_caption_preflight',PROJECT/'production/composite-native-frame.py').NativeFrameComposer()
    for cue in timeline['captions']:
        for lang in ('ko','en'):
            native._captions(Image.new('RGB',(1,1)),tuple(cue[lang+'Lines']),caption_emphasis(cue,lang))
    sources = {s['id']:s for s in read(PROJECT/'source-footage.json')['sources'] if s.get('selectedForCut')}
    for section in timeline['sections']:
        if section['kind'] != 'gameplay':
            continue
        source = sources.get(section['sourceId'])
        if not source or source['sha256'] != section['sourceSHA256'] or Path(source['path']).resolve() != Path(section['sourcePath']).resolve():
            raise ValueError('Gameplay cut is not the current selected independent source')
        bound_file(dict(path=source['path'],sha256=source['sha256']), 'gameplay source')
        duration = (section['endFrameExclusive']-section['startFrame'])/FPS
        if section['sourceLocalInPts']+duration > float(source['duration'])+.000001:
            raise ValueError('Gameplay window runs past the bound source')
    audio = timeline.get('audio', {})
    voice=audio.get('voice',audio)
    voice_path=bound_file(voice,'current voice WAV')
    import soundfile as sf
    voice_info=sf.info(voice_path)
    if (voice_info.samplerate,voice_info.channels,voice_info.frames)!=(voice.get('sampleRate'),voice.get('channels'),voice.get('frames')):
        raise ValueError('Current voice actual sample properties differ from timeline')
    mix = audio.get('mix')
    if mix is None:
        if require_mix:
            raise ValueError('Final hash-bound voice/BGM mix is not ready; no audio is fabricated')
        result['audioMixReady'] = False
    else:
        path = bound_file(mix, 'final audio mix')
        info = sf.info(path)
        if (info.samplerate,info.channels,info.frames) != (mix.get('sampleRate'),mix.get('channels'),mix.get('frames')):
            raise ValueError('Audio mix actual sample properties differ from timeline')
        if not all(isinstance(voice.get(k),int) and voice[k] > 0 for k in ('frames','sampleRate')):
            raise ValueError('Actual original voice sample count/rate required')
        if abs(info.frames/info.samplerate-voice['frames']/voice['sampleRate']) > 1/info.samplerate:
            raise ValueError('Mix changed the original voice duration')
        if timeline['totalFrames'] != math.ceil(info.frames*FPS/info.samplerate):
            raise ValueError('Film clock must cover the exact mix with less than one frame rounding')
        result['audioMixReady'] = True
    return result


def fresh_authorization():
    """Read the live exact111 local-production boundary; never mutate it."""
    control=read(ROOT/'shared/publishing/video-production-control.json')
    grant=control.get('explicitArchitectural111Batch20261106',{})
    batch=read(HERE/'batch.json');project=read(PROJECT/'project.json')
    if grant.get('status') in ('paused','stopped','cancelled','canceled'):
        raise ValueError('Selected batch is explicitly stopped')
    if (grant.get('id')!='explicitArchitectural111Batch20261106' or
        grant.get('batch')!='production/batches/architectural-111-20261106/batch.json' or
        not batch.get('fullProductionAuthorized') or not batch.get('localFinalReviewOnly') or
        project.get('slug')!=SLUG or project.get('topicId')!='03.02' or
        not any(p.get('slug')==SLUG and p.get('topicId')=='03.02' for p in batch.get('projects',[]))):
        raise ValueError('Exact selected first-film local production is not authorized')
    return dict(authorizationId=grant['id'],scope=grant.get('scope'),localFinalReviewOnly=True,
        controlReadSHA256=sha(ROOT/'shared/publishing/video-production-control.json'))


def run(command, log):
    fresh_authorization()
    with Path(log).open('xb') as handle:
        result = subprocess.run([str(x) for x in command],stdout=subprocess.DEVNULL,stderr=handle,creationflags=CREATE)
    if result.returncode:
        raise RuntimeError('Scoped ffmpeg command failed; see '+str(log))


def binaries():
    ffmpeg = os.environ.get('YAMYAM_FFMPEG') or shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('ffmpeg not found')
    ffprobe = str(Path(ffmpeg).with_name('ffprobe.exe' if os.name == 'nt' else 'ffprobe'))
    if not Path(ffprobe).is_file():
        raise RuntimeError('Matching ffprobe not found')
    return ffmpeg, ffprobe


def probe_pts(source, ffprobe):
    command = [ffprobe,'-v','error','-threads','1','-select_streams','v:0','-show_frames',
        '-show_entries','frame=best_effort_timestamp_time,width,height','-of','json',source]
    response = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE)
    if response.returncode:
        raise RuntimeError('Decoded source PTS inspection failed')
    rows = json.loads(response.stdout)['frames']
    if not rows or any((r.get('width'),r.get('height')) != (1920,1080) for r in rows):
        raise ValueError('Every actual decoded gameplay frame must be FHD')
    pts = [float(r['best_effort_timestamp_time']) for r in rows]
    pts = [p for p in pts if p >= 0]
    if not pts or any(not math.isfinite(p) for p in pts) or any(a >= b for a,b in zip(pts,pts[1:])):
        raise ValueError('Decoded source PTS must be finite and strictly increasing')
    return pts


class CutDecoder:
    """One streaming decoder per cut, actual PTS scheduling, no per-frame launch."""
    def __init__(self, source, pts, start, frames, ffmpeg, log):
        self.pts = pts
        first = bisect.bisect_right(pts,start+.000001)-1
        last_time = start+(frames-1)/FPS
        last = bisect.bisect_right(pts,last_time+.000001)-1
        if first < 0 or last < first or last >= len(pts):
            raise ValueError('Gameplay cut has no valid presented source frames')
        self.selected = pts[first:last+1]
        self.index = -1
        self.image = None
        self.last_desired = -1.
        self.log = Path(log).open('xb')
        selection = f"select='between(t,{self.selected[0]-.0000005:.7f},{self.selected[-1]+.0000005:.7f})'"
        self.process = subprocess.Popen([ffmpeg,'-hide_banner','-nostdin','-threads','1','-i',str(source),
            '-vf',selection,'-fps_mode','passthrough','-frames:v',str(len(self.selected)),
            '-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=self.log,creationflags=CREATE)

    def at(self, desired):
        if desired < self.last_desired:
            raise ValueError('No backwards motion/loop inside a gameplay cut')
        self.last_desired = desired
        # ffprobe serializes thirds of a millisecond to6 decimals. One micro-
        # second tolerance preserves exact30→60 cadence without a late frame.
        while self.index+1 < len(self.selected) and self.selected[self.index+1] <= desired+.000001:
            data = self.process.stdout.read(1920*1080*3)
            if len(data) != 1920*1080*3:
                raise RuntimeError('Truncated source decode; never hold a missing frame')
            self.image = Image.frombytes('RGB',(1920,1080),data)
            self.index += 1
        if self.image is None:
            raise RuntimeError('No actual source frame at requested PTS')
        return self.image,self.selected[self.index]

    def close(self, failed=False):
        self.process.stdout.close()
        if failed and self.process.poll() is None:
            self.process.terminate()  # This exact helper-owned decoder only.
        code = self.process.wait(timeout=30)
        self.log.close()
        if code and not failed:
            raise RuntimeError('Source decoder did not finish cleanly')


class FrameRouter:
    def __init__(self,timeline,work,ffmpeg,ffprobe):
        self.timeline=timeline;self.work=Path(work);self.ffmpeg=ffmpeg;self.ffprobe=ffprobe
        self.native_module=load_module('firstfilm_native_frames',PROJECT/'production/composite-native-frame.py')
        self.game_module=load_module('firstfilm_game_frames',PROJECT/'production/composite-game-frame.py')
        self.native=self.native_module.NativeFrameComposer()
        track=next(r for r in timeline['inputs'] if r.get('role')=='tracking')
        self.game=self.game_module.GameFrameComposer(tracking_path=track['path'])
        self.style=self.native
        self.starts=[s['startFrame'] for s in timeline['sections']]
        self.caption_starts=[c['startFrame'] for c in timeline['captions']]
        self.current_section=None;self.decoder=None;self.pts_cache={};self.cut_counter=0
        self.hold_cache={}
        self.game_last_key=None;self.game_last_result=None

    def caption_at(self,frame):
        index=bisect.bisect_right(self.caption_starts,frame)-1
        cue=self.timeline['captions'][index] if index>=0 else None
        return cue if cue and frame<cue['endFrameExclusive'] else None

    def _guide_parts(self,image,row,layout,parts):
        """Progressive editorial components, same native coordinates/camera/tokens."""
        if layout not in ('dual','single-top'):
            return image,dict(parts=list(parts),shown=False,reason='No top camera in this layout')
        image=image.copy();draw=ImageDraw.Draw(image);upper=layout=='single-top'
        spec=self.native.spec;tokens=self.native.tokens
        cfg=spec['nativeCropMaps']['editorialPostOverlay'];point=self.native._top_point
        cart=next(t for t in spec['overlayTargets'] if t['id']=='cart-footprint')
        x,z=float(row['playerX']),float(row['playerZ']);radius=float(row['playerDiameter'])/2
        center=point(x,z,upper);blocked=row['blocked']=='1';passed=z-radius>cart['size'][2]/2
        role='problem' if blocked else 'result' if passed else 'relationship';color=tokens[role]
        shown=[];input_target=None
        if 'clearance' in parts:
            a=point(cart['size'][0]/2,cfg['clearanceSampleWorldZ'],upper)
            b=point(float(row['width'])/2,cfg['clearanceSampleWorldZ'],upper)
            draw.line([a,b],fill=tokens['title'],width=cfg['strokeNativeCompositePx'])
            tick=cfg['endpointTickPx']/2
            for p in (a,b):draw.line([(p[0]-tick,p[1]),(p[0]+tick,p[1])],fill=tokens['title'],width=8)
            if not upper:
                self.style.text(draw,'사람이 지날 틈',(700,1133),40,tokens['title'])
                mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
                draw.line([(610,1158),(mid[0]+16,mid[1])],fill=tokens['title'],width=4)
            shown.append('clearance')
        if 'footprint' in parts:
            circle=[point(x+radius*math.cos(i*math.pi/48),z+radius*math.sin(i*math.pi/48),upper) for i in range(97)]
            draw.line(circle,fill=color,width=cfg['strokeNativeCompositePx'],joint='curve')
            if not upper:
                lx=720 if center[0]>650 else 210
                self.style.text(draw,'충돌 영역',(lx,1408),40,color)
                draw.line([(lx,1380),(center[0],center[1]+31)],fill=color,width=4)
            shown.append('footprint')
        if 'input' in parts and not upper:
            # Native UpdateGuides draws its fixed forward-intent shaft from
            # z+.45 toz+1.11. Point to a visible piece of that actual shaft;
            # never continue an arrow beyond its captured field of view.
            camera=cfg['topCamera'];maximum_z=camera['position'][2]+camera['orthographicSize']-.08
            target_z=min(z+.78,maximum_z)
            if target_z>=z+.46:
                candidate=point(x,target_z,upper)
                dest=spec['nativeCropMaps']['top']['destinationInLower']
                if dest[0]+4<candidate[0]<dest[0]+dest[2]-4 and dest[1]+4<candidate[1]<dest[1]+dest[3]-4:
                    lx=210 if center[0]>650 else 720
                    self.style.text(draw,'이동 입력',(lx,1408),40,tokens['relationship'])
                    draw.line([(lx+(80 if lx==210 else -80),1380),(candidate[0],candidate[1]+14)],fill=tokens['relationship'],width=4)
                    input_target=list(candidate);shown.append('input')
        return image,dict(parts=list(parts),shownParts=shown,kind='editorial same-native-geometry component reveal',
            nativeThickGuide=False,depthTested=False,role=role,sourceTraceFrame=int(row['frame']),
            capsuleCenter=list(center),radiusWorld=radius,inputTarget=input_target,
            inputMeaning='native attempted forward input, never measured displacement',commercialMeasurement=False)

    def _term_cards(self,image,terms,gameplay=False,identified_objects=False):
        if not terms:return image
        if len(terms)>1:raise ValueError('One clear term focus per frame')
        term=terms[0];draw=ImageDraw.Draw(image)
        heading=f"{term['english']} ({term['korean']})"
        if self.style.font(40).getlength(heading)>800:
            raise ValueError('Term heading must fit the measured mobile width')
        if term['presentation']=='chip':
            if gameplay:
                if identified_objects:raise ValueError('Game identification and term chip need separate clear focus cues')
                # Above the complete source viewport; never hide TF2 HUD.
                draw.rectangle((48,374,936,423),fill='#000000')
                self.style.text(draw,heading,(492,397),40,self.style.tokens['title'])
                return image
            # A source-kind subline distinguishes our scene from commercial data.
            draw.rectangle((66,440,918,540),fill='#000000')
            self.style.text(draw,heading,(492,468),40,self.style.tokens['title'])
            self.style.text(draw,'직접 만든 Unity 시연',(492,516),30,self.style.tokens['muted'])
            return image
        if not gameplay:
            dim=Image.new('RGBA',image.size,(0,0,0,0))
            ImageDraw.Draw(dim).rectangle((48,424,936,1468),fill=(0,0,0,210))
            image=Image.alpha_composite(image.convert('RGBA'),dim).convert('RGB')
        draw=ImageDraw.Draw(image)
        self.style.text(draw,heading,(492,1060),40,self.style.tokens['title'])
        lines=[];line='';font=self.style.font(40)
        for word in term['meaning'].split():
            if font.getlength(word)>760:
                raise ValueError('A definition word exceeds the readable scene width')
            candidate=(line+' '+word) if line else word
            if font.getlength(candidate)>760:
                lines.append(line);line=word
            else:line=candidate
        if line:lines.append(line)
        if len(lines)>4:raise ValueError('Definition needs readable scene-sized text, not a tiny font')
        for i,text in enumerate(lines):self.style.text(draw,text,(492,1120+i*54),40,self.style.tokens['ink'])
        return image

    def _purpose_illustration(self,image,overlay):
        if not overlay:return image
        # An expressly labelled2D concept diagram, not an extra engine result,
        # historical TF2 prototype, measured corridor or collision claim.
        image=image.copy()
        # Retain a dim visible portion of the same native stage behind the
        # conceptual explanation rather than inventing another commercial shot.
        panel=image.crop((48,424,936,924))
        panel=Image.blend(panel,Image.new('RGB',panel.size,'black'),.6)
        image.paste(panel,(48,424));draw=ImageDraw.Draw(image)
        draw.rectangle((48,328,936,374),fill='black')
        self.style.text(draw,'설명용 도식 · 직접 만든 시연 위에 표시',(492,350),32,self.style.tokens['muted'])
        self.style.text(draw,overlay['heading'],(492,990),40,self.style.tokens['title'])
        ink=self.style.tokens['ink'];red=self.style.tokens['problem'];teal=self.style.tokens['relationship']
        self.style.text(draw,overlay['narrowPurposeLabel'],(300,1044),36,ink)
        self.style.text(draw,overlay['widePurposeLabel'],(720,1044),36,ink)
        for x in (210,390,564,884):draw.line([(x,1080),(x,1380)],fill=ink,width=8)
        self.style.text(draw,overlay['enemyLabel'],(300,1120),36,red)
        draw.ellipse((276,1150,324,1198),outline=red,width=8)
        draw.line([(300,1200),(300,1260)],fill=red,width=10)
        draw.line([(266,1238),(300,1208),(334,1238)],fill=red,width=8)
        draw.line([(272,1300),(300,1260),(328,1300)],fill=red,width=8)
        draw.line([(300,1370),(300,1320)],fill=teal,width=8)
        draw.line([(286,1338),(300,1320),(314,1338)],fill=teal,width=8)
        # Cart tray/wheels and articulated stick-person are openly abstract
        # relationship symbols, not new enemies, rigs or simulated physics.
        draw.line([(598,1134),(614,1225),(742,1225),(758,1134)],fill=teal,width=8)
        draw.line([(598,1134),(758,1134)],fill=teal,width=8)
        draw.ellipse((615,1238,649,1272),outline=teal,width=7)
        draw.ellipse((705,1238,739,1272),outline=teal,width=7)
        self.style.text(draw,'수레',(678,1182),36,teal)
        draw.ellipse((794,1110,836,1152),outline=ink,width=7)
        draw.line([(815,1156),(815,1210)],fill=ink,width=8)
        draw.line([(784,1190),(815,1164),(846,1190)],fill=ink,width=7)
        draw.line([(790,1250),(815,1210),(840,1250)],fill=ink,width=7)
        for x in (678,815):
            draw.line([(x,1370),(x,1300)],fill=teal,width=8)
            draw.line([(x-14,1318),(x,1300),(x+14,1318)],fill=teal,width=8)
        self.style.text(draw,overlay['narrowActionLabel'],(300,1410),36,ink)
        self.style.text(draw,overlay['wideActionLabel'],(720,1410),36,ink)
        self.style.text(draw,overlay['resultLabel'],(492,1460),36,self.style.tokens['title'])
        return image

    def compose(self,frame):
        if not integer(frame) or not 0<=frame<self.timeline['totalFrames']:
            raise ValueError('Output frame outside the exact film clock')
        section=self.timeline['sections'][bisect.bisect_right(self.starts,frame)-1]
        if self.current_section is not section:
            if self.decoder:self.decoder.close();self.decoder=None
            self.current_section=section
            self.game_last_key=None;self.game_last_result=None
            if section['kind']=='gameplay':
                sid=section['sourceId']
                if sid not in self.pts_cache:self.pts_cache[sid]=probe_pts(section['sourcePath'],self.ffprobe)
                self.cut_counter+=1
                self.decoder=CutDecoder(section['sourcePath'],self.pts_cache[sid],section['sourceLocalInPts'],
                    section['endFrameExclusive']-section['startFrame'],self.ffmpeg,self.work/f'decode-{self.cut_counter:02d}.log')
        active={cue['kind'] for cue in section.get('annotationCues',[]) if cue['startFrame']<=frame<cue['endFrameExclusive']}
        offset=frame-section['startFrame']
        if section['kind']=='gameplay':
            picture,pts=self.decoder.at(section['sourceLocalInPts']+offset/FPS)
            key=(section['sourceId'],pts,'opening-tracks' in active)
            if key==self.game_last_key:result=self.game_last_result
            else:
                result=self.game.compose(picture,source_id=section['sourceId'],local_pts=pts,
                    annotations='opening-tracks' in active)
                self.game_last_key=key;self.game_last_result=result
        else:
            native=section['native'];hold=native.get('holdPolicy')
            nf=native['startNativeFrame']+(0 if hold else offset)
            request=guide_request(section,frame)
            key=(native['mode'],nf,native['layout'],request['reviewedBundle'],request['parts'])
            if hold and key in self.hold_cache:result=self.hold_cache[key]
            else:
                result=self.native.compose(native['mode'],nf,layout=native['layout'],
                    editorial_guides=request['enabled'] and request['reviewedBundle'])
                if request['enabled'] and not request['reviewedBundle']:
                    picture,guide=self._guide_parts(result.image,result.evidence['traceState'],native['layout'],request['parts'])
                    evidence=dict(result.evidence,editorialGuides=guide)
                    result=self.native_module.ComposedFrame(picture,evidence)
                if hold:self.hold_cache[key]=result
        clean=self._term_cards(result.image.copy(),section.get('termChips',[]),
            gameplay=section['kind']=='gameplay',identified_objects=bool(result.evidence.get('annotations')))
        clean=self._purpose_illustration(clean,section.get('illustrationOverlay'))
        if section['kind']!='gameplay' and section['native'].get('holdPolicy') and not section.get('illustrationOverlay'):
            self.style.text(ImageDraw.Draw(clean),'설명을 위한 정지 화면',(492,1488),30,self.style.tokens['muted'])
        pose=section.get('catPose');alpha=None
        reactions=self.timeline.get('catCues') or section.get('catCues',[])
        for cat in reactions:
            if cat['startFrame']<=frame<cat['endFrameExclusive']:
                if pose is not None:raise ValueError('Two cat reactions overlap')
                pose=cat['pose']
                ease_in=max(1,cat['easeInFrames']);ease_out=max(1,cat['easeOutFrames'])
                alpha=min(1,(frame-cat['startFrame']+1)/ease_in,(cat['endFrameExclusive']-frame)/ease_out)
        if pose:
            cat_image=clean.copy();self.style._cat(cat_image,pose)
            # Meaningful reaction cue, short entrance/exit only; no new assets.
            ramp=alpha if alpha is not None else min(1,(offset+1)/12,(section['endFrameExclusive']-frame)/12)
            clean=Image.blend(clean,cat_image,max(0,ramp))
        captioned=clean.copy();cue=self.caption_at(frame)
        if cue:
            self.style._captions(captioned,tuple(cue['koLines']),caption_emphasis(cue))
        return clean,captioned,dict(outputFrame=frame,sectionId=section['id'],beatId=section.get('beatId'),
            source=result.evidence,captionId=cue.get('id') if cue else None,
            termChips=section.get('termChips',[]),catPose=pose,
            conceptualOverlay=section.get('illustrationOverlay'))

    def close(self,failed=False):
        if self.decoder:self.decoder.close(failed);self.decoder=None


class VideoEncoder:
    def __init__(self,path,frames,ffmpeg,log):
        self.log=Path(log).open('xb')
        self.process=subprocess.Popen([ffmpeg,'-hide_banner','-nostdin','-f','rawvideo','-pixel_format','rgb24',
            '-video_size','1080x1920','-framerate','60','-i','pipe:0','-an','-c:v','libx264','-threads','2',
            '-preset','medium','-crf','18','-pix_fmt','yuv420p','-frames:v',str(frames),
            '-video_track_timescale','60000','-movflags','+faststart',str(path)],
            stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=self.log,creationflags=CREATE)

    def write(self,image):self.process.stdin.write(image.tobytes())

    def close(self,failed=False):
        if getattr(self,'closed',False):return
        self.closed=True
        pipe_error=None
        try:
            if not self.process.stdin.closed:self.process.stdin.close()
        except (BrokenPipeError,OSError) as error:
            pipe_error=error
        if failed and self.process.poll() is None:self.process.terminate()
        code=self.process.wait(timeout=300);self.log.close()
        if (code or pipe_error) and not failed:raise RuntimeError('Software video encoder failed')


def selected_output_root(value=None):
    expected=(MEDIA/'render-attempts').resolve()
    chosen=Path(value).resolve() if value else expected
    if chosen!=expected:raise ValueError('Output root must be the selected project C-media/render-attempts')
    return chosen


def execute(timeline_path,output_root=None,sample_frame=None):
    path=Path(timeline_path).resolve();timeline=read(path)
    inspection=verify_inputs(timeline,require_mix=sample_frame is None)
    authority=fresh_authorization()
    ffmpeg,ffprobe=binaries()
    root=selected_output_root(output_root)
    name=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]
    attempt=root/name;attempt.mkdir(parents=True,exist_ok=False)
    work=attempt/'work';work.mkdir()
    timeline_sha=sha(path);(attempt/'timeline.input.json').write_bytes(path.read_bytes())
    router=None;encoders=[]
    try:
        router=FrameRouter(timeline,work,ffmpeg,ffprobe)
        if sample_frame is not None:
            clean,captioned,evidence=router.compose(sample_frame)
            for kind,picture in (('clean',clean),('captioned',captioned)):
                picture.save(attempt/f'sample-{sample_frame:06d}.{kind}.png')
                picture.resize((375,667),Image.Resampling.LANCZOS).save(attempt/f'sample-{sample_frame:06d}.{kind}.375px.png')
            (attempt/'sample-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            router.close(failed=True)
            return dict(status='sample-only-no-film',path=str(attempt),timelineSHA256=timeline_sha)
        mix=timeline['audio']['mix'];aac=work/'shared-audio.m4a'
        run([ffmpeg,'-hide_banner','-nostdin','-i',mix['path'],'-vn','-c:a','aac','-b:a','192k',aac],work/'audio-encode.log')
        video_paths={kind:work/(kind+'.video.mp4') for kind in ('clean','captioned')}
        for kind in ('clean','captioned'):
            encoders.append(VideoEncoder(video_paths[kind],timeline['totalFrames'],ffmpeg,work/(kind+'-encode.log')))
        samples=[]
        section_starts={s['startFrame'] for s in timeline['sections']}
        for frame in range(timeline['totalFrames']):
            if frame%60==0:
                fresh_authorization()
                if sha(path)!=timeline_sha:raise ValueError('Timeline changed while rendering; abort this attempt')
            clean,captioned,evidence=router.compose(frame)
            encoders[0].write(clean);encoders[1].write(captioned)
            if frame in section_starts:
                samples.append(evidence)
        router.close()
        for encoder in encoders:encoder.close()
        encoders=[]
        outputs={}
        for kind in ('clean','captioned'):
            target=attempt/f'{SLUG}.{kind}.mp4'
            run([ffmpeg,'-hide_banner','-nostdin','-i',video_paths[kind],'-i',aac,'-map','0:v:0','-map','1:a:0',
                '-c','copy','-movflags','+faststart',target],work/(kind+'-mux.log'))
            outputs[kind]=dict(path=target.as_posix(),sha256=sha(target))
        for lang in ('ko','en'):
            target=attempt/f'{SLUG}.{lang}.srt';source=bound_file(timeline['subtitles'][lang],lang+' SRT')
            target.write_bytes(source.read_bytes());outputs[lang]=dict(path=target.as_posix(),sha256=sha(target))
        if sha(path)!=timeline_sha:raise ValueError('Timeline changed before output completion')
        verify_inputs(timeline)
        fresh_authorization()
        manifest=dict(schemaVersion='03-02-render-manifest-v1',slug=SLUG,complete=True,status='encoded-local-outputs-awaiting-independent-QA',
            timeline=dict(path=path.as_posix(),sha256=timeline_sha),format=dict(width=1080,height=1920,fps=60,totalFrames=timeline['totalFrames']),
            outputs=outputs,audioAac=dict(path=aac.as_posix(),sha256=sha(aac),sharedPacketCopy=True),
            renderer=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__),gpuUsed=False,modelStarted=False),
            inspection=inspection,authorization=authority,inputs=timeline['inputs'],sectionStartSamples=samples,
            humanListening=False,humanFinalApproval=False,encodedMotionQA=False,platformActions=[])
        (attempt/'render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        return manifest
    except Exception as error:
        if router:
            try:router.close(failed=True)
            except Exception:pass
        for encoder in encoders:
            try:encoder.close(failed=True)
            except Exception:pass
        (attempt/'failed.json').write_text(json.dumps(dict(error=str(error),timelineSHA256=timeline_sha,complete=False),indent=2)+'\n',encoding='utf8')
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeline',required=True)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--sample-frame',type=int)
    parser.add_argument('--output-root')
    args=parser.parse_args()
    if args.execute and args.sample_frame is not None:raise ValueError('Choose a single-frame sample or full execution')
    if args.execute or args.sample_frame is not None:
        result=execute(args.timeline,args.output_root,args.sample_frame)
    else:
        timeline=read(args.timeline)
        result=dict(status='validated-CPU-only-no-process',structure=validate_structure(timeline))
        try:result['readiness']=verify_inputs(timeline)
        except (ValueError,OSError) as error:result.update(status='not-ready-no-process',reason=str(error))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
