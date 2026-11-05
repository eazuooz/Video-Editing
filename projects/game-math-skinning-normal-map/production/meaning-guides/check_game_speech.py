"""Check intelligibility at the three places where native game sound overlaps speech."""
import os
os.environ.update(OMP_NUM_THREADS="3", MKL_NUM_THREADS="3", OPENBLAS_NUM_THREADS="2",
                  HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
from pathlib import Path
from difflib import SequenceMatcher
import re

import torch
import soundfile as sf
from scipy.signal import resample_poly
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq, pipeline
from prepare import P, read, save


def normalize(text):
    return re.sub(r"[^가-힣a-z0-9]", "", text.lower())


def check():
    work = P / "production/local/render-v2"
    queue = read(work / "queue.json")
    timing = read(Path(queue["audioDirectory"]) / "narration.timing.json")
    scenes = {item["scene_id"]: item for item in timing["entries"]}
    model_dir = Path.home() / ".cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9"
    torch.set_num_threads(3)
    processor = AutoProcessor.from_pretrained(str(model_dir), local_files_only=True)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_dir), dtype=torch.float32,
                                                       local_files_only=True, use_safetensors=True)
    transcribe = pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
                          feature_extractor=processor.feature_extractor, device="cpu")
    records = []
    with sf.SoundFile(work / "final-mix-review/actual-final-body-mono.wav") as body:
        for cut in queue["cuts"]:
            if cut["kind"] != "actual-gameplay":
                continue
            entry = scenes[cut["scene"]]
            i = round(entry["start"] * body.samplerate)
            body.seek(i)
            wave = body.read(round(entry["end"] * body.samplerate) - i, dtype="float32")
            result = transcribe({"array": resample_poly(wave, 1, 3).copy(), "sampling_rate": 16000},
                                generate_kwargs={"language":"korean","task":"transcribe"},
                                return_timestamps=True, chunk_length_s=28, stride_length_s=4)
            a, b = normalize(entry["text"]), normalize(result["text"])
            record = dict(scene=cut["scene"], expected=entry["text"], heard=result["text"],
                          similarity=round(SequenceMatcher(None, a, b, autojunk=False).ratio(), 4))
            records.append(record)
            print(record, flush=True)
    master = read(work / "final-qa/report.json")["files"]["captioned"]["sha256"]
    save(work / "final-qa/game-speech.json",
         dict(masterSha256=master, method="CPU ASR of encoded mix; no text prompt", items=records))


if __name__ == "__main__":
    check()
