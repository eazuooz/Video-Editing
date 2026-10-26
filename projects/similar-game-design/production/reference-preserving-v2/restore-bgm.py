"""D22: restore the approved Nimbus bed; preserve both compressed video streams.

No TTS, image render, timing, subtitle, source, platform or foreign-job changes.
All media writes use the existing verified D22 C-backed local output route.
"""
from pathlib import Path
import argparse
import copy
import json
import shutil
import numpy as np
import soundfile as sf
import audio_pipeline as audio
import video_pipeline as video

HERE = Path(__file__).resolve().parent
VARIANT = 'bgm-restored-v4'
OLD_PLAN = HERE / 'edit-plan-coaching-silent-v3.json'
PLAN = HERE / 'edit-plan-bgm-restored-v4.json'
RATE = 48000
MUSIC_GAIN_DB = 3.0
GRAPH = ('[0:a]asplit=3[voice][side1][side2];'
         '[1:a][side1]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1,'
         'asplit=2[bg][bgdiag];'
         '[2:a][side2]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[game];'
         '[voice][bg][game]amix=inputs=3:normalize=0:duration=first,'
         'alimiter=limit=0.794:level=false:latency=true[out]')


def guard(stage):
    evidence = audio.read(HERE / 'authorization.json').get('bgmRestoration', {})
    if evidence.get('revision') != VARIANT or evidence.get('renderAuthorized') is not True:
        raise ValueError('Require the actual current user-backed D22 BGM request')
    return audio.require_authorized('D22 approved BGM restoration ' + stage)


def locations():
    old = audio.read(OLD_PLAN)
    old_dir = audio.current_local_output(old['outputDir'])
    new = audio.current_local_output(old_dir.parent / VARIANT)
    original = old_dir.parent
    return old, old_dir, new, original


def render():
    guard('audio render/remux')
    old, old_dir, new, original = locations()
    new.mkdir(parents=True, exist_ok=True)
    receipt = new / 'render-receipt.json'
    if receipt.exists():
        record = audio.read(receipt)
        for item in record['outputs'].values():
            if audio.sha(audio.repo_path(item['path'])) != item['sha256']:
                raise ValueError('Existing rendered output changed; preserve it')
        print('Unchanged BGM restoration already rendered; reused')
        return
    narrator = old_dir / 'narration-stem.wav'
    music = original / 'music-stem.wav'
    game = original / 'game-stem.wav'
    source_files = video.output_files(old, old_dir)
    inputs = {name: audio.artifact(path) for name, path in
              [('narration', narrator), ('music', music), ('game', game),
               ('cleanVideo', source_files['clean']), ('captionedVideo', source_files['captioned'])]}
    track = audio.repo_path(old['audio']['music']['path'])
    if audio.sha(track) != old['audio']['music']['sha256']:
        raise ValueError('Original approved Nimbus identity changed')
    music_samples, rate = sf.read(music, dtype='float64', always_2d=True)
    if rate != RATE or len(music_samples) != old['totalFrames'] * 800:
        raise ValueError('Original continuous music clock changed')
    revised = new / 'music-stem.wav'
    audio.require_new(revised, new / 'final-mix.wav', new / 'final-mix.m4a')
    sf.write(revised, music_samples * 10 ** (MUSIC_GAIN_DB / 20), RATE, subtype='PCM_24')
    duration = old['totalFrames'] / old['fps']
    audio.run_ff(['-i', narrator, '-i', revised, '-i', game,
                  '-filter_complex', GRAPH, '-map', '[out]', '-t', duration,
                  '-ar', RATE, '-c:a', 'pcm_s24le', new / 'final-mix.wav',
                  '-map', '[bgdiag]', '-t', duration, '-ar', RATE, '-c:a', 'pcm_s24le',
                  new / 'music-after-ducking.wav'], new / 'mix.log')
    audio.run_ff(['-i', new / 'final-mix.wav', '-ar', RATE, '-ac', '2',
                  '-c:a', 'aac', '-b:a', '192k', new / 'final-mix.m4a'], new / 'aac.log')
    plan = copy.deepcopy(old)
    plan.update(variant=VARIANT, status='approved-nimbus-audibility-restored',
                outputDir=audio.relative(new), outputStem='similar-game-design-' + VARIANT,
                mixFile=audio.relative(new / 'final-mix.wav'))
    plan['audio']['musicLufs'] = -28
    plan['audio']['musicDucking'] = dict(threshold=.08, ratio=2.2, attackMs=15, releaseMs=280)
    plan['bgmRestoration'] = dict(
        userEvidence=['배경음악이 빠졌는데? 우리 원래 배경음악', '재렌더해서 기존거 내리고 다시 업로드해줘'],
        basePlan=audio.artifact(OLD_PLAN), inputs=inputs,
        originalMusicAlreadyPresent=True, originalMusicLufs=-31,
        originalMusicDucking=dict(threshold=.025, ratio=3, attackMs=35, releaseMs=400),
        musicGainDb=MUSIC_GAIN_DB, musicTargetLufs=-28, mixGraph=GRAPH,
        change='Raise approved continuous Nimbus bed 3 dB and reduce excessive speech ducking.',
        narrationInputIdentical=True, gameInputAndDuckingIdentical=True,
        bothCompressedVideoStreamsCopied=True, scriptsAndCaptionClocksUnchanged=True,
        newTts=False, durationAndEndPageUnchanged=True, humanWholeListening=False)
    audio.save(PLAN, plan)
    files = video.output_files(plan, new)
    for kind, source in source_files.items():
        audio.require_new(files[kind])
        audio.run_ff(['-i', source, '-i', new / 'final-mix.m4a',
                      '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'copy',
                      '-video_track_timescale', '60000', '-movflags', '+faststart', files[kind]],
                     new / (kind + '-remux.log'))
    for name in ['captions.ko.srt', 'captions.en.srt', 'captions.ko.ass', 'captions.en.ass',
                 'captions.json', 'caption-alignment.json', 'caption-layout.json']:
        shutil.copyfile(old_dir / name, new / name)
    outputs = {k: audio.artifact(p) for k, p in files.items()}
    outputs.update({n: audio.artifact(new / n) for n in
                    ['final-mix.wav', 'final-mix.m4a', 'music-stem.wav', 'music-after-ducking.wav']})
    audio.save(receipt, dict(inputs=inputs, outputs=outputs, plan=audio.artifact(PLAN),
                            videoEncode=False, audioEncodedOnce=True, originalMediaPreserved=True))
    print('Restored Nimbus bed, encoded AAC once, copied both video streams unchanged')


