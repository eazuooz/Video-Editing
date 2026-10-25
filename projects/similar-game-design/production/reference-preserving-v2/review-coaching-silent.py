"""Finite QA for the changed ending; no whole-video ASR or new TTS."""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageDraw
import audio_pipeline as audio
import video_pipeline as video

HERE = Path(__file__).resolve().parent


def packets(file):
    command = [video.binary('ffprobe'), '-v', 'error', '-select_streams', 'a:0',
        '-show_packets', '-show_data_hash', 'sha256', '-show_entries',
        'packet=pts_time,duration_time,data_hash', '-of', 'json', str(file)]
    rows = json.loads(subprocess.check_output(command))['packets']
    return [{k: row[k] for k in ['pts_time', 'duration_time', 'data_hash']} for row in rows]


def main():
    audio.require_authorized('bounded changed-ending QA only')
    plan = audio.read(HERE / 'edit-plan-coaching-silent-v3.json')
    base = audio.read(HERE / 'edit-plan-final-v4.json')
    new, old = audio.repo_path(plan['outputDir']), audio.repo_path(base['outputDir'])
    structural = audio.read(new / 'structural-verification.json')
    assert structural['status'] == 'pass'
    master = audio.repo_path(structural['outputs']['captioned']['path'])
    qa = audio.current_local_output(new / 'qa')
    qa.mkdir(parents=True, exist_ok=True)
    before, after = packets(old / 'final-mix.m4a'), packets(new / 'final-mix.m4a')
    cutoff = 269.5
    def prefix(rows):
        return [x for x in rows if float(x['pts_time']) + float(x['duration_time']) <= cutoff]
    assert prefix(before) == prefix(after), 'Retained encoded narration prefix changed'
    first_changed = next((i for i, pair in enumerate(zip(before, after)) if pair[0] != pair[1]), None)
    packet_proof = {'status': 'pass', 'cutoffSeconds': cutoff,
        'identicalEncodedPacketCount': len(prefix(after)),
        'firstChangedPacket': first_changed,
        'firstChangedPacketPts': float(after[first_changed]['pts_time']) if first_changed is not None else None,
        'oldAac': audio.artifact(old / 'final-mix.m4a'),
        'newAac': audio.artifact(new / 'final-mix.m4a'),
        'sameCodecPtsDurationAndDataHashesBeforeCutoff': True}
    audio.save(qa / 'aac-prefix-review.json', packet_proof)
    loudness = audio.loudness(new / 'final-mix.m4a', qa / 'final-loudness.log', -16, -1.5)
    audio.save(qa / 'final-loudness.json', loudness)
    clip = qa / 'encoded-ending-269.5-276.5.wav'
    if not clip.exists():
        audio.run_ff(['-ss', 269.5, '-i', master, '-t', 7, '-vn', '-ar', 16000,
            '-ac', 1, '-c:a', 'pcm_s16le', clip], qa / 'ending-decode.log')
    asr_file = qa / 'ending-asr.json'
    recognized = audio.full_asr(clip, asr_file, final=True)
    recognized.update(scope='Only the encoded ending at global269.5–276.5s; not a whole-master ASR.',
        boundedMasterRangeSeconds=[269.5, 276.5], wholeMasterSubmitted=False)
    audio.save(asr_file, recognized)
    frames = qa / 'frames'; frames.mkdir(exist_ok=True)
    times = [273.8, 275.1, 277.0, 280.05, 280.3, 285.0, 290.0]
    if not (frames / '0007.png').exists():
        expression = '+'.join(f'eq(n,{round((t - 269) * 60)})' for t in times)
        audio.run_ff(['-ss', 269, '-i', master, '-an', '-vf', "select='" + expression + "'",
            '-frames:v', len(times), '-fps_mode', 'vfr', '-threads', 4,
            frames / '%04d.png'], qa / 'ending-pixels.log')
    board = Image.new('RGB', (750, 4 * 241), '#151515')
    draw = ImageDraw.Draw(board)
    records = []
    for i, time in enumerate(times):
        file = frames / f'{i + 1:04d}.png'
        with Image.open(file) as im:
            assert im.size == (1920, 1080)
            small = im.convert('RGB').resize((375, 211), Image.Resampling.LANCZOS)
            x, y = i % 2 * 375, i // 2 * 241
            board.paste(small, (x, y)); draw.text((x + 8, y + 216), f'{time:.3f}s', fill='white')
        records.append({'globalTime': time, **audio.artifact(file)})
    mobile = qa / 'ending-375.jpg'; board.save(mobile, quality=94)
    old_cues = audio.read(old / 'captions.json')['cues']
    new_cues = audio.read(new / 'captions.json')['cues']
    assert new_cues == old_cues[:104]
    report = {'status': 'analysis-complete-direct-pixels-and-text-review-pending',
        'recordedAt': audio.now(), 'master': audio.artifact(master),
        'pcmAndStreamVerification': audio.artifact(new / 'revision-verification.json'),
        'structuralVerification': audio.artifact(new / 'structural-verification.json'),
        'aacPrefixEvidence': audio.artifact(qa / 'aac-prefix-review.json'),
        'loudness': loudness, 'boundedEndingAsr': audio.artifact(asr_file),
        'recognizedText': recognized['text'], 'frames': records,
        'mobileBoard': audio.artifact(mobile),
        'first104CueObjectsExactlyRetained': True, 'removedCaptionCue': 105,
        'durationFramesUnchanged': 17408, 'endPageAndLinksPreserved': True,
        'newTtsOrCloudCredits': False, 'fullHumanListening': False,
        'platformMutation': False}
    audio.save(HERE / 'coaching-silent-v3-review.json', report)
    print(json.dumps({'recognizedEnding': recognized['text'],
        'encodedPrefixPackets': len(prefix(after)), 'qa': audio.relative(qa)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
