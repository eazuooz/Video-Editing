"""11.05 guarded software compositor source. Default performs no media work.

Only --execute can reserve a lease/start exact owned encoders/decoders. A sample
also needs --execute and all actual mix/caption/native/atlas/guide proofs.
"""
from __future__ import annotations
import argparse, bisect, hashlib, importlib.util, json, math, os, shutil, subprocess, sys, time, uuid
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106') / PROJECT.name
PINS = {
    'render-zen-view-film.py': '9e3ea1f564269d027111356bbecf762673114a0b4acb2c034121d18fea5138c2',
    'render-first-film.py': '1a82e5676058835bcdf752706d96888deb1b6d393a06ec53efe86a3c189bd372',
    'solution-path-composition-data-v1.py': 'a3e8dc89206f0c188a9f818d9b07885b2fa50095848596baea33925e1d5a43ab',
    'composite-solution-path-frame-v1.py': '8646cebfc31b77daa939195ec013d7d33c0ac0ee1a926b707e511c5e3aea2f02',
    'solution-path-postrepair-resource-v1.py': '6532b6e19ab92418a1f2f2f02d270493848b5984880ddc335b041cc2f2dde73e',
    'run-solution-path-structure-atlas-v2.py': '966a85e7fc2e7c9f6135fca914f8d6383692385bda0cd8df9da28188c5dec110',
}
BUILDER_SHA = '55bfa9e115062bfe6d167fd5885e7d5ed093b481ed69733aeab922539bbf0a12'
PROTOCOL = 'architectural111-11-05-composite-v3'
OWNER = 'architectural-111-11-05-composite'
STATE = MEDIA.parent / '11-05-composite-progress-v3.json'
WORKER = MEDIA.parent / '11-05-composite-worker-v3.json'
OUTPUT = MEDIA / 'render-attempts-v3'
CREATE = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
SOURCE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


class Pending(ValueError):
    pass


def need(value, reason):
    if not value: raise Pending(reason)


