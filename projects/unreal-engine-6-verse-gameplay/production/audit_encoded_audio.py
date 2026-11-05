"""Recognize the one packet-copied AAC mix, independently of the approved script.

Full mix slices share boundaries in the 280 ms inter-paragraph gaps. No text,
prompt, substitution or speech-only stem is fed to Whisper. The exact AAC hash
binds the evidence to both masters.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

import numpy as np
from edition import BASE, EXTENDED, LOCAL

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
AUDIO = LOCAL / "audio.m4a"


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main():
    os.environ["HF_HUB_OFFLINE"] = "1"
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    from huggingface_hub import try_to_load_from_cache

    plan = json.loads((LOCAL / "timeline.json").read_text(encoding="utf-8"))
    output = LOCAL / "encoded-audio-readback.json"
    signature = digest(AUDIO)
    result = {"aacContainerSha256": signature, "model": "openai/whisper-large-v3-turbo",
              "device": "CPU", "scriptPrompt": False, "scenes": []}
    if output.exists():
        previous = json.loads(output.read_text(encoding="utf-8"))
        if previous["aacContainerSha256"] == signature:
            result = previous
            if result.get("complete"):
                print("Exact AAC already reviewed.")
                return
    torch.set_num_threads(4)
    model_dir = ROOT / "qwen3-tts/models/whisper-large-v3-turbo"
    if not (model_dir / "model.safetensors").is_file():
        model_dir = Path(try_to_load_from_cache("openai/whisper-large-v3-turbo", "config.json")).parent
    processor = AutoProcessor.from_pretrained(model_dir, local_files_only=True)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_dir, local_files_only=True,
        dtype=torch.float32, low_cpu_mem_usage=True, attn_implementation="sdpa")
    asr = pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
                   feature_extractor=processor.feature_extractor, device=-1)
    pcm = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(AUDIO),
        "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]), dtype="<f4").copy()
    boundaries = [0.] + [2+s["voiceStart"]-.14 for s in plan["scenes"][1:]] + [len(pcm)/16000]
    old_result={}
    old_pcm=None
    prior=BASE
    if EXTENDED and (LOCAL/'qa/pre-coda-balance/encoded-audio-readback.json').is_file():
        prior=LOCAL/'qa/pre-coda-balance'
    if EXTENDED and (prior/'encoded-audio-readback.json').is_file():
        old_audio=prior/'audio.m4a'
        old_result=json.loads((prior/'encoded-audio-readback.json').read_text(encoding='utf-8'))
        if old_result.get('complete') and old_result['aacContainerSha256']==digest(old_audio):
            old_pcm=np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-i",str(old_audio),
                "-ac","1","-ar","16000","-f","f32le","-"]),dtype="<f4")
    for index, scene in enumerate(plan["scenes"]):
        if index < len(result["scenes"]):
            assert result["scenes"][index]["scene"] == scene["id"]
            continue
        begin, end = boundaries[index:index+2]
        section = pcm[round(begin*16000):round(end*16000)]
        reused=False
        if old_pcm is not None and index < len(old_result['scenes']):
            old=old_result['scenes'][index]
            if (old['scene']==scene['id'] and old['globalStart']==begin and old['globalEnd']==end
                    and np.array_equal(section,old_pcm[round(begin*16000):round(end*16000)])):
                recognized={'text':old['text'],'chunks':old['segments']}
                reused=True
        if not reused:
            recognized = asr({"array":section,"sampling_rate":16000},
                             return_timestamps=True,
                             generate_kwargs={"language":"korean", "task":"transcribe","num_beams":1})
        result["scenes"].append({"scene":scene["id"],"globalStart":begin,"globalEnd":end,
                                 "text":recognized["text"],"segments":recognized.get("chunks",[]),
                                 "decodedInputSha256":hashlib.sha256(section.tobytes()).hexdigest(),
                                 "reusedExactDecodedBaseline":reused,
                                 "reusedSourceAacSha256":old_result.get("aacContainerSha256") if reused else None})
        result["complete"] = len(result["scenes"]) == len(plan["scenes"])
        temporary=output.with_suffix(".tmp")
        temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        temporary.replace(output)
        print(scene["id"], recognized["text"], flush=True)


if __name__ == "__main__":
    main()
