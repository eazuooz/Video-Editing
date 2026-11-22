"""Recapture the selected weapon-grip and gate-reveal corrections."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path

import psutil

import produce_observed_v10 as v10

FRAMES = {"14-1": (176, 245, 286), "14-3": (220, 337, 369),
          "17-1": (124, 338, 532), "17-3": (285, 420, 622)}
EPISODES = tuple(dict.fromkeys(key[:2] for key in FRAMES))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("pilot", "capture"))
    parser.add_argument("base_work", type=Path)
    args = parser.parse_args()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

    base = args.base_work.resolve()
    assert base.parent == v10.WORK.resolve()
    prior = v10.read(base / "capture-receipt.json")
    assert len(prior["cuts"]) == 52 and base.name == prior["fingerprint"][:12]
    assert all(v10.read(v10.OUT / n / "decode-check.json")["fingerprint"] == prior["fingerprint"] for n in EPISODES)
    rows, observations, _, source, _ = v10.production_inputs()
    rows = {key: rows[key] for key in FRAMES}
    fingerprint = sha256((source + v10.sha(Path(__file__))).encode()).hexdigest()
    work = base / "continuity-pickup" / fingerprint[:12]
    pilot = work / "pilot"
    final = work / "captures"
    v10.capture.pipeline.CAPTURES = final
    guard = v10.capture.gpu_guard()
    worker = guard.SingleWorker(path=v10.WORKER)
    worker.acquire()
    try:
        v10.wait_for_editor(180)
        selected = {key: row | {"pilotFrames": FRAMES[key]} for key, row in rows.items()}
        v10.capture.software_job(worker, work, fingerprint, selected, pilot, True, False,
                                 observed_v10=True, observed_pickup=True)
        v10.make_contact_sheets(pilot, tuple(rows), fingerprint)
        if args.stage == "pilot":
            print(f"Continuity test frames ready: {pilot}", flush=True)
            return
        v10.wait_for_editor(180)
        v10.capture.software_job(worker, work, fingerprint, rows, final, False, False,
                                 observed_v10=True, observed_pickup=True)
        captures = {key: v10.capture.pipeline.validate_capture(row, fingerprint) for key, row in rows.items()}
        assert all(entry["softwareAdapter"] and Path(entry["scenePath"]).parent.name == "ScenesV10Pickups"
                   for entry in captures.values())
    finally:
        worker.close()

    v10.render.OUT = v10.OUT / "pickups"
    v10.render.VERSION = v10.VERSION
    contract = v10.read(v10.render.film.FORMAT)
    paragraphs = v10.read(v10.render.film.CAPTIONS)["paragraphs"]
    index = base / "pickups.json"
    pickups = v10.read(index) if index.is_file() else {}
    for number in EPISODES:
        row = observations[number]
        v10.render.GUIDES.update({f"{number}-{shot}": steps for shot, steps in row["guides"].items()})
        windows = {cut["index"]: (cut["replacement"]["start"], cut["replacement"]["observation"])
                   for cut in row["cuts"] if "replacement" in cut}
        output = v10.render.render_episode(number, rows, captures, contract, paragraphs, work / "composition",
                                               gameplay_windows=windows)
        v10.verify_new(number, output, fingerprint)
        pickups[number] = {"folder": output.relative_to(v10.OUT).as_posix(), "fingerprint": fingerprint,
                           "sceneCount": 2, "originalVerificationSha256": v10.sha(v10.OUT / number / "verification.json")}
    v10.save(index, pickups)


if __name__ == "__main__":
    main()