def sha(path):
    with Path(path).open('rb') as handle: return hashlib.file_digest(handle, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def module(name, path, expected):
    need(isinstance(expected, str) and len(expected) == 64 and sha(path) == expected, 'Reviewed helper pin missing/changed: ' + Path(path).name)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


def builder():
    return module('solution_full_film_current_builder', HERE / 'build-solution-path-film-timeline-v3.py', BUILDER_SHA)


def verify_timeline(path):
    b = builder(); b.authority()
    path = Path(path).resolve(); value = b.verify_existing(path)['timeline']
    need(value.get('rendererSource') == dict(path=str(Path(__file__).resolve()), sha256=SOURCE_SHA)
         and sha(__file__) == SOURCE_SHA, 'Timeline/loaded renderer source changed')
    for name, expected in PINS.items(): need(sha(HERE / name) == expected, 'Frozen renderer primitive changed: ' + name)
    verify_atlas_producer(value)
    return value, b


def verify_atlas_producer(timeline):
    """Upstream producer only. It pins the builder, never this renderer."""
    name='run-solution-path-structure-atlas-v2.py'
    atlas=module('solution_current_atlas_producer',HERE/name,PINS[name])
    saved=read(timeline['structureAtlas']['path']);p=timeline['picturePlan']
    try:
        prov=atlas.prepare(saved['job']['path'],p['captionTiming']['path'],p['audioBuild']['path'])
        need(prov.get('ready') is True,'Actual current source-bound atlas producer proof missing')
        atlas.validate_manifest(timeline['structureAtlas']['path'],prov)
    except atlas.Pending as error: raise Pending(str(error)) from error


def section_at(t, frame):
    need(type(frame) is int and 0 <= frame < t['totalFrames'], 'Current integer output frame required')
    rows = t['sections']; i = bisect.bisect_right([v['startFrame'] for v in rows], frame) - 1
    need(i >= 0 and frame < rows[i]['endFrameExclusive'], 'No picture covers this audio frame')
    return rows[i]


def cue_at(rows, frame):
    return next((v for v in rows if v['startFrame'] <= frame < v['endFrameExclusive']), None)


def manual_mark(guide_rows, source_frame):
    need(60 <= source_frame < 961 and len(guide_rows) == 901, 'Exact reviewed source guide clock required')
    row = guide_rows[source_frame - 60]
    need(row['sourceFrame'] == source_frame, 'Manual guide would leak across source clock/cut')
    return row['marks']


def enemy_contact(state):
    names = state['contactColliderNames']
    need(isinstance(names, list) and all(isinstance(value, str) for value in names), 'Actual collider-name trace required')
    # Exact source GameObject/collider name, preserved in actual B1680 trace.
    # Do not infer contact from screen overlap or a broad enemy-name alias.
    return 'Own patrol/contact actor' in names


class FrameRouter:
    def __init__(self, timeline, work, ffmpeg, ffprobe, primitives):
        self.full, self.t, self.work, self.ffmpeg, self.ffprobe, self.lib = timeline, timeline['picturePlan'], Path(work), ffmpeg, ffprobe, primitives
        self.b = builder()
        self.data_api = module('solution_full_frame_data', HERE / 'solution-path-composition-data-v1.py', PINS['solution-path-composition-data-v1.py'])
        self.frame_api = module('solution_full_frame_ui', HERE / 'composite-solution-path-frame-v1.py', PINS['composite-solution-path-frame-v1.py'])
        self.native = self.data_api.NativeData(); self.composer = self.frame_api.FrameComposer()
        self.style = None; self.decoder = None; self.decoder_key = None; self.source_pts = None
        self.guides = read(timeline['movingGuides']['path'])['sourceFrameRows']
        atlas = read(timeline['structureAtlas']['path'])
        self.atlas = {(v['mode'], v['nativeFrame']): atlas['frames'][v['atlasIndex']]['image'] for v in atlas['aliases']}
        self.atlas_cache, self.last_frame = {}, -1

    def font_style(self):
        if self.style is None: self.style = self.frame_api.prepared_style()
        return self.style

    def game_frame(self, section, frame):
        source = self.t['actualGameSource']; cut = section['actualGame']
        if self.decoder_key != section['id']:
            if self.decoder: self.decoder.close(); self.decoder = None
            if self.source_pts is None:
                self.source_pts = self.lib.probe_pts(source['path'], (1920, 1080), self.ffprobe)
                need(len(self.source_pts) > 960 and all(abs(self.source_pts[i] - i * 1001 / 60000) < .000003 for i in range(60, 961)),
                     'Actual decoded PTS differs from pinned displayed59.94 clock')
            first, last = cut['sourceRange'][0], cut['sourceRange'][1] - 1
            start = self.source_pts[first]
            # Exact past-PTS decoder is asked for the already-selected nearest
            # source PTS. Its finite range includes the final selected input.
            count = math.ceil((self.source_pts[last] - start) * 60) + 1
            self.decoder = self.lib.StreamDecoder(source['path'], (1920, 1080), self.source_pts, start, count,
                                                 self.ffmpeg, self.work / (section['id'] + '-source.log'))
            self.decoder_key = section['id']
        index = self.b.source_index(cut, frame)
        image, pts = self.decoder.at(self.source_pts[index])
        need(abs(pts - self.source_pts[index]) < .000001, 'Source sampler did not present its exact selected input')
        return image, index

    def draw_game(self, section, frame, caption):
        from PIL import Image, ImageDraw
        source, index = self.game_frame(section, frame)
        style = self.font_style(); canvas = Image.new('RGB', (1080, 1920), '#000000')
        canvas.paste(source.resize((880, 495), Image.Resampling.LANCZOS), (48, 410))
        draw = ImageDraw.Draw(canvas); font = lambda size, weight=700: style.font(size, weight, True)
        for i, text in enumerate(self.t['headline']):
            need(font(62).getlength(text) <= 800, 'Keep authored fixed headline size')
            draw.text((488, (166, 254)[i]), text, font=font(62), fill=('#e8cf83', '#f5f5f5')[i], anchor='mm')
        draw.text((488, 376), 'Spelunky (HD) · 실제 플레이', font=font(36), fill='#b8b8b8', anchor='mm')
        colors = dict(term='#73c7c2', result='#a4c6a0', problem='#ef8585')
        for mark in manual_mark(self.guides, index):
            points = [(48 + x * 11 / 24, 410 + y * 11 / 24) for x, y in mark['sourcePoints']]
            color = colors[mark['role']]
            if mark['kind'] in ('ellipse', 'rectangle'):
                need(len(points) == 2 and points[0][0] < points[1][0] and points[0][1] < points[1][1], 'Actual authored region required')
                getattr(draw, mark['kind'])([*points[0], *points[1]], outline=color, width=9)
            else:
                draw.line(points, fill=color, width=9)
                a, end = points[-2:]; angle = math.atan2(end[1] - a[1], end[0] - a[0])
                for delta in (-.55, .55):
                    draw.line([end, (end[0] - 24 * math.cos(angle + delta), end[1] - 24 * math.sin(angle + delta))], fill=color, width=9)
            need(font(46).getlength(mark['labelKo']) <= 800, 'Game guide text must fit outside source without shrinking')
            draw.text((488, 1000), mark['labelKo'], font=font(46), fill=color, anchor='mm')
        clean, captioned = canvas, canvas.copy()
        if caption: style._captions(captioned, tuple(caption['lines']), self.frame_api.caption_emphasis(caption))
        return clean, captioned, dict(sectionId=section['id'], sourceFrame=index, actualSourcePts=self.source_pts[index], editorialGuide=bool(manual_mark(self.guides, index)))

    def compose(self, frame):
        from PIL import Image, ImageDraw
        need(frame > self.last_frame, 'Film compositor only advances; sample uses a fresh router')
        self.last_frame = frame; section = section_at(self.t, frame); caption = cue_at(self.t['captions']['ko'], frame)
        if section['kind'] == 'actual-game': return self.draw_game(section, frame, caption)
        if self.decoder:
            self.decoder.close(); self.decoder = None; self.decoder_key = None
        n = section['native']; native = self.b.native_index(section, frame); term = self.b.term_at(self.t, frame)
        structure = section['structuralCompanion'] and not (term and term['presentation'] == 'definition')
        # Structural Node owns its canonical heading/kind/legend; do not draw
        # a second active term chip beneath or over that illustration.
        ui_term = None if structure else term
        cat = cue_at(self.t['catCues'], frame)
        cat_pose = cat['pose'] if cat and section['catAllowed'] and n['layout'] == 'single-player' and (not term or term['presentation'] == 'chip') else None
        guides = []
        if section['reviewedClosedPortGuide'] and not (term and term['presentation'] == 'definition'):
            guides = [dict(panel=1, anchorId='closed-port-10-11', kind='blocked-port-label', label='닫힌 통로', role='problem', labelCenter=[760, 1370])]
        packet = self.native.packet(n['layout'], n['modes'], native, guides, purpose='hero' if cat_pose else 'explanation', cat_pose=cat_pose, term=ui_term)
        pictures = self.native.decoded_panels(packet)
        clean, captioned, record = self.composer.compose(packet, pictures, headline=self.t['headline'], caption=caption,
                                                       hold_reason=n['holdReason'] if n['playback'] == 'held' else None)
        if structure:
            key = (n['modes'][0], native)
            if key not in self.atlas_cache:
                row = self.atlas[key]; image = self.b.bound(row)
                with Image.open(image) as source:
                    need(source.size == (1080, 900) and source.format == 'PNG', 'Actual full-aspect source-bound structure PNG required')
                    # Atlas snapshots are assets, not a second motion clock.
                    # One uniform scale for both axes, including the fractional
                    # 733.333px height; transparent padding never stretches it.
                    overlay = source.convert('RGBA').transform((880, 734), Image.Transform.AFFINE,
                        (1080 / 880, 0, 0, 0, 1080 / 880, 0), resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
                    self.atlas_cache = {key: overlay}
            overlay = self.atlas_cache[key]
            clean.paste(overlay, (48, 410), overlay); captioned.paste(overlay, (48, 410), overlay)
        if section['paragraph'] in (12, 13) and n['modes'] == ['threats-a', 'threats-b'] and not (term and term['presentation'] == 'definition'):
            for i, mode in enumerate(n['modes']):
                state = self.native.frame(mode, native)['state']
                touch = enemy_contact(state)
                text = '적 트리거 접촉 기록 있음' if touch else '적 트리거 접촉 기록 없음'
                for canvas in (clean, captioned):
                    draw = ImageDraw.Draw(canvas); font = self.composer.style.font(36, 700, True)
                    need(font.getlength(text) <= 800, 'Contact record must fit its panel')
                    y = (835, 1417)[i]
                    draw.rectangle((72, y - 29, 904, y + 29), fill='#000000')
                    draw.text((488, y), text, font=font, fill='#ef8585' if touch else '#a4c6a0', anchor='mm')
        record.update(sectionId=section['id'], nativeFrame=native, sourceModes=n['modes'], structuralCompanion=structure,
                      actualPixelQaPassed=False, actualListening=False)
        return clean, captioned, record

    def close(self, failed=False):
        if self.decoder: self.decoder.close(failed); self.decoder = None


def _render(path, attempt, sample_frame, lib):
    timeline, b = verify_timeline(path); t = timeline['picturePlan']; authority = b.authority()
    timeline_sha = sha(path)
    input_stats = {v['path']: (Path(v['path']).stat().st_size, Path(v['path']).stat().st_mtime_ns) for v in timeline['inputs']}
    first = module('solution_software_binaries', HERE / 'render-first-film.py', PINS['render-first-film.py'])
    ffmpeg, ffprobe = first.binaries(); work = attempt / 'work'; work.mkdir()
    (attempt / 'timeline.input.json').write_bytes(Path(path).read_bytes())
    router, encoders = None, []
    try:
        router = FrameRouter(timeline, work, ffmpeg, ffprobe, lib)
        if sample_frame is not None:
            from PIL import Image
            clean, captioned, evidence = router.compose(sample_frame)
            for kind, picture in [('clean', clean), ('captioned', captioned)]:
                picture.save(attempt / f'sample-{sample_frame:06d}.{kind}.png')
                picture.resize((375, 667), Image.Resampling.LANCZOS).save(attempt / f'sample-{sample_frame:06d}.{kind}.375px.png')
            lib.save(attempt / 'sample-evidence.json', evidence); router.close(True)
            return dict(status='sample-only-no-film', complete=False, output=str(attempt), actualPixelQaPassed=False)
        mix = t['audio']['mix']; aac = work / 'shared-audio.m4a'
        lib.run([ffmpeg, '-hide_banner', '-nostdin', '-threads', '2', '-i', mix['path'], '-vn', '-c:a', 'aac', '-b:a', '320k', '-n', aac], work / 'audio-encode.log')
        videos = {kind: work / (kind + '.video.mp4') for kind in ('clean', 'captioned')}
        encoders = [lib.VideoEncoder(videos[kind], t['totalFrames'], ffmpeg, work / (kind + '-encode.log')) for kind in videos]
        samples = []
        for frame in range(t['totalFrames']):
            if frame % 60 == 0:
                b.authority()
                need(sha(path) == timeline_sha and sha(__file__) == SOURCE_SHA and all((Path(p).stat().st_size, Path(p).stat().st_mtime_ns) == stamp
                     for p, stamp in input_stats.items()), 'Frozen input changed during render')
            clean, captioned, evidence = router.compose(frame)
            encoders[0].write(clean); encoders[1].write(captioned)
            if frame in {v['startFrame'] for v in t['sections']}: samples.append(evidence)
        router.close(); [encoder.close() for encoder in encoders]; encoders = []
        outputs = {}
        for kind, video in videos.items():
            target = attempt / (PROJECT.name + '.' + kind + '.mp4')
            lib.run([ffmpeg, '-hide_banner', '-nostdin', '-threads', '2', '-i', video, '-i', aac, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', '-n', target], work / (kind + '-mux.log'))
            outputs[kind] = dict(path=str(target), sha256=sha(target))
        for language in ('ko', 'en'):
            source = b.bound(t['subtitles'][language]); target = attempt / (PROJECT.name + '.' + language + '.srt')
            target.write_bytes(source.read_bytes()); outputs[language] = dict(path=str(target), sha256=sha(target))
        verify_timeline(path)
        result = dict(schemaVersion='11.05-render-manifest-v3', topicId='11.05', slug=PROJECT.name, complete=True,
                      timeline=dict(path=str(path), sha256=sha(path)), format=dict(width=1080, height=1920, fps=60, totalFrames=t['totalFrames']),
                      outputs=outputs, audioAac=dict(path=str(aac), sha256=sha(aac), sharedPacketCopy=True), inputs=timeline['inputs'],
                      encodedAudioMapping=timeline['encodedAudioMapping'], assemblyProfile=timeline['assemblyProfile'],
                      renderer=dict(path=str(Path(__file__)), sha256=sha(__file__), gpuUsed=False, modelStarted=False),
                      authorization=authority, sectionStartSamples=samples, encodedMotionQA=False,
                      humanListening=False, humanFinalApproval=False, platformActions=[])
        lib.save(attempt / 'render-manifest.json', result); return result
    except BaseException:
        if router:
            try: router.close(True)
            except Exception: pass
        for encoder in encoders:
            try: encoder.close(True)
            except Exception: pass
        raise


def execute(path, sample_frame=None):
    timeline, b = verify_timeline(path); b.authority()
    if sample_frame is not None: section_at(timeline['picturePlan'], sample_frame)
    lib = module('solution_owned_stream_primitives', HERE / 'render-zen-view-film.py', PINS['render-zen-view-film.py'])
    lib.fresh_authorization = b.authority
    resource = module('solution_owned_composite_resource', HERE / 'solution-path-postrepair-resource-v1.py', PINS['solution-path-postrepair-resource-v1.py'])
    rt = resource.rt; rt.PROTOCOL, rt.OWNER = PROTOCOL, OWNER
    worker = rt.SingleWorker(WORKER).acquire(); token, rec, controller, attempt = None, None, None, None
    known = set()
    try:
        old = worker.previous or {}; known = set(old.get('recoverableLeaseTokens', []))
        if old.get('leaseToken'): known.add(old['leaseToken'])
        worker.update(recoverableLeaseTokens=sorted(known))
        if rt.LEASE.exists():
            old_lease = read(rt.LEASE)
            if lib.reclaimable_lease(old_lease, known, rt): rt.archive(rt.LEASE, old_lease['token'])
        reason = resource.busy_reason()
        if reason: return dict(status='resource-declined-no-process', reason=reason, exitCode=75)
        need(shutil.disk_usage(MEDIA).free >= 4 * 1024**3, 'Preserve existing media and4GiB C reserve')
        attempt = OUTPUT / (datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:10])
        attempt.mkdir(parents=True, exist_ok=False)
        proposed = uuid.uuid4().hex
        rec = dict(protocol=PROTOCOL, owner=OWNER, token=proposed, **rt.identity(), child=None, children=[], phase='reserved',
                   output=str(attempt), timelineSHA256=sha(path), rendererSHA256=sha(__file__))
        try:
            with rt.LEASE.open('x', encoding='utf8') as handle: json.dump(rec, handle)
        except FileExistsError: return dict(status='resource-race-no-process', exitCode=75)
        token = proposed; known.add(token)
        worker.update(leaseToken=token, recoverableLeaseTokens=sorted(known), attempt=str(attempt))
        controller = lib.OwnedController(rt, worker, rec); lib.CONTROLLER = controller
        reason = resource.busy_reason(token)
        need(reason is None, 'Resources changed after lease reservation: ' + str(reason))
        verify_timeline(path)
        lib.save(STATE, dict(rec, status='owned-software-compositing', gpuEncoding=False, modelStarted=False, complete=False))
        result = _render(Path(path).resolve(), attempt, sample_frame, lib)
        lib.save(STATE, dict(rec, status=result.get('status', 'encoded-local-review-pending'), complete=bool(result.get('complete')),
                             gpuEncoding=False, modelStarted=False)); return result
    except BaseException as error:
        if controller: controller.terminate_owned()
        # Do not overwrite previous live/completed state if failure preceded our
        # actual lease/attempt ownership. Partials remain in their fresh folder.
        if token and rec:
            lib.save(STATE, dict(rec, status='failed-preserved', complete=False, error=str(error), recoverableLeaseTokens=sorted(known)))
            lib.save(attempt / 'failed.json', dict(error=str(error), timelineSHA256=rec['timelineSHA256'], complete=False))
        raise
    finally:
        lib.CONTROLLER = None
        live = bool(rec and (rt.alive(rec.get('child')) or lib.pending_child(rec, rt)))
        if token and not live and rt.LEASE.exists():
            current = read(rt.LEASE)
            if rt.ours(current) and current['token'] == token: rt.LEASE.unlink()
        unresolved = rt.LEASE.exists() and rt.ours(read(rt.LEASE)) and read(rt.LEASE).get('token') in known
        worker.close(remove=not live and not unresolved)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--timeline'); p.add_argument('--execute', action='store_true'); p.add_argument('--sample-frame', type=int)
    args = p.parse_args()
    if args.execute:
        need(args.timeline, 'Explicit current timeline required before execution')
        result = execute(args.timeline, args.sample_frame)
    elif args.timeline:
        try:
            value, _ = verify_timeline(args.timeline)
            result = dict(ready=True, timelineSHA256=sha(args.timeline), totalFrames=value['picturePlan']['totalFrames'], jobLaunched=False)
        except (Pending, OSError, KeyError) as error: result = dict(ready=False, reason=str(error), jobLaunched=False)
    else:
        result = dict(ready=False, reason='Pending actual current caption/mix/structure/guide timeline', jobLaunched=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result.get('exitCode', 0)


if __name__ == '__main__':
    raise SystemExit(main())
