"""Prepare or explicitly compose the D21 real-timing 30.7-second inspection sample.

`prepare` writes only three MC source modules, their project, clipped copies of
the current KO ASS, cut14's normal annotation ASS and ignored provenance. It
does not start a renderer, FFmpeg, TTS, ASR or another process. Run the printed
MC render command separately; only then run `compose`. Neither stage modifies
the full movie, original captions, PCM, edit plan or another production.

The four separated excerpts intentionally cut speech at their boundaries.
Their concatenation is an inspection sample, never whole-video approval.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess

import soundfile as sf

from audio_pipeline import require_authorized
from video_pipeline import annotations, binary, filter_path, probe, ENCODER

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOCAL = ROOT / 'projects/player-customization/production/local/reference-preserving-v2'
MC = ROOT / 'motion-canvas/src/projects/player-customization/revision-v2'
OUT = LOCAL / 'inspection/timed-preflight'
PLAN = HERE / 'edit-plan.json'
EDIT = LOCAL / 'edit'
MC_NAME = 'customization-timed-preflight-v2'
MC_MOVIE = ROOT / f'shared/output/motion-canvas/{MC_NAME}.mp4'
MC_ROUTE = '/src/projects/player-customization/revision-v2/timed-preflight-project.ts'
FPS, WIDTH, HEIGHT = 60, 1920, 1080
WINDOWS = [('acvi', 5621, 6023, None),
           ('tradeoffs', 6395, 6875, 'tradeoffs'),
           ('find', 11388, 11868, 'find'),
           ('auto', 14298, 14778, 'auto')]


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def sha(p):
    digest = hashlib.sha256()
    with Path(p).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def path(value):
    p = Path(value)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    p.relative_to(ROOT.resolve())
    return p


def rel(p):
    return Path(p).resolve().relative_to(ROOT.resolve()).as_posix()


def record(p):
    p = path(p)
    return dict(path=rel(p), sha256=sha(p), bytes=p.stat().st_size)


def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write(p, content):
    # Preserve completed media; only the explicitly owned preparation sources
    # and ignored text evidence can be refreshed, never the full production.
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists() or p.read_text(encoding='utf-8') != content:
        p.write_text(content, encoding='utf-8')


def ass_seconds(value):
    h, m, s = value.strip().split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def ass_stamp(seconds):
    n = round(seconds * 100)
    return f'{n // 360000}:{n // 6000 % 60:02}:{n // 100 % 60:02}.{n % 100:02}'


def clip_ass(original, sections):
    """Keep all original layers/box paths/text/tags; change only Start/End."""
    header, events = [], []
    for line in original.splitlines():
        if line.startswith('Dialogue: '):
            fields = line[len('Dialogue: '):].split(',', 9)
            if len(fields) != 10:
                raise ValueError('Malformed original ASS Dialogue')
            events.append((fields, ass_seconds(fields[1]), ass_seconds(fields[2])))
        else:
            header.append(line)
    result, event_map = '\n'.join(header).rstrip() + '\n', []
    for section in sections:
        lo, hi = section['globalStartFrame'] / FPS, section['globalEndFrame'] / FPS
        offset = section['sampleStartFrame'] / FPS
        for ordinal, (fields, start, end) in enumerate(events):
            a, b = max(lo, start), min(hi, end)
            if b <= a:
                continue
            copied = fields.copy()
            copied[1], copied[2] = ass_stamp(offset + a - lo), ass_stamp(offset + b - lo)
            if copied[1] == copied[2]:
                continue
            result += 'Dialogue: ' + ','.join(copied) + '\n'
            event_map.append(dict(section=section['name'], originalEvent=ordinal,
                                  originalStart=start, originalEnd=end,
                                  sampleStart=offset + a - lo, sampleEnd=offset + b - lo,
                                  clippedAtStart=start < lo, clippedAtEnd=end > hi,
                                  encodedStart=copied[1], encodedEnd=copied[2]))
    return result, event_map


def current_captions(sections):
    """Read the current subtitle revision; do not pin an obsolete cue split."""
    layout, alignment = read(EDIT / 'caption-layout.json'), read(EDIT / 'caption-alignment.json')
    if (not layout['rows'] or len(layout['rows']) != alignment['bilingualCueCount'] or
            layout['fixedCenter'] != [960, 970] or layout['fontSize'] != 48 or layout['maxLines'] != 2):
        raise ValueError('Current caption count/alignment or fixed960,970/48px/two-line style disagrees')
    cues = []
    for s in sections:
        lo, hi, offset = s['globalStartSeconds'], s['globalEndSeconds'], s['sampleStartSeconds']
        cues.append(dict(section=s['name'], cues=[
            dict(cue=r['cue'], paragraph=r['paragraph'], ko=r['ko'],
                 globalStart=r['start'], globalEnd=r['end'],
                 sampleStart=offset+max(r['start'], lo)-lo,
                 sampleEnd=offset+min(r['end'], hi)-lo,
                 clippedAtStart=r['start'] < lo, clippedAtEnd=r['end'] > hi)
            for r in layout['rows'] if r['start'] < hi and r['end'] > lo]))
    original = (EDIT/'captions.ko.ass').read_text(encoding='utf-8-sig')
    captions, mapping = clip_ass(original, sections)
    return layout, cues, captions, mapping


def prepare():
    auth = require_authorized('timed-preflight-prepare-files-only')
    if (OUT / 'composition.json').exists():
        raise ValueError('A composed inspection is preserved here; do not replace its preparation')
    plan = read(PLAN)
    if (plan['width'], plan['height'], plan['fps']) != (WIDTH, HEIGHT, FPS):
        raise ValueError('This sample requires the current FHD60 edit')
    inputs = [record(PLAN), record(EDIT / 'captions.ko.ass'), record(EDIT / 'caption-layout.json'),
              record(EDIT / 'caption-alignment.json'), record(HERE / 'video_pipeline.py'),
              record(MC / 'visuals.tsx'), record(Path(__file__))]
    source = read(LOCAL / 'assets/provenance.json')
    inputs.append(record(LOCAL / 'assets/provenance.json'))
    # The exact MC assets it serves are pinned as well as the provenance registry.
    for asset in source:
        if 'image' in asset:
            image = path(asset['image'])
            if sha(image) != asset['sha256']:
                raise ValueError(f'Inspected asset has changed: {asset["id"]}')
            inputs.append(record(image))
            served = ROOT / 'output/player-customization/preproduction-assets' / image.name
            if sha(served) != asset['sha256']:
                raise ValueError(f'MC-served asset differs: {served.name}')
            inputs.append(record(served))
    pcm = ROOT / 'shared/output/narration/player-customization/reference-preserving-v2/narration-source.wav'
    inputs.append(record(pcm))
    scenes = {r['id']: r for r in plan['scenes']}
    sections, outputs, imports, cursor, mc_cursor = [], [], [], 0, 0
    cut14 = next(c for c in plan['cuts'] if c['id'] == 'cut14')
    if (cut14['startFrame'], cut14['endFrame'], cut14['frames'], cut14['sourceStart']) != (5621, 6023, 402, 154.8):
        raise ValueError('The requested complete ACVI comparison cut has changed')
    if {m['id'] for m in cut14['marks']} != {'acvi-boost-speed', 'acvi-qb-energy'}:
        raise ValueError('Expected the two current verified comparison marks')
    actual = path(cut14['sourceFile'])
    if sha(actual) != cut14['sourceSha256']:
        raise ValueError('ACVI original differs from the native-pixel reviewed recording')
    inputs.append(record(actual))
    OUT.mkdir(parents=True, exist_ok=True)
    annotation_ass, geometry = annotations(deepcopy(cut14), plan)
    mark_file = OUT / 'cut14-marks.ass'
    write(mark_file, annotation_ass)
    outputs.append(record(mark_file))
    for name, lo, hi, kind in WINDOWS:
        if kind is None:
            cut = cut14
        else:
            matches = [c for c in plan['cuts'] if c['kind'] == 'explanation' and c.get('visual') == kind
                       and c['startFrame'] <= lo and hi <= c['endFrame']]
            if len(matches) != 1:
                raise ValueError(f'Sample {name} is no longer inside one current explanation cut')
            cut = matches[0]
        section = dict(name=name, cut=cut['id'], scene=cut['scene'], kind=cut['kind'],
                       globalStartFrame=lo, globalEndFrame=hi, frames=hi-lo,
                       globalStartSeconds=lo/FPS, globalEndSeconds=hi/FPS,
                       sampleStartFrame=cursor, sampleEndFrame=cursor+hi-lo,
                       sampleStartSeconds=cursor/FPS, sampleEndSeconds=(cursor+hi-lo)/FPS)
        if kind:
            row = scenes[cut['scene']]
            local_start = lo / FPS - float(row['voiceStart'])
            cues = [float(p) - local_start for p in row['paragraphStarts']]
            # Subtract the actual source-local clock, including negative cues.
            # Do not re-time all paragraphs into an eight-second demo.
            equivalent = [float(p) - (lo-cut['startFrame'])/FPS for p in cut['cues']]
            if any(abs(a-b) > 1e-8 for a, b in zip(cues, equivalent)):
                raise ValueError('Measured voice cues disagree with the locked cut')
            payload = dict(duration=((hi-lo)-.75)/FPS, cues=cues, credit=cut['credit'])
            module = MC / f'timed-{name}.tsx'
            write(module, "import {makeScene2D} from '@motion-canvas/2d';\n"
                  "import {lesson} from './visuals';\n"
                  "export default makeScene2D(function*(view){yield* lesson(view,"
                  + json.dumps(kind) + ',' + json.dumps(payload, ensure_ascii=False) + ');});\n')
            imports.append(f"import s{len(imports)} from './timed-{name}?scene';")
            outputs.append(record(module))
            section.update(visual=kind, module=rel(module), originalParagraphStarts=row['paragraphStarts'],
                           originalSceneVoiceStart=row['voiceStart'], narrationSceneLocalStart=local_start,
                           shiftedParagraphCues=cues, mcStartFrame=mc_cursor,
                           mcEndFrame=mc_cursor+hi-lo, rendererDuration=payload['duration'])
            mc_cursor += hi-lo
        else:
            section.update(sourceFile=cut['sourceFile'], sourceSha256=cut['sourceSha256'],
                           sourceLocalStart=cut['sourceStart'], sourceLocalEnd=cut['sourceStart']+(hi-lo)/FPS,
                           viewport=cut.get('viewport', [0, 0, WIDTH, HEIGHT]), aspectFit='contain',
                           annotationAss=rel(mark_file), annotationGeometry=geometry,
                           marks=[m['id'] for m in cut['marks']], productionCut=deepcopy(cut))
        sections.append(section)
        cursor += hi-lo
    if cursor != 1842 or mc_cursor != 1440:
        raise ValueError('Expected30.7seconds / MC24seconds exactly at60fps')
    project = MC / 'timed-preflight-project.ts'
    write(project, "import {makeProject} from '@motion-canvas/core';\n" + '\n'.join(imports)
          + '\nexport default makeProject({scenes:[' + ','.join(f's{i}' for i in range(len(imports))) + ']});\n')
    outputs.append(record(project))
    layout, caption_cues, captions, mapping = current_captions(sections)
    for section, cues in zip(sections, caption_cues):
        section['captionCues'] = cues['cues']
    caption_file = OUT / 'captions.ko.ass'
    write(caption_file, captions)
    outputs.append(record(caption_file))
    # Catch concurrent plan/caption/visual changes before recording prepared state.
    for item in inputs:
        if sha(path(item['path'])) != item['sha256']:
            raise ValueError(f'Input changed during preparation: {item["path"]}')
    manifest = dict(schemaVersion=1, project='player-customization', revision='reference-preserving-v2',
                    createdAt=datetime.now(timezone.utc).isoformat(), status='prepared-no-render-or-compose',
                    authorization=auth, inputs=inputs, preparedOutputs=outputs, fps=FPS, width=WIDTH, height=HEIGHT,
                    frames=cursor, seconds=cursor/FPS, mcFrames=mc_cursor, mcVideo=rel(MC_MOVIE),
                    sections=sections, originalCaptionCueCount=len(layout['rows']), assEventMapping=mapping,
                    captionRule='Original ASS layers, text, geometry and tags retained; intersection/shift/centisecond rounding only.',
                    captionRevisionRule='Compose re-reads the current ASS/layout/alignment, validates their agreement and writes fresh clipped captions with current hashes. A cue split change does not change PCM or MC paragraph timing.',
                    audioDefault=dict(path=rel(EDIT/'final-mix.wav'), globalOriginSeconds=0,
                                      hash='deferred until compose; current root mix may still be running'),
                    sourceVoicePcm=dict(path=rel(pcm), sha256=sha(pcm), globalOriginSeconds=2),
                    commands=dict(render=['node', rel(HERE/'render-diagrams.cjs'), MC_NAME, '1440', MC_ROUTE],
                                  compose=['qwen3-tts/.venv/Scripts/python.exe', rel(Path(__file__)), 'compose']),
                    sourceCutAnnotations='Normal video_pipeline.annotations(cut14, currentPlan); same source-local targets and output placement.',
                    actualDirectReview='pending', mobile375Review='pending', continuousPlaybackAndListening='pending',
                    wholeMovieApproved=False, representativeSampleOnly=True,
                    intentionalExcerptEdges='Separated speech excerpts may begin/end mid-sentence; original full PCM and movie are untouched.',
                    mediaJobsStarted=0, originalCaptionsModified=False, foreignFilesOrProcessesChanged=[])
    save(OUT/'preparation.json', manifest)
    print(json.dumps(dict(status=manifest['status'], manifest=rel(OUT/'preparation.json'),
                          frames=cursor, mcFrames=mc_cursor, captionCues=[r['cue'] for s in sections for r in s['captionCues']],
                          commands=manifest['commands']), ensure_ascii=False))


def verify_preparation(manifest):
    dynamic = {rel(EDIT/n) for n in ['captions.ko.ass', 'caption-layout.json', 'caption-alignment.json']}
    dynamic.add(rel(OUT/'captions.ko.ass'))
    for item in [*manifest['inputs'], *manifest['preparedOutputs']]:
        if item['path'] in dynamic:
            continue
        p = path(item['path'])
        if not p.is_file() or sha(p) != item['sha256']:
            raise ValueError(f'Prepared input/output changed; recheck before compose: {item["path"]}')


def compose(audio_value, origin):
    """An explicit later command; never called by prepare or by import."""
    auth = require_authorized('timed-preflight-compose-explicit')
    manifest = read(OUT/'preparation.json')
    verify_preparation(manifest)
    layout, caption_cues, captions, mapping = current_captions(manifest['sections'])
    current_caption_inputs = [record(EDIT/n) for n in ['captions.ko.ass', 'caption-layout.json', 'caption-alignment.json']]
    # Safe local derivative only. The full movie's original subtitles are never edited.
    write(OUT/'captions.ko.ass', captions)
    caption_snapshot = dict(inputs=current_caption_inputs, cueCount=len(layout['rows']),
                            sections=caption_cues, assEventMapping=mapping,
                            shiftedAss=record(OUT/'captions.ko.ass'))
    movie, wav_file, receipt = OUT/'timed-preflight.captioned.mp4', OUT/'timed-preflight.audio.wav', OUT/'composition.json'
    audio, mc = path(audio_value), MC_MOVIE
    if not mc.is_file() or not audio.is_file():
        raise ValueError('Render1440MCframes and finish the selected global-clock PCM before compose')
    if audio.suffix.lower() != '.wav':
        raise ValueError('Use an existing PCM WAV; source recording audio is never mixed into this inspection')
    audio_info = sf.info(str(audio))
    if not audio_info.subtype.startswith('PCM_'):
        raise ValueError('The selected inspection audio must be an existing PCM WAV')
    audio_duration = audio_info.duration
    sections = manifest['sections']
    if min(s['globalStartSeconds']-origin for s in sections) < 0 or max(s['globalEndSeconds']-origin for s in sections) > audio_duration+1/48000:
        raise ValueError('PCM clock/duration does not cover the requested global sample ranges')
    mc_probe = probe(mc)
    stream = next(s for s in mc_probe['streams'] if s['codec_type'] == 'video')
    if ((stream['width'], stream['height']) != (WIDTH, HEIGHT) or Fraction(stream['avg_frame_rate']) != FPS
            or int(stream.get('nb_frames', -1)) != 1440):
        raise ValueError('The rendered preflight must be exactly1440FHDframes at60fps')
    cut = sections[0]['productionCut']
    native = path(cut['sourceFile'])
    stream = next(s for s in probe(native)['streams'] if s['codec_type'] == 'video')
    if stream['width'] < WIDTH or stream['height'] < HEIGHT:
        raise ValueError('The actual selected recording must be native FHD or higher')
    sar = stream.get('sample_aspect_ratio', '1:1')
    sar = Fraction(sar.replace(':', '/')) if sar not in ('N/A', '0:1', '0/1') else Fraction(1)
    sar = sar if sar > 0 else Fraction(1)
    # Match the production contain transform exactly; never stretch source UI.
    x, y, w, h = cut.get('viewport', [0, 0, WIDTH, HEIGHT])
    if any(v % 2 for v in [x, y, w, h]) or min(x, y) < 0 or x+w > WIDTH or y+h > HEIGHT:
        raise ValueError('Invalid exact production viewport')
    crop = cut.get('sourceCrop')
    crop_filter = ''
    if crop:
        cx, cy, cw, ch = crop
        if any(int(v) != v or v % 2 for v in crop) or min(cx,cy) < 0 or min(cw,ch) <= 0 or cx+cw > stream['width'] or cy+ch > stream['height']:
            raise ValueError('Invalid inspected production crop')
        crop_filter, aspect = f'crop={cw}:{ch}:{cx}:{cy},', cw*float(sar)/ch
    else:
        aspect = stream['width']*float(sar)/stream['height']
    fit_w, fit_h = w, 2*math.floor((w/aspect)/2)
    if fit_h > h:
        fit_h, fit_w = h, 2*math.floor((h*aspect)/2)
    left, top = (x+(w-fit_w)//2)//2*2, (y+(h-fit_h)//2)//2*2
    normalize = 'fps=60,setsar=1,settb=1/60000,setpts=N/(60*TB),format=yuv420p'
    graph = [f'[0:v]{crop_filter}fps=60,trim=end_frame=402,setpts=PTS-STARTPTS,'
             f'scale={fit_w}:{fit_h}:flags=lanczos,setsar=1,pad=1920:1080:{left}:{top}:black,'
             'ass='+filter_path(path(sections[0]['annotationAss']))+','+normalize+'[actual]',
             '[1:v]split=3[mc0][mc1][mc2]']
    for i, s in enumerate(sections[1:]):
        graph.append(f'[mc{i}]trim=start_frame={s["mcStartFrame"]}:end_frame={s["mcEndFrame"]},'
                     f'setpts=PTS-STARTPTS,{normalize}[v{i}]')
    graph += ['[actual][v0][v1][v2]concat=n=4:v=1:a=0[uncaptioned]',
              '[uncaptioned]ass='+filter_path(OUT/'captions.ko.ass')+'[video]',
              '[2:a]asplit=4[a0][a1][a2][a3]']
    for i, s in enumerate(sections):
        graph.append(f'[a{i}]atrim=start={s["globalStartSeconds"]-origin:.12f}:'
                     f'end={s["globalEndSeconds"]-origin:.12f},asetpts=PTS-STARTPTS[clip{i}]')
    graph += ['[clip0][clip1][clip2][clip3]concat=n=4:v=0:a=1,aresample=48000,'
              'aformat=sample_fmts=s32:channel_layouts=stereo,asplit=2[audio][pcm]']
    graph_file = OUT/'compose.filter.txt'
    write(graph_file, ';\n'.join(graph)+'\n')
    signature = dict(preparationSha256=sha(OUT/'preparation.json'), audio=record(audio), audioGlobalOrigin=origin,
                     motionCanvas=record(mc), currentCaptions=caption_snapshot,
                     graph=record(graph_file), code=record(Path(__file__)))
    if receipt.exists():
        old = read(receipt)
        if old.get('signature') == signature and movie.exists() and wav_file.exists() and all(
                sha(path(r['path'])) == r['sha256'] for r in old['outputs']):
            print(json.dumps(dict(status='reused-identical-inspection', receipt=rel(receipt))))
            return
        raise ValueError('A different completed preflight is preserved; do not overwrite it')
    if movie.exists() or wav_file.exists():
        raise ValueError('Unreceipted media exists; inspect it without overwriting')
    partial_movie, partial_wav = movie.with_name('timed-preflight.captioned.partial.mp4'), wav_file.with_name('timed-preflight.audio.partial.wav')
    if partial_movie.exists() or partial_wav.exists():
        raise ValueError('An incomplete previous composition is preserved; inspect its log first')
    cmd = [binary('ffmpeg'), '-nostdin', '-hide_banner', '-v', 'warning', '-n',
           '-filter_threads', '1', '-filter_complex_threads', '1',
           '-ss', f'{cut["sourceStart"]:.9f}', '-threads', '2', '-i', str(native),
           '-threads', '2', '-i', str(mc), '-i', str(audio),
           '-filter_complex', graph_file.read_text(encoding='utf-8'), '-map', '[video]', '-map', '[audio]',
           '-frames:v', '1842', *ENCODER, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
           '-movflags', '+faststart', str(partial_movie),
           '-map', '[pcm]', '-vn', '-c:a', 'pcm_s24le', '-ar', '48000', '-ac', '2', str(partial_wav)]
    log = OUT/'compose.log'
    with log.open('w', encoding='utf-8') as output:
        result = subprocess.run(cmd, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Inspection composition failed; existing log/partials preserved: {rel(log)}')
    final_probe = probe(partial_movie)
    v = next(s for s in final_probe['streams'] if s['codec_type'] == 'video')
    if (v['width'], v['height'], int(v.get('nb_frames', -1)), Fraction(v['avg_frame_rate'])) != (WIDTH, HEIGHT, 1842, FPS):
        raise ValueError('Inspection frame count, resolution or fps differs; partial retained')
    sample_seconds = sf.info(str(partial_wav)).duration
    if abs(sample_seconds-30.7) > 2/48000:
        raise ValueError('Continuous PCM excerpt does not match30.7seconds; partial retained')
    for item in [*current_caption_inputs, signature['audio'], signature['motionCanvas']]:
        if sha(path(item['path'])) != item['sha256']:
            raise ValueError(f'Input changed during composition; partial retained: {item["path"]}')
    # Probe/encode success is not a direct pixel, moving playback or audio pass.
    partial_movie.replace(movie)
    partial_wav.replace(wav_file)
    save(receipt, dict(schemaVersion=1, status='composed-awaiting-direct-inspection', signature=signature,
                       authorization=auth, createdAt=datetime.now(timezone.utc).isoformat(),
                       outputs=[record(movie), record(wav_file)], nativeContain=[left, top, fit_w, fit_h],
                       frames=1842, seconds=30.7, mcFrames=1440, continuousAudioEncodingCount=1,
                       audioPolicy='Exact ordered PCM excerpts concatenated before the single AAC encode; no new speech/BGM/gain/fades.',
                       actualDirectReview='pending', mobile375Review='pending', continuousPlaybackAndListening='pending',
                       fullDecodePtsIntegrity='pending', wholeMovieApproved=False, representativeSampleOnly=True,
                       originalFullPcmOrCaptionsChanged=False))
    print(json.dumps(dict(status='composed-awaiting-direct-inspection', movie=rel(movie), audio=rel(wav_file), receipt=rel(receipt))))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('stage', choices=['prepare', 'compose'])
    parser.add_argument('--audio', default=rel(EDIT/'final-mix.wav'), help='Compose only: completed global-clock PCM WAV; pass the revised mix path explicitly if needed')
    parser.add_argument('--audio-origin', type=float, default=0, help='Global time of PCM sample0; use0 for the timed/final stem,2 for the unmodified narration-source.wav')
    args = parser.parse_args()
    if args.stage == 'prepare':
        prepare()
    else:
        if not math.isfinite(args.audio_origin):
            raise ValueError('Audio origin must be finite')
        compose(args.audio, args.audio_origin)


if __name__ == '__main__':
    main()
