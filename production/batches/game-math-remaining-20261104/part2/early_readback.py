"""Audit existing word evidence against the finished recording without running a model."""
import argparse
import hashlib
import re
import soundfile as sf
from edition import ROOT,BATCH,read,save,sha

def verify(episode,revision):
    items=read(BATCH/"batch.json")["items"][2:]
    row=next(r for r in items if r["id"]==episode)
    assert re.fullmatch(r"audio-v\d+",revision)
    project=ROOT/"projects"/row["slug"];folder=project/"production/local"/revision
    timing=read(folder/"narration.timing.json")
    checked=[]
    with sf.SoundFile(folder/"narration.wav") as audio:
        for entry in timing["entries"]:
            key=f"{entry['scene_id']}-{entry['paragraph']:02}"
            early=folder/"review/early-pcm"/(key+".json")
            if not early.is_file():continue
            evidence=read(early);sr=audio.samplerate
            start=round(entry["start"]*sr);end=round(entry["end"]*sr)
            audio.seek(start);pcm=audio.read(end-start,dtype="float32")
            digest=hashlib.sha256(pcm.tobytes()).hexdigest()
            assert sr==evidence["sampleRate"] and digest==evidence["pcmSha256"]
            assert entry["text"]==evidence["sourceText"]
            adopted=read(folder/"review/paragraphs"/(key+".json"))
            assert adopted["earlyReview"]["verifiedPcmSha256"]==digest
            checked.append(dict(id=key,samples=len(pcm),pcmSha256=digest,cacheSha256=sha(early)))
    assert checked
    save(project/"production/part2-review"/(revision+"-word-evidence.json"),dict(episode=episode,revision=revision,
        finishedWavSha256=sha(folder/"narration.wav"),verified=checked,totalParagraphs=len(timing["entries"]),
        humanListening=False,method="Read the final WAV at its measured paragraph times and require exact decoded sample identity."))
    print(episode,revision,len(checked),"verified recorded paragraphs.")

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("episode");parser.add_argument("revision")
    a=parser.parse_args();verify(a.episode,a.revision)
