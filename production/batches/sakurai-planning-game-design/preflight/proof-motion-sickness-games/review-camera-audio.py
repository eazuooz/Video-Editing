"""Read back our existing public camera lectures before a duplicate verdict.

Research only. Does not generate a new script or use a GPU. Raw audio stays
outside Git; timestamped ASR is imperfect and needs direct content review.
"""
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent
MODEL = ROOT / "qwen3-tts/models/whisper-large-v3-turbo"
torch.set_num_threads(2)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL, dtype=torch.float32, low_cpu_mem_usage=True, use_safetensors=True
).to("cpu")
processor = AutoProcessor.from_pretrained(MODEL)
asr = pipeline("automatic-speech-recognition", model=model,
    tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor,
    dtype=torch.float32, device="cpu")
for video_id in ["tmL7WV17r5g", "upO4CW3INvE", "qfkL1VjnYo8"]:
    files = [p for p in (BASE / "audio").glob(video_id + ".*")
             if p.suffix in [".m4a", ".webm"]]
    if not files:
        raise FileNotFoundError(video_id)
    audio = files[0]
    output = BASE / (video_id + ".asr.json")
    digest = hashlib.sha256(audio.read_bytes()).hexdigest()
    if output.exists() and json.loads(output.read_text("utf-8")).get("audioSha256") == digest:
        print("EXISTING", video_id, flush=True)
        continue
    print("START", video_id, flush=True)
    result = asr(str(audio), chunk_length_s=30, stride_length_s=5,
                 generate_kwargs={"language": "korean", "task": "transcribe"},
                 return_timestamps=True)
    evidence = {"videoId": video_id, "audioSha256": digest, "device": "cpu",
                "model": str(MODEL), "purpose": "duplicate-content-review-only",
                "manualContentReview": "pending", **result}
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("DONE", video_id, flush=True)
