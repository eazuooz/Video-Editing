"""Generate the approved Shorts voice for the exact 36-episode review revision."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import wave

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QWEN = ROOT / "qwen3-tts"
LEGACY = HERE.parent / "architectural-111-20261106"
APPROVED = ROOT / "projects/shorts-mario-one-action/production/local/tts-execution.json"
PLAN_PATH = HERE / "episodes-v1.json"
PLAN_SHA = "ea0224cbea04e050a295dfa298a87caa67b02633bf6b6586f9114f7d4453dcc6"
PROJECT = "elden-ring-development-36-approved-voice"
DEFAULT_OUTPUT = Path("C:/Users/1/Videos/YamyamProduction/elden-ring-development-36/pc-review-v2")
MIN_FREE = 8192
ALLOCATOR_LIMIT = 7168


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    target = importlib.util.module_from_spec(spec)
    sys.modules[name] = target
    spec.loader.exec_module(target)
    return target


def resource_guard():
    sys.path.insert(0, str(LEGACY))
    return module("elden_ring_cooperative_resource_guard", LEGACY / "run-first-native.py")


def headroom():
    command = ["nvidia-smi", "--query-gpu=memory.free,utilization.gpu", "--format=csv,noheader,nounits"]
    free, usage = map(int, subprocess.check_output(command, text=True).splitlines()[0].split(","))
    return free, usage


def busy(guard, minimum):
    reason = guard.busy_reason()
    if reason:
        return reason
    free, usage = headroom()
    return f"GPU {free} MiB free / {usage}% utilization" if free < minimum or usage >= 15 else None


def pinned_plan():
    if sha(PLAN_PATH) != PLAN_SHA:
        raise ValueError("The 36 reviewed scripts changed")
    plan = read(PLAN_PATH)
    if [ep["id"] for ep in plan] != [f"{number:02d}" for number in range(1, 37)]:
        raise ValueError("The review must contain IDs 01–36 in order")
    return plan


def stage_voice(engine, output):
    takes = output / "approved-voice"
    takes.mkdir(parents=True, exist_ok=True)
    prior = read(APPROVED)["inputs"]
    if sha(engine.REFERENCE) != prior["reference"] or sha(engine.REFERENCE_TEXT_PATH) != prior["referenceText"]:
        raise ValueError("The approved Shorts speaker inputs changed")
    engine.CHUNK_DIR = takes
    engine.MAX_RENDER_ATTEMPTS = 1
    engine.MAX_NEW_TOKENS = 4096
    return [engine.RenderItem(f"{episode['id']}-{index}", text, takes / f"{episode['id']}-{index}.wav")
            for episode in pinned_plan() for index, text in enumerate(episode["narrationKo"])]


def pcm(path):
    with wave.open(str(path), "rb") as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) != (1, 2, 24000):
            raise ValueError(f"Unexpected raw WAV format: {path.name}")
        frames = wav.getnframes()
        if not frames or len(wav.readframes(frames)) != frames * 2:
            raise ValueError(f"Unreadable raw WAV: {path.name}")
    return {"file": path.name, "sha256": sha(path), "samples": frames, "sampleRate": 24000}


def render(output, limit, only):
    sys.path.insert(0, str(QWEN))
    import render_narration as engine
    from gpu_handoff_guard import schedule_gpu_handoff

    items = stage_voice(engine, output)
    config = {"planSha256": PLAN_SHA, "referenceSha256": sha(engine.REFERENCE),
              "referenceTextSha256": sha(engine.REFERENCE_TEXT_PATH), "engineSha256": sha(QWEN / "render_narration.py"),
              "model": engine.MODEL_DIR.name, "sceneBatchSize": 1, "allocatorLimitMiB": ALLOCATOR_LIMIT}
    identity = output / "voice-identity-v2.json"
    if identity.exists() and read(identity) != config:
        raise ValueError("Existing raw voice belongs to a different identity")
    save(identity, config)
    for item in items:
        if item.path.exists():
            pcm(item.path)
    pending = [item for item in items if not item.path.exists() and (not only or item.key in only)]
    if pending:
        guard = resource_guard()
        worker = guard.SingleWorker(path=output / "voice-worker.json")
        worker.acquire()
        try:
            deadline = time.monotonic() + limit * 60
            previous = None
            while reason := busy(guard, MIN_FREE):
                if reason != previous:
                    print(f"Waiting for approved voice resources: {reason}", flush=True)
                    previous = reason
                if time.monotonic() >= deadline:
                    raise RuntimeError("Approved voice resource window did not open")
                time.sleep(15)
            free, usage = headroom()
            print(f"Approved voice guard passed: {free} MiB free / {usage}% utilization", flush=True)
            schedule_gpu_handoff(PROJECT, "cuda:0", minimum_free_mib=MIN_FREE)
            engine.load_tts_dependencies()
            total = engine.torch.cuda.get_device_properties(0).total_memory
            engine.torch.cuda.set_per_process_memory_fraction(min(1.0, ALLOCATOR_LIMIT * 1024 * 1024 / total), 0)
            engine.render_chunks(pending, batch_size=1)
        finally:
            worker.close()
    present = {item.key: pcm(item.path) for item in items if item.path.exists()}
    if len(present) == len(items):
        save(output / "voice-generation-v2.json", {"identity": config, "takes": present})
    print(f"Approved voice generated for {len(present)}/{len(items)} scenes.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--wait-minutes", type=int, default=45)
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.execute:
        render(output, args.wait_minutes, set(args.only))
    else:
        print(f"{len(pinned_plan())} episodes, {sum(len(ep['narrationKo']) for ep in pinned_plan())} scenes")
        print("Current guard:", busy(resource_guard(), MIN_FREE))


if __name__ == "__main__":
    main()
