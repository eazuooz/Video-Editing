"""Check the *encoded* narration against its source throughout M22, including game cuts."""
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from prepare import P, read, save, sha


def measure():
    work = P / "production/local/render-v2"
    queue = read(work / "queue.json")
    qa = read(work / "final-qa/report.json")
    reference = work / "composite/narration-normalized.wav"
    mix = work / "final-mix-review/actual-final-body-mono.wav"
    timing = read(Path(queue["audioDirectory"]) / "narration.timing.json")
    output = Path(qa["files"]["captioned"]["path"])
    assert sha(output) == qa["files"]["captioned"]["sha256"]
    result = []
    with sf.SoundFile(reference) as source, sf.SoundFile(mix) as final:
        rate = final.samplerate
        assert rate == source.samplerate == 48000 and final.channels == 1
        assert 0 <= len(source) - len(final) <= rate / 60 + 2
        for entry in timing["entries"]:
            start = round(entry["start"] * rate)
            end = round(entry["end"] * rate)
            source.seek(start)
            final.seek(start)
            x = source.read(end - start, always_2d=True).sum(axis=1)
            if source.channels == 2:
                x *= 2 ** -0.5
            y = final.read(end - start)
            assert len(x) == len(y)
            block = rate // 10
            limit = len(x) // block * block
            a, b = (s[:limit].reshape(-1, block) for s in (x, y))
            power = (a * a).mean(axis=1)
            voiced = power > 10 ** (-35 / 10)
            assert np.any(voiced)
            a, b, power = a[voiced], b[voiced], power[voiced]
            gain = (a * b).mean(axis=1) / power
            gain_db = 20 * np.log10(np.maximum(np.abs(gain), 1e-12))
            corr = (a * b).mean(axis=1) / np.sqrt(power * np.maximum((b * b).mean(axis=1), 1e-12))
            suspect = np.flatnonzero(np.abs(gain_db) > 3)
            result.append(dict(scene=entry["scene_id"], voicedWindows=len(corr),
                               correlationP05=round(float(np.quantile(corr, .05)), 4),
                               minGainDb=round(float(gain_db.min()), 2),
                               maxGainDb=round(float(gain_db.max()), 2),
                               medianGainDb=round(float(np.median(gain_db)), 2),
                               windowsBeyond3dB=len(suspect),
                               inspectAtVideoSeconds=[round(2+entry["start"]+np.flatnonzero(voiced)[index]*.1, 3)
                                                      for index in suspect]))
    evidence = dict(masterSha256=qa["files"]["captioned"]["sha256"], sourceSha256=sha(reference),
                    decodedBodySha256=sha(mix), sampleRate=rate, scenes=result, humanListening=False)
    save(work / "final-qa/voice-preservation.json", evidence)
    print(json.dumps(dict(scenes=len(result), voicedWindows=sum(r["voicedWindows"] for r in result),
                          lowestP05=min(r["correlationP05"] for r in result),
                          beyond3dB=sum(r["windowsBeyond3dB"] for r in result))))


if __name__ == "__main__":
    measure()
