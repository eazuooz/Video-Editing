"""Measure source → stem → encoded mix in corresponding 400 ms speech windows."""
from pathlib import Path
import hashlib
import json
import subprocess
from statistics import median

import numpy as np
import soundfile as sf
from edition import LOCAL, voice_dir

P = Path(__file__).resolve().parents[1]
L = LOCAL
FS = 24000


def db(value):
    return float(20*np.log10(max(float(value), 1e-9)))


def energy(signal):
    return np.sqrt(np.mean(signal*signal, dtype=np.float64)) if len(signal) else 0


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def decode(path):
    return np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-i",str(path),
        "-ac","1","-ar",str(FS),"-f","f32le","-"]), dtype="<f4")


def consecutive(rows, seek):
    """Join threshold-crossing runs; reject isolated windows and keep true duration."""
    runs=[]
    for row in rows:
        if not seek(row):continue
        if runs and row["offset"]-runs[-1][-1]["offset"] <= .101:
            runs[-1].append(row)
        else:runs.append([row])
    return [[r[0]["offset"],round(r[-1]["offset"]+.4,2)] for r in runs
            if r[-1]["offset"]-r[0]["offset"]+.4 >= .499]


def main():
    plan=json.loads((L/"timeline.json").read_text(encoding="utf-8"))
    narration=decode(L/"narration-stem.wav")
    encoded=decode(L/"audio.m4a")
    result=[]
    for scene in plan["scenes"]:
        name=scene["id"]
        voice=voice_dir(name)
        source=voice/f"chunks/{name}-scene.wav"
        raw,rate=sf.read(source,dtype="float32")
        assert rate==FS
        words=json.loads((voice/f"asr/{name}.json").read_text(encoding="utf-8"))["words"]
        mask=np.zeros(len(raw),dtype=bool)
        for word in words:
            a,b=word["timestamp"]
            if a is not None and b is not None:
                mask[max(0,round(a*FS)):min(len(raw),round(b*FS))]=True
        origin=round((2+scene["voiceStart"])*FS)
        rows=[]
        for i in range(0,len(raw)-int(.4*FS)+1,int(.1*FS)):
            m=mask[i:i+int(.4*FS)]
            if m.sum()<.24*FS:continue
            x=raw[i:i+len(m)][m].astype('float64')
            y=narration[origin+i:origin+i+len(m)][m].astype('float64')
            z=encoded[origin+i:origin+i+len(m)][m].astype('float64')
            if energy(x)<1e-5 or energy(y)<1e-5:continue
            # Estimated voice gain is regression onto the actual processed narration.
            # Uncorrelated music is measured as loudness of the residual instead
            # of interpreting the mixed RMS as the voice level.
            k=np.sum(z*y, dtype=np.float64)/max(np.sum(y*y, dtype=np.float64),1e-9)
            rows.append(dict(offset=round(i/FS,2),source=db(energy(x)),stem=db(energy(y)),
                             sourceToStem=db(energy(y)/energy(x)),voiceInMixGain=db(abs(k)),
                             voiceToResidual=db(energy(y*k)/max(energy(z-y*k),1e-9))))
        assert rows
        for j,row in enumerate(rows):
            close=[v for v in rows[max(0,j-28):j+29] if abs(v['offset']-row['offset'])<3.1]
            row["sourceLocalDip"]=median(x["source"] for x in close)-row["source"]
            row["extraStemDip"]=median(x["sourceToStem"] for x in close)-row["sourceToStem"]
            row["extraMixDip"]=median(x["voiceInMixGain"] for x in close)-row["voiceInMixGain"]
        result.append(dict(scene=name,sourceSha256=digest(source),sampledSpeechWindows=len(rows),
            sourceSpeechMedianDbfs=round(median(x["source"] for x in rows),2),
            stemSpeechMedianDbfs=round(median(x["stem"] for x in rows),2),
            mixVoiceGainMedianDb=round(median(x["voiceInMixGain"] for x in rows),2),
            voiceToResidualMedianDb=round(median(x["voiceToResidual"] for x in rows),2),
            voiceToResidualP10Db=round(float(np.percentile([x["voiceToResidual"] for x in rows],10)),2),
            preexistingRawDipCandidates=consecutive(rows,lambda x:x["sourceLocalDip"]>=6),
            addedStemDipCandidates=consecutive(rows,lambda x:x["extraStemDip"]>=6),
            addedMixDipCandidates=consecutive(rows,lambda x:x["extraMixDip"]>=6),
            possibleMasking=consecutive(rows,lambda x:x["voiceToResidual"]<3)))
    joins=[dict(before=a["scene"],after=b["scene"],changeDb=round(b["stemSpeechMedianDbfs"]-a["stemSpeechMedianDbfs"],2))
           for a,b in zip(result,result[1:])]
    output={"aacSha256":digest(L/"audio.m4a"),"method":"400 ms, 100 ms hop, >=240 ms of word-aligned speech. Residual includes music and AAC differences. Levels are dBFS, not LUFS.",
        "scenes":result,"joins":joins,"humanListening":"pending"}
    (L/"encoded-level-continuity.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
