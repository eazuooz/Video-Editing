"""Finite selected-Short audio mix and aligned level report; no TTS/ASR side effects.

Run with the qwen3-tts venv: finish-audio.py mix | report
Game section sourceStart/sourceEnd default to clip-relative seconds at 1x.
Original time bases use only each selected source's explicitly recorded offset.
Successful hashed outputs are reused, never silently overwritten.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import subprocess

import numpy as np
import soundfile as sf


R = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parents[1]
L = P / 'production/local'
S = P.name
RATE = 48000
BIN = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/'
           'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FF = os.environ.get('YAMYAM_FFMPEG', str(BIN / 'ffmpeg.exe'))
MUSIC = R / 'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.mp3'
LICENSE = MUSIC.with_suffix('.LICENSE.md')
MUSIC_SHA = 'b2609a077fae292679f25b83519f470ed308abb40d11f89bff8c6f896deefed3'
SOURCES = {}  # Populated only from this selected edit's explicit source registry.
SETTINGS = {
    'audioRevision': 'one-action-v1-voice-peak-correction',
    'voiceOffsetSeconds': 0.20, 'voiceTargetLufs': -16.0,
    'narrationCompressor': 'acompressor=threshold=0.12:ratio=3:attack=5:release=140:makeup=1,alimiter=limit=0.14:attack=5:release=80:level=false:latency=true',
    'voiceSamplePeakCeilingDbfs': -3.0,
    'nativeGameTargetLufs': -23.0, 'nativeGameSamplePeakCeilingDbfs': -6.0,
    'nativeGameMaximumPositiveGainDb': 6.0,
    'musicTargetLufs': -29.0, 'musicStartSeconds': 0.0,
    'musicFadeSeconds': 0.45, 'gameFadeInSeconds': 0.12,
    'gameFadeOutSeconds': 0.30,
    'backgroundSpeechDuckDb': 4.0, 'duckAttackMs': 15, 'duckReleaseMs': 280,
    'speechEnvelopeFloorDbfs': -42.0, 'speechEnvelopeFullDbfs': -30.0,
    'mixInitialSamplePeakCeilingDbfs': -2.3, 'encodedTruePeakMaximumDbtp': -1.5,
    'maximumEncodeAttempts': 2, 'speechSpeed': 1.0,
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as handle:
        handle.write(encoded(value))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for data in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            digest.update(data)
    return digest.hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(R).as_posix()


def run(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace')[-5000:])
    return result


def pcm(path):
    data = run([FF, '-v', 'error', '-i', str(path), '-map', '0:a:0',
                '-ar', str(RATE), '-ac', '2', '-f', 'f32le', 'pipe:1']).stdout
    samples = np.frombuffer(data, dtype='<f4').reshape(-1, 2).copy()
    if not len(samples) or not np.isfinite(samples).all():
        raise RuntimeError('Missing/nonfinite decoded PCM: ' + str(path))
    return samples


def db(samples):
    if not len(samples):
        return -240.0
    return 20 * math.log10(max(float(np.sqrt(np.mean(samples.astype(np.float64) ** 2))), 1e-12))


def loud(path):
    # Read-only measurement. loudnorm's output goes to null, never to a stem.
    result = run([FF, '-hide_banner', '-i', str(path), '-map', '0:a:0',
                  '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json',
                  '-f', 'null', '-'])
    blocks = re.findall(r'\{\s*"input_i"[\s\S]*?\}', result.stderr.decode(errors='replace'))
    if not blocks:
        raise RuntimeError('No integrated loudness result for ' + str(path))
    return json.loads(blocks[-1])


def fixed_gain(samples, measured, target, peak_ceiling, maximum_positive_db=None):
    integrated = float(measured['input_i'])
    if not math.isfinite(integrated):
        return 0.0, {'inaudible': True, 'constantGainDb': None}
    desired = 10 ** ((target - integrated) / 20)
    peak = float(np.max(np.abs(samples)))
    ceiling = 10 ** (peak_ceiling / 20) / max(peak, 1e-12)
    gain_cap = 10 ** (maximum_positive_db / 20) if maximum_positive_db is not None else math.inf
    gain = min(desired, ceiling, gain_cap)
    return gain, {'inaudible': False, 'targetLufs': target,
                  'constantGainDb': 20 * math.log10(gain),
                  'peakReserveLimitedTarget': ceiling < desired,
                  'positiveGainCapDb': maximum_positive_db,
                  'positiveGainCapLimitedTarget': gain_cap < min(desired, ceiling),
                  'sourceMeasured': measured}


def guard():
    control = read(R / 'shared/publishing/video-production-control.json')
    if control.get('selectedShortVideo') != S:
        raise RuntimeError('Selected Short changed; preserve outputs and stop costly work.')
    selected=control.get('shortsDirectSelection',{})
    if selected.get('selectedRevision') != 'one-action-v1' or not selected.get('fullProductionAuthorized'):
        raise RuntimeError('Direct selected revision authorization changed.')



def inputs():
    global SOURCES
    project = read(P / 'project.json')
    captions = read(P / 'script/captions.json')
    timing = read(L / 'visual-timing.json')
    SOURCES={key: (R/value['path'],float(value.get('originalOffsetSeconds',0))) for key,value in timing['sources'].items()}
    if any(not p.resolve().is_relative_to(R.resolve()) for p,_ in SOURCES.values()):
        raise RuntimeError('Source path escaped repository.')
    voice = Path(project['paths']['voiceNarration'])
    voice = voice if voice.is_absolute() else R / voice
    duration = float(captions['durationSeconds'])
    frames = int(captions['frames'])
    if not (math.isfinite(duration) and 0 < duration <= 180
            and abs(duration - frames / 60) < 1e-7):
        raise RuntimeError('Use the finite current60fps caption timeline, without silent60s padding.')
    if abs(float(captions['voiceOffsetSeconds']) - SETTINGS['voiceOffsetSeconds']) > 1e-8:
        raise RuntimeError('Caption/voice0.20s offset differs.')
    voice_hash = sha(voice)
    if captions.get('timingInputs', {}).get('voiceSha256') != voice_hash:
        raise RuntimeError('Caption timing does not belong to this voice hash.')
    if sha(MUSIC) != MUSIC_SHA:
        raise RuntimeError('Pixel Peeker Polka input differs from the registered approved file.')
    if not LICENSE.exists():
        raise RuntimeError('Preserve the existing Pixel Peeker Polka license/credit record.')
    sections, previous = [], 0.0
    for item in timing['sections']:
        start, end = float(item['start']), float(item['end'])
        if not (math.isfinite(start) and math.isfinite(end)
                and previous - 1e-7 <= start < end <= duration + 1e-7):
            raise RuntimeError('Invalid/overlapping visual timing section: ' + str(item.get('id')))
        previous = end
        if item['kind'] != 'game':
            continue
        source = item['source']
        if source not in SOURCES or float(item.get('rate', 1)) != 1:
            raise RuntimeError('Only the selected registered native sources at1x are allowed.')
        basis = item.get('sourceTimeBasis', timing.get('sourceTimeBasis', 'clip-relative'))
        if basis not in ['clip-relative', 'original-seconds']:
            raise RuntimeError('Unknown source time basis.')
        offset = SOURCES[source][1] if basis == 'original-seconds' else 0.0
        source_start, source_end = float(item['sourceStart']) - offset, float(item['sourceEnd']) - offset
        if not (math.isfinite(source_start) and math.isfinite(source_end)
                and 0 <= source_start < source_end
                and abs((source_end - source_start) - (end - start)) <= 1 / 60 + 1e-7):
            raise RuntimeError('Native audio must match the unslowed selected visual interval.')
        sections.append({'id': item['id'], 'source': source, 'start': start, 'end': end,
                         'sourceStart': source_start, 'sourceEnd': source_end,
                         'sourceTimeBasis': basis})
    used = sorted({section['source'] for section in sections})
    recipe = {'scriptSha256': sha(__file__), 'settings': SETTINGS,
              'voice': {'path': relative(voice), 'sha256': voice_hash},
              'durationSeconds': duration, 'frames': frames, 'gameSections': sections,
              'sources': {key: {'path': relative(SOURCES[key][0]), 'sha256': sha(SOURCES[key][0])}
                          for key in used},
              'music': {'path': relative(MUSIC), 'sha256': MUSIC_SHA,
                        'license': relative(LICENSE), 'licenseSha256': sha(LICENSE)}}
    fingerprint = hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()
    return voice, captions, timing, recipe, fingerprint


def duck_curve(stem):
    hop = RATE // 100
    padded = np.pad(stem, ((0, (-len(stem)) % hop), (0, 0)))
    rms = np.sqrt(np.mean(padded.reshape(-1, hop, 2).astype(np.float64) ** 2, axis=(1, 2)))
    levels = 20 * np.log10(np.maximum(rms, 1e-12))
    target = np.clip((levels - SETTINGS['speechEnvelopeFloorDbfs']) /
                     (SETTINGS['speechEnvelopeFullDbfs'] - SETTINGS['speechEnvelopeFloorDbfs']), 0, 1)
    attack = math.exp(-10 / SETTINGS['duckAttackMs'])
    release = math.exp(-10 / SETTINGS['duckReleaseMs'])
    envelope = np.zeros_like(target)
    last = 0.0
    for index, value in enumerate(target):
        coefficient = attack if value > last else release
        last = coefficient * last + (1 - coefficient) * value
        envelope[index] = last
    sample_envelope = np.interp(np.arange(len(stem)), np.arange(len(envelope)) * hop, envelope)
    return (10 ** (-SETTINGS['backgroundSpeechDuckDb'] * sample_envelope / 20)).astype(np.float32)


def mix():
    guard()
    voice, captions, timing, recipe, fingerprint = inputs()
    build_path = L / 'audio-build.json'
    if build_path.exists():
        built = read(build_path)
        if (built.get('fingerprint') != fingerprint or
                any(sha(R / entry['path']) != entry['sha256'] for entry in built['artifacts'].values())):
            raise RuntimeError('Existing successful audio differs; preserve/version it before a new mix.')
        print('Reused hashed successful mix: ' + built['artifacts']['final-mix.m4a']['path'])
        return report()
    names = ['narration-source-timeline.wav', 'narration-prepared-stem.wav', 'narration-stem.wav', 'game-stem.wav',
             'music-stem.wav', 'background-stem.wav', 'final-mix.wav', 'final-mix.m4a']
    if any((L / name).exists() for name in names):
        raise RuntimeError('Unreceipted audio outputs exist; inspect/version them, do not overwrite.')
    count = round(recipe['durationSeconds'] * RATE)
    source_voice = pcm(voice)
    if abs(len(source_voice) / RATE - float(captions['voiceDurationSeconds'])) > 2 / RATE:
        raise RuntimeError('Voice duration differs from the measured caption input.')
    offset = round(SETTINGS['voiceOffsetSeconds'] * RATE)
    if offset + len(source_voice) > count:
        raise RuntimeError('The full unchanged voice does not fit; never trim spoken PCM.')
    source_timeline = np.zeros((count, 2), np.float32)
    source_timeline[offset:offset + len(source_voice)] = source_voice
    work = L / 'audio-work' / (fingerprint[:12] + '-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                              + '-' + str(os.getpid()))
    work.mkdir(parents=True, exist_ok=False)
    sf.write(work / 'narration-source-timeline.wav', source_timeline, RATE, subtype='FLOAT')
    run([FF, '-v', 'warning', '-n', '-i', str(work / 'narration-source-timeline.wav'),
         '-af', SETTINGS['narrationCompressor'], '-c:a', 'pcm_f32le',
         str(work / 'narration-prepared-stem.wav')])
    prepared = pcm(work / 'narration-prepared-stem.wav')
    if len(prepared) != count:
        raise RuntimeError('Narration preparation changed the sample count/timing.')
    original_voice_measured = loud(voice)
    prepared_measured = loud(work / 'narration-prepared-stem.wav')
    voice_gain, voice_levels = fixed_gain(prepared, prepared_measured, SETTINGS['voiceTargetLufs'],
                                           SETTINGS['voiceSamplePeakCeilingDbfs'])
    if voice_gain <= 0:
        raise RuntimeError('Selected voice is inaudible.')
    stem = prepared * voice_gain
    native = np.zeros_like(stem)
    source_cache, source_levels, events = {}, {}, []
    for key, entry in recipe['sources'].items():
        source = R / entry['path']
        decoded = pcm(source)
        gain, measured = fixed_gain(decoded, loud(source), SETTINGS['nativeGameTargetLufs'],
                                    SETTINGS['nativeGameSamplePeakCeilingDbfs'],
                                    SETTINGS['nativeGameMaximumPositiveGainDb'])
        source_cache[key] = decoded * gain
        source_levels[key] = measured
    for section in recipe['gameSections']:
        src = source_cache[section['source']]
        first, last = round(section['sourceStart'] * RATE), round(section['sourceEnd'] * RATE)
        destination = round(section['start'] * RATE)
        length = round(section['end'] * RATE) - destination
        if last > len(src) + 2 or first + length > len(src) + 2:
            raise RuntimeError('Game interval exceeds the decoded source.')
        clip = src[first:first + length].copy()
        if len(clip) < length:
            clip = np.pad(clip, ((0, length - len(clip)), (0, 0)))
        fade_in = min(round(SETTINGS['gameFadeInSeconds'] * RATE), len(clip) // 2)
        fade_out = min(round(SETTINGS['gameFadeOutSeconds'] * RATE), len(clip) // 2)
        if fade_in:
            clip[:fade_in] *= np.linspace(0, 1, fade_in, dtype=np.float32)[:, None]
        if fade_out:
            clip[-fade_out:] *= np.linspace(1, 0, fade_out, dtype=np.float32)[:, None]
        native[destination:destination + length] += clip
        events.append({**section, 'destinationSamples': [destination, destination + length],
                       'sourceSamples': [first, first + length],
                       'audio': 'synchronized original source mix; native music/voices, if present, not separated',
                       'fabricatedEffects': False})
    music_source = pcm(MUSIC)
    music_gain, music_levels = fixed_gain(music_source, loud(MUSIC), SETTINGS['musicTargetLufs'], -12)
    music = np.zeros_like(stem)
    music_start = round(SETTINGS['musicStartSeconds'] * RATE)
    length = count - music_start
    if length <= 0 or len(music_source) < length:
        raise RuntimeError('The selected continuous Pixel Peeker Polka excerpt does not cover this timeline.')
    bed = music_source[:length].copy() * music_gain
    fade = min(round(SETTINGS['musicFadeSeconds'] * RATE), len(bed) // 2)
    bed[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)[:, None]
    bed[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)[:, None]
    music[music_start:] = bed
    duck = duck_curve(stem)
    # Short profile: only added BGM ducks; keep synchronized original game effects.
    music *= duck[:, None]
    combined = stem + native + music
    overall = min(1.0, 10 ** (SETTINGS['mixInitialSamplePeakCeilingDbfs'] / 20) /
                  max(float(np.max(np.abs(combined))), 1e-12))
    attempts, accepted = [], None
    for attempt in range(1, SETTINGS['maximumEncodeAttempts'] + 1):
        wav = work / f'attempt-{attempt}.wav'
        aac = work / f'attempt-{attempt}.m4a'
        sf.write(wav, combined * overall, RATE, subtype='FLOAT')
        run([FF, '-v', 'warning', '-n', '-i', str(wav), '-c:a', 'aac', '-b:a', '192k',
             '-ar', str(RATE), '-ac', '2', '-movflags', '+faststart', str(aac)])
        measured = loud(aac)
        peak = float(measured['input_tp'])
        attempts.append({'attempt': attempt, 'uniformMixGainDb': 20 * math.log10(overall),
                         'encodedMeasured': measured})
        if math.isfinite(peak) and peak <= SETTINGS['encodedTruePeakMaximumDbtp']:
            accepted = (wav, aac)
            break
        if not math.isfinite(peak):
            raise RuntimeError('Final AAC true peak is not finite.')
        overall *= 10 ** ((SETTINGS['encodedTruePeakMaximumDbtp'] - peak - 0.35) / 20)
    if accepted is None:
        raise RuntimeError('Bounded AAC true-peak check failed; keep staging evidence for review.')
    final_stems = {'narration-stem.wav': stem * overall, 'game-stem.wav': native * overall,
                   'music-stem.wav': music * overall, 'background-stem.wav': (native + music) * overall}
    for name, data in final_stems.items():
        if not np.isfinite(data).all():
            raise RuntimeError('Nonfinite final stem.')
        sf.write(work / name, data, RATE, subtype='FLOAT')
    accepted[0].rename(work / 'final-mix.wav')
    accepted[1].rename(work / 'final-mix.m4a')
    guard()
    if inputs()[-1] != fingerprint:
        raise RuntimeError('Audio inputs changed during production; preserve staging, do not publish stale work.')
    for name in names:
        if (L / name).exists():
            raise RuntimeError('Another writer created a final audio output; preserve both sets.')
    for name in names:
        (work / name).rename(L / name)
    artifacts = {name: {'path': relative(L / name), 'sha256': sha(L / name)} for name in names}
    save_new(build_path, {
        'status': 'encoded-technical-measurement-complete; final-ASR-and-listening-pending',
        'fingerprint': fingerprint, 'recipe': recipe, 'artifacts': artifacts,
        'narrationConstantGainDb': 20 * math.log10(voice_gain * overall),
        'narrationDucked': False, 'narrationFades': False, 'narrationSpeedChanged': False,
        'sourceToTimeline': {'offsetSeconds': 0.20, 'sourceSamples': len(source_voice),
                             'destinationSamples': [offset, offset + len(source_voice)]},
        'voiceLevels': voice_levels, 'sourceLevels': source_levels, 'musicLevels': music_levels,
        'originalVoiceMeasured': original_voice_measured,
        'preparedNarrationMeasured': prepared_measured,
        'narrationPreparation': {'filter': SETTINGS['narrationCompressor'],
                                 'originalPcmPreserved': True, 'timingAndSampleCountPreserved': True,
                                 'compressedPreparedToStemConstantGain': True},
        'gameEvents': events, 'addedEffects': [], 'addedMusicDuckedByVoiceOnly': True, 'nativeGameDucked': False,
        'duckGainDbRange': [20 * math.log10(float(duck.min())), 20 * math.log10(float(duck.max()))],
        'encodeAttempts': attempts, 'humanListening': 'pending', 'finalMixAsr': 'pending; separate one-time full-input check',
        'credit': 'Pixel Peeker Polka - faster Kevin MacLeod (incompetech.com); CC BY4.0; exact credit in LICENSE',
        'nativeAudioLimit': 'Original mixed game audio preserved. No claimed music/voice separation or fabricated effects.',
    })
    print('Mixed finite timeline: ' + str(recipe['durationSeconds']) + 's')
    report()


def grouped(rows, key, minimum=0.5):
    """Require at least0.5s of consecutive100ms measurement centers.

    Counting the union of overlapping400ms windows incorrectly promoted two
    flagged centers (only0.2s) into a sustained0.5s finding in the v1 report.
    """
    groups, active = [], []

    def finish():
        if len(active) * 0.1 + 1e-8 >= minimum:
            groups.append({'start': active[0]['start'] + 0.15,
                           'end': active[-1]['start'] + 0.25,
                           'windowCount': len(active),
                           'consecutiveMeasurementSeconds': round(len(active) * 0.1, 6),
                           'measurementContext': [active[0]['start'], active[-1]['end']]})

    for row in rows:
        if row[key] and (not active or row['start'] - active[-1]['start'] <= 0.101):
            active.append(row)
        else:
            finish()
            active = [row] if row[key] else []
    finish()
    return groups


def merged_contexts(groups, duration):
    """One playback range can resolve several overlapping candidate contexts."""
    expanded = sorted([{'start': max(0.0, row['start'] - 2),
                        'end': min(duration, row['end'] + 2)} for row in groups],
                      key=lambda row: row['start'])
    output = []
    for row in expanded:
        if output and row['start'] <= output[-1]['end']:
            output[-1]['end'] = max(output[-1]['end'], row['end'])
        else:
            output.append(dict(row))
    return output


def report():
    guard()
    voice, captions, timing, recipe, fingerprint = inputs()
    build = read(L / 'audio-build.json')
    if build['fingerprint'] != fingerprint:
        raise RuntimeError('Report input recipe differs from the current successful mix.')
    for entry in build['artifacts'].values():
        if sha(R / entry['path']) != entry['sha256']:
            raise RuntimeError('A successful audio artifact changed.')
    target = L / 'audio-continuity.json'
    if target.exists():
        cached = read(target)
        if cached.get('fingerprint') != fingerprint:
            raise RuntimeError('Preserve/version the previous audio continuity evidence.')
        print('Reused aligned source/stem/final report: ' + relative(target))
        return
    source, stem = pcm(L / 'narration-source-timeline.wav'), pcm(L / 'narration-stem.wav')
    prepared = pcm(L / 'narration-prepared-stem.wav')
    background, decoded = pcm(L / 'background-stem.wav'), pcm(L / 'final-mix.m4a')
    count = round(recipe['durationSeconds'] * RATE)
    if not (len(source) == len(prepared) == len(stem) == len(background) == count
            and count <= len(decoded) <= count + 2048):
        raise RuntimeError('Stem/final AAC lengths differ from the exact timeline.')
    decoded_sample_count = len(decoded)
    decoded = decoded[:count]
    expected_gain = 10 ** (build['narrationConstantGainDb'] / 20)
    deviation = float(np.max(np.abs(stem - prepared * expected_gain)))
    if deviation > 2e-6:
        raise RuntimeError('Prepared narration was not preserved under one constant gain.')
    # Known-background subtraction is a diagnostic approximation after AAC,
    # not a claim that encoded speech has been perfectly separated.
    speech_estimate = decoded - background
    width, step = round(0.4 * RATE), round(0.1 * RATE)
    rows = []
    for first in range(0, max(1, count - width + 1), step):
        last = min(count, first + width)
        a, b, c = source[first:last], stem[first:last], speech_estimate[first:last]
        prepared_window = prepared[first:last]
        source_level = db(a)
        center = (first + last) / (2 * RATE)
        inside_cue = any(cue['start'] <= center <= cue['end'] for cue in captions['cues'])
        if source_level < -60 or (not inside_cue and source_level < -50):
            continue
        energy = float(np.sum(b.astype(np.float64) ** 2))
        transfer = float(np.sum(b.astype(np.float64) * c) / max(energy, 1e-16))
        transfer_db = 20 * math.log10(max(transfer, 1e-12))
        background_level = db(background[first:last])
        rows.append({'start': first / RATE, 'end': last / RATE, 'sourceRmsDbfs': source_level,
                     'preparedRmsDbfs': db(prepared_window), 'stemRmsDbfs': db(b),
                     'finalMixRmsDbfs': db(decoded[first:last]),
                     'backgroundSubtractedEstimateRmsDbfs': db(c),
                     'sourceToPreparedGainDb': db(prepared_window) - source_level,
                     'preparedToStemGainDb': db(b) - db(prepared_window),
                     'sourceToStemGainDb': db(b) - source_level,
                     'encodedSpeechTransferDb': transfer_db, 'backgroundRmsDbfs': background_level,
                     'speechToBackgroundDb': db(b) - background_level,
                     'withinCaptionSpeechRange': inside_cue,
                     'encodedAttenuationCandidate': transfer_db < -3,
                     'maskingCandidate': inside_cue and db(b) - background_level < 6})
    for row in rows:
        nearby = [other['sourceRmsDbfs'] for other in rows
                  if 0.45 <= abs(other['start'] - row['start']) <= 2.5]
        reference = float(np.median(nearby)) if nearby else row['sourceRmsDbfs']
        row['neighborSourceMedianDbfs'] = reference
        row['sourceLowLevelCandidate'] = (row['withinCaptionSpeechRange']
                                           and row['sourceRmsDbfs'] < reference - 6)
    joins = sorted({0.20, SETTINGS['musicStartSeconds'],
                    *[float(item['start']) for item in timing['sections']],
                    *[float(item['end']) for item in timing['sections']],
                    *[float(cue['start']) for i, cue in enumerate(captions['cues'])
                      if i and cue.get('lineIndex') != captions['cues'][i - 1].get('lineIndex')]})
    join_rows = []
    for join in joins:
        before = [row for row in rows if join - 2 <= row['start'] < join - 0.1]
        after = [row for row in rows if join + 0.1 <= row['start'] < join + 2]
        difference = (float(np.median([row['stemRmsDbfs'] for row in after])) -
                      float(np.median([row['stemRmsDbfs'] for row in before]))) if before and after else None
        source_difference = (float(np.median([row['sourceRmsDbfs'] for row in after])) -
                             float(np.median([row['sourceRmsDbfs'] for row in before]))) if before and after else None
        join_rows.append({'seconds': join, 'speechActiveMedianDifferenceDb': difference,
                          'originalSpeechActiveMedianDifferenceDb': source_difference,
                          'processingChangeAcrossJoinDb': difference - source_difference
                          if difference is not None and source_difference is not None else None,
                          'candidate': difference is not None and abs(difference) >= 3,
                          'comparisonWindowSeconds': 2})
    attenuation = grouped(rows, 'encodedAttenuationCandidate')
    low = grouped(rows, 'sourceLowLevelCandidate')
    masking = grouped(rows, 'maskingCandidate')
    # Reuse the successful encode's exact-hash loudness/true-peak measurement.
    final_levels = build['encodeAttempts'][-1]['encodedMeasured']
    if float(final_levels['input_tp']) > SETTINGS['encodedTruePeakMaximumDbtp']:
        raise RuntimeError('Final encoded true peak exceeds the ceiling.')
    status = ('technical-continuity-pass; contextual-and-human-listening-pending'
              if not attenuation else 'encoded-attenuation-candidates; contextual-review-required')
    save_new(target, {
        'status': status, 'fingerprint': fingerprint,
        'artifacts': build['artifacts'], 'fullDecodedAudioChecked': True,
        'voiceOffsetSeconds': 0.20, 'durationSeconds': recipe['durationSeconds'],
        'frames': recipe['frames'], 'aacDecodedSamplesBeforePaddingTrim': decoded_sample_count,
        'preparedToStemConstantSpeechGainVerified': True,
        'originalToStemPureConstantGainClaimed': False,
        'preparedStemMaximumSampleDeviation': deviation,
        'speechDuckingOrSpeechFadesApplied': False, 'windowSeconds': 0.4, 'stepSeconds': 0.1,
        'sourceMeasured': build['originalVoiceMeasured'],
        'preparedNarrationMeasured': build['preparedNarrationMeasured'],
        'narrationPreparation': build['narrationPreparation'],
        'narrationStemMeasured': loud(L / 'narration-stem.wav'),
        'finalEncodedMeasured': final_levels, 'speechActiveWindows': rows, 'joins': join_rows,
        'sustainedEncodedAttenuationCandidates': attenuation,
        'sustainedSourceLowLevelCandidates': low, 'sustainedMaskingCandidates': masking,
        'measurementLimits': 'Source low-level and join differences may be natural prosody. Known-background subtraction afterAAC is approximate. Candidates require aligned contextual playback/listening; never cleared from LUFS or ASR alone.',
        'candidateGrouping': 'At least5 consecutive100ms centers;400ms windows are not counted as independent durations. Playback contexts merge overlaps.',
        'contextPlaybackRequiredRanges': merged_contexts(low + masking + attenuation + [
            {'start': item['seconds'], 'end': item['seconds']}
            for item in join_rows if item['candidate']
        ], recipe['durationSeconds']),
        'humanListening': 'pending', 'pronunciation': 'pending', 'finalMixAsr': 'pending; separate current full-input ASR',
    })
    print(encoded({'audioReport': relative(target), 'status': status,
                   'sustainedEncodedAttenuationCandidates': len(attenuation),
                   'sustainedSourceLowLevelCandidates': len(low),
                   'sustainedMaskingCandidates': len(masking), 'humanListening': 'pending'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['mix', 'report'])
    args = parser.parse_args()
    {'mix': mix, 'report': report}[args.command]()


if __name__ == '__main__':
    main()