def verify():
    guard('verification')
    old, old_dir, new, original = locations()
    plan = audio.read(PLAN)
    video.verify(plan, new)
    sources, files = video.output_files(old, old_dir), video.output_files(plan, new)
    proof = {'revision': VARIANT, 'checkedAt': audio.now(), 'videoStreams': {}, 'captions': {}}
    for kind in files:
        before = video.stream_hash(sources[kind], '0:v:0')
        after = video.stream_hash(files[kind], '0:v:0')
        if before != after:
            raise ValueError('Video bytes changed during audio-only restoration')
        proof['videoStreams'][kind] = dict(compressedSha256=after, identical=True)
    aac = video.stream_hash(new / 'final-mix.m4a', '0:a:0')
    if any(video.stream_hash(path, '0:a:0') != aac for path in files.values()):
        raise ValueError('Output AAC differs')
    proof['sharedAacPacketSha256'] = aac
    for language in ['ko', 'en']:
        name = 'captions.' + language + '.srt'
        if (old_dir / name).read_bytes() != (new / name).read_bytes():
            raise ValueError('Subtitle content/clock changed')
        proof['captions'][language] = audio.artifact(new / name)
    raw, rate = sf.read(old_dir / 'narration-stem.wav', dtype='int32', always_2d=True)
    proof['narrationSourceSha256'] = audio.sha(old_dir / 'narration-stem.wav')
    proof['coachingSpeechRemainsSilentFrom274_88'] = bool(np.all(raw[13194240:] == 0))
    diagnostics = {}
    for name in ['music-stem.wav', 'music-after-ducking.wav', 'final-mix.wav']:
        data, rate = sf.read(new / name, dtype='float64', always_2d=True)
        if rate != RATE or len(data) != plan['totalFrames'] * 800 or not np.isfinite(data).all():
            raise ValueError('Audio clock/nonfinite sample problem')
        db = lambda x: float(20 * np.log10(np.sqrt(np.mean(x * x)) + 1e-12))
        diagnostics[name] = dict(rmsDbfs=db(data), samples=len(data),
            windows=[dict(start=a, end=b, rmsDbfs=db(data[round(a*rate):round(b*rate)]))
                     for a,b in [(0,2),(10,20),(50,60),(100,110),(160,170),(275,280),(280,290)]])
    proof.update(audioDiagnostics=diagnostics, ttsRegenerated=False, humanWholeListening=False,
                 measuredAudibilityNotHumanListening=True,
                 loudness=audio.loudness(files['captioned'], new / 'final-aac-measure.log'))
    if float(proof['loudness']['input_tp']) > -1.5:
        raise ValueError('Encoded true peak exceeds -1.5 dBTP')
    audio.save(new / 'bgm-restoration-verification.json', proof)
    print('Both videos bit-identical, captions exact, AAC shared, music continuous, true peak passed')


def recognize():
    guard('one current encoded mix ASR')
    old, old_dir, new, original = locations()
    plan = audio.read(PLAN)
    encoded = video.output_files(plan, new)['captioned']
    decoded = new / 'encoded-audio-for-asr.wav'
    if not decoded.exists():
        audio.run_ff(['-i', encoded, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', decoded],
                     new / 'encoded-asr-decode.log')
        audio.save(new / 'encoded-asr-input.json', dict(encoded=audio.artifact(encoded), decoded=audio.artifact(decoded)))
    audio.full_asr(decoded, new / 'final-mix-asr.json', final=True)
    audio.SCRIPT = HERE.parents[1] / 'script/coaching-silent-v3'
    audio.compare(new / 'final-mix-asr.json', new / 'final-mix-text-comparison.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['render', 'verify', 'recognize'])
    args = parser.parse_args()
    {'render': render, 'verify': verify, 'recognize': recognize}[args.stage]()
