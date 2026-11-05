"""Recognize a local movie with no narration prompt. Keep word times for editing."""
import argparse, json, os, subprocess, sys
from pathlib import Path
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument("movie", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("language", choices=["english", "korean"])
args = parser.parse_args()
if args.output.exists():
    sys.exit(0)
sys.path.insert(0, str(ROOT / "qwen3-tts"))
from gpu_handoff_guard import schedule_gpu_handoff
schedule_gpu_handoff("unreal-engine-6-verse-gameplay", "cuda:0", minimum_free_mib=8192)
os.environ["HF_HUB_OFFLINE"] = "1"
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from huggingface_hub import try_to_load_from_cache
model_dir = ROOT / "qwen3-tts/models/whisper-large-v3-turbo"
if not (model_dir / "model.safetensors").exists():
    model_dir = Path(try_to_load_from_cache("openai/whisper-large-v3-turbo", "config.json")).parent
processor = AutoProcessor.from_pretrained(model_dir, local_files_only=True)
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_dir, local_files_only=True,
    dtype=torch.float16, attn_implementation="eager").to("cuda:0")
asr = pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor, device=0)
import numpy as np
pcm = np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-i",str(args.movie),
    "-vn","-ac","1","-ar","16000","-f","f32le","-"]), dtype="<f4").copy()
result = asr({"array":pcm, "sampling_rate":16000}, chunk_length_s=24, stride_length_s=4,
    return_timestamps="word", generate_kwargs={"language":args.language, "task":"transcribe"})
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(result["text"])
