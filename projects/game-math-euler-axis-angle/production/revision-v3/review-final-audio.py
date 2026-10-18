"""Complete encoded-mix ASR with bounded overlapping chunks in a crash-isolated worker.

Only the parent owns/removes its lease. A Windows native worker fault cannot
bypass that parent's finally. Existing authenticated encoded WAV is never changed.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse, difflib, hashlib, json, os, subprocess, sys, time, uuid
import psutil

R = Path(__file__).resolve().parents[4]
P = R / "projects/game-math-euler-axis-angle"
O = P / "production/local/revision-v3"
LEASE = R / "shared/output/GPU_HANDOFF.json"
EXECUTION = O / "final-asr-execution.json"
ASR_OPTIONS = {"chunk_length_s": 25, "stride_length_s": 3, "batch_size": 1}
sys.path.insert(0, str(R / "qwen3-tts"))
from review_project_narration import normalize


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    temporary = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def selected():
    assert read(R / "shared/publishing/video-production-control.json")["selectedVideo"] == P.name


def authenticated_input():
    selected()
    build = read(O / "audio-build.json")
    assert build.get("voiceGainMode") == "constant scene gain plus constant global gain"
    assert build.get("voiceDucked") is False and build.get("sourceAudioUsed") is True and build["music"]["addedBgm"] is False
    timeline_sha = sha_file(P / "production/revision-v3/timeline.json")
    assert build["timelineSha256"] == timeline_sha, "Stale mixed audio timeline"
    video_sha = sha_file(O / "euler-captioned.mp4")
    pair = read(O / "pair-source.json")
    assert pair["outputs"]["captioned"]["sha256"] == video_sha
    assert pair["inputs"]["timelineSha256"] == timeline_sha
    extraction = read(O / "encoded-audio-source.json")
    assert extraction["inputs"] == dict(videoSha256=video_sha, rate=16000, channels=1, format="pcm_s16le")
    audio_sha = sha_file(O / "encoded-audio.wav")
    assert extraction["audioSha256"] == audio_sha, "Existing encoded WAV changed; inspect rather than automatically re-extract"
    return dict(audioSha256=audio_sha, videoSha256=video_sha, timelineSha256=timeline_sha)


def successful_cache(inputs):
    f = O / "final-mix-asr.json"
    if not f.exists():
        return False
    d = read(f)
    return (d.get("audioSha256") == inputs["audioSha256"] and bool(d.get("text", "").strip())
            and isinstance(d.get("words"), list) and bool(d["words"]) and d.get("complete", True) is True)


def comparison(inputs):
    cache = O / "final-mix-asr.json"
    script = P / "script/revision-v3/narration.ko.json"
    signature = dict(inputs, asrSha256=sha_file(cache), koScriptSha256=sha_file(script))
    target = O / "final-mix-text-comparison.json"
    if target.exists() and read(target).get("inputs") == signature:
        return
    expected = " ".join(line for s in read(script)["scenes"] for line in s["lines"])
    actual = read(cache)["text"]
    a, b = normalize(expected), normalize(actual)
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    diff = [{"kind": op, "expected": a[i:j], "recognized": b[k:l]}
            for op, i, j, k, l in matcher.get_opcodes() if op != "equal"]
    save(target, dict(inputs=signature, similarity=matcher.ratio(), expected=expected,
                      recognized=actual, differences=diff,
                      reviewStatus="pending direct reading of complete recognized text"))
    print("Final encoded mix ASR complete; similarity", matcher.ratio(), flush=True)


@contextmanager
def parent_lease(device):
    selected()
    assert not LEASE.exists(), "Preserve another GPU lease"
    if device != "cpu":
        free = int(subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            text=True).splitlines()[0])
        assert free >= 8000, free
    token = str(uuid.uuid4())
    me = psutil.Process()
    owned = dict(token=token, project=P.name, state="tts_running",
                 purpose="one complete final encoded mix ASR; isolated chunked worker", device=device,
                 coordinator=dict(pid=me.pid, createTime=me.create_time()),
                 startedAt=time.time(), foreignProcessesPaused=[])
    with LEASE.open("x", encoding="utf-8") as f:
        json.dump(owned, f)
    try:
        yield token
    finally:
        if LEASE.exists() and read(LEASE).get("token") == token:
            LEASE.unlink()


def validate_worker_lease(token, device):
    selected()
    owned = read(LEASE)
    assert owned.get("token") == token and owned.get("project") == P.name
    assert owned.get("device") == device and owned.get("state") == "tts_running"
    coordinator = owned["coordinator"]
    p = psutil.Process(coordinator["pid"])
    assert p.is_running() and abs(p.create_time() - coordinator["createTime"]) < .01
    immediate = psutil.Process(os.getppid())
    if immediate.pid != p.pid:
        # Windows venv python.exe may be a redirector that launches the real
        # interpreter. Permit that one exact bridge, never an arbitrary ancestor.
        assert os.name == "nt" and immediate.ppid() == p.pid, "Worker is outside its lease owner's process family"
        assert Path(immediate.exe()).resolve() == Path(sys.executable).resolve(), "Unexpected intermediary executable"
        assert immediate.is_running() and immediate.create_time() >= p.create_time()


def model_worker(args):
    # A worker validates the live parent; it never acquires/removes any lease.
    validate_worker_lease(args.lease_token, args.device)
    print("Validated model worker", os.getpid(), "parent", os.getppid(), "device", args.device, flush=True)
    inputs = authenticated_input()
    if successful_cache(inputs):
        comparison(inputs)
        return 0
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(8 if args.device == "cpu" else 2)
    dtype = torch.float32 if args.device == "cpu" else torch.float16
    local = R / "qwen3-tts/models/whisper-large-v3-turbo"
    mid = str(local) if (local / "config.json").exists() else "openai/whisper-large-v3-turbo"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        mid, dtype=dtype, attn_implementation="eager", local_files_only=True).to(args.device)
    processor = AutoProcessor.from_pretrained(mid, local_files_only=True)
    asr = pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
                   feature_extractor=processor.feature_extractor, dtype=dtype, device=args.device,
                   **ASR_OPTIONS)
    validate_worker_lease(args.lease_token, args.device)
    result = asr(str(O / "encoded-audio.wav"), generate_kwargs={"language": "korean", "task": "transcribe"},
                 return_timestamps="word")
    assert result["text"].strip() and result["chunks"], "No successful complete transcription returned"
    save(O / "final-mix-asr.json", dict(
        inputs, text=result["text"], words=result["chunks"], complete=True,
        scope="complete encoded final mix, including joins and quiet native game sound; no added music; direct full-text comparison required",
        recognition=dict(ASR_OPTIONS, expectedTextPrompt=False,
                         coverage="entire authenticated encoded-audio.wav passed to the pipeline",
                         overlapReconciliation="Transformers Whisper decoder reconciles left/right strides and word timestamps"),
        humanListening="pending local user review", noOtherProcessPaused=True))
    comparison(inputs)
    return 0


def parent(args):
    inputs = authenticated_input()
    if successful_cache(inputs):
        print("Reusing current complete final-mix ASR", flush=True)
        comparison(inputs)
        return 0
    me = psutil.Process()
    family = {p.pid for p in [me, *me.parents()]}
    assert not [p.pid for p in psutil.process_iter(["name"])
                if p.pid not in family and (p.info["name"] or "").lower().startswith("python")], "Another compute process must finish"
    attempt = dict(schemaVersion=1, status="worker-pending", inputs=inputs, device=args.device,
                   recognition=ASR_OPTIONS, startedAt=time.time(),
                   parent=dict(pid=me.pid, createTime=me.create_time()), humanListening="pending")
    archive = O / ("final-asr-attempt-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8] + ".json")
    worker_stdout = archive.with_suffix(".stdout.log")
    worker_stderr = archive.with_suffix(".stderr.log")
    attempt.update(workerInterpreter=sys.executable, workerStdout=str(worker_stdout), workerStderr=str(worker_stderr))
    def receipt():
        save(EXECUTION, attempt)
        save(archive, attempt)
    try:
        with parent_lease(args.device) as token:
            command = [sys.executable, "-u", "-X", "utf8", str(Path(__file__).resolve()),
                       "--device", args.device, "--worker", "--lease-token", token]
            with worker_stdout.open("wb") as stdout, worker_stderr.open("wb") as stderr:
                worker = subprocess.Popen(command, cwd=R, stdout=stdout, stderr=stderr,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
                attempt.update(status="worker-running", workerPid=worker.pid)
                receipt()
                try:
                    code = worker.wait()
                except BaseException:
                    if worker.poll() is None:
                        worker.terminate()
                        try:
                            worker.wait(timeout=15)
                        except subprocess.TimeoutExpired:
                            worker.kill()
                            worker.wait()
                    raise
            unsigned = code & 0xFFFFFFFF
            attempt.update(status="complete" if code == 0 else "failed-native-worker" if unsigned == 0xC0000005 else "failed-worker",
                           returnCode=code, windowsUnsignedReturnCode=unsigned,
                           windowsExceptionHex=f"0x{unsigned:08X}", completedAt=time.time())
            if code == 0:
                assert successful_cache(inputs) and (O / "final-mix-text-comparison.json").exists()
            else:
                print("Final ASR worker failed:", code, "; stderr:", worker_stderr, flush=True)
                print(worker_stderr.read_text(encoding="utf-8", errors="replace")[-3000:], file=sys.stderr, flush=True)
    except BaseException as error:
        attempt.update(status="failed-parent-or-interrupted", error=repr(error), completedAt=time.time())
        raise
    finally:
        attempt["leaseReleaseHandledByParent"] = True
        receipt()
    # Successful worker wrote cache+comparison once; parent does not repeat them.
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["cpu", "cuda:0"], default="cpu")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--lease-token")
    args = parser.parse_args()
    assert not args.worker or args.lease_token, "A worker requires the parent's existing lease token"
    assert args.worker or args.lease_token is None, "Only a worker accepts a lease token"
    return model_worker(args) if args.worker else parent(args)


if __name__ == "__main__":
    sys.exit(main())
