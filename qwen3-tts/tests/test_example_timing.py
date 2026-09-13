"""No GPU/model calls: exercise example padding, KO/EN SRT and scene timing."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import soundfile as sf

BASE = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, BASE / f"{name}.py")
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


class ExampleTimingTest(unittest.TestCase):
    def exercise(self, mode, example, continuous=False):
        lead = 0 if continuous else example
        with tempfile.TemporaryDirectory(prefix="video-example-test-") as directory:
            root = Path(directory)
            out = root / "audio"
            chunks = out / "chunks"
            chunks.mkdir(parents=True)
            renderer = module("render_narration")
            renderer.np, renderer.sf = np, sf
            renderer.OUTPUT_DIR, renderer.CHUNK_DIR = out, chunks
            renderer.FINAL_WAV, renderer.FINAL_SRT = out / "test.wav", out / "test.srt"
            renderer.TIMING_JSON = out / "test.timing.json"
            renderer.RENDER_MODE, renderer.EXAMPLE_SECONDS = mode, example
            if continuous:
                renderer.NARRATION_PLACEMENT = "continuous-across-example-and-explanation"
            jobs = [renderer.Job("01", "Intro", 1, "First line."), renderer.Job("02", "Body", 1, "Second line.")]
            sr = 24000
            wave = np.sin(np.arange(sr) * 2 * np.pi * 220 / sr).astype(np.float32) * .1
            for job in jobs:
                target = chunks / f"{job.scene_id}-scene.wav" if mode == "scene" else job.path
                sf.write(target, wave, sr)
            renderer.assemble_outputs(jobs)
            timing = json.loads(renderer.TIMING_JSON.read_text())
            starts = [entry["start"] for entry in timing["entries"]]
            self.assertAlmostEqual(starts[0], lead)
            self.assertAlmostEqual(starts[1], 2 * lead + 1.72)
            audio, _ = sf.read(renderer.FINAL_WAV)
            self.assertAlmostEqual(len(audio) / sr, 2 * lead + 2.72)
            if lead:
                self.assertEqual(np.max(np.abs(audio[:int(lead * sr)])), 0)
            self.assertIn(renderer.timestamp(lead), renderer.FINAL_SRT.read_text())

            project = root / "projects" / "test"
            (project / "script").mkdir(parents=True)
            (root / "motion" / "assets").mkdir(parents=True)
            script = {"scenes": [{"id": "01", "title": "Intro", "lines": ["First line."]}, {"id": "02", "title": "Body", "lines": ["Second line."]}]}
            for lang in ["ko", "en"]:
                (project / "script" / f"narration.{lang}.json").write_text(json.dumps(script), encoding="utf-8")
            manifest = {"slug": "test", "video": {}, "editing": {"exampleSeconds": lead}, "tts": {"outputDir": "audio", "filenameStem": "test"}, "paths": {"script": "projects/test/script/narration.ko.json", "motionCanvasProject": "motion/project.ts", "captionsEn": "audio/test.en.srt"}}
            (project / "project.json").write_text(json.dumps(manifest), encoding="utf-8")
            manifest["editing"].update(exampleSeconds=example, narrationPlacement=renderer.NARRATION_PLACEMENT)
            (project / "project.json").write_text(json.dumps(manifest), encoding="utf-8")
            sync = module("build_project_timing")
            sync.ROOT = root
            with patch.object(sys, "argv", ["test", "--project", "test"]):
                sync.main()
            ts = (root / "motion" / "timing.ts").read_text(encoding="utf-8")
            self.assertIn("export const SCENE_STARTS = [\n  0.0,", ts)
            translate = module("build_translated_srt")
            translate.ROOT = root
            with patch.object(sys, "argv", ["test", "--project", "test", "--language", "en"]):
                translate.main()
            ko_times = [x for x in renderer.FINAL_SRT.read_text().splitlines() if " --> " in x]
            en_times = [x for x in (out / "test.en.srt").read_text().splitlines() if " --> " in x]
            self.assertEqual(ko_times, en_times)
            correct_placement = manifest["editing"]["narrationPlacement"]
            manifest["editing"]["narrationPlacement"] = "after-example-meme-overlays-explanation" if continuous else "continuous-across-example-and-explanation"
            (project / "project.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(sys, "argv", ["test", "--project", "test"]), self.assertRaisesRegex(ValueError, "placement changed"):
                sync.main()
            manifest["editing"]["narrationPlacement"] = correct_placement
            manifest["editing"]["exampleSeconds"] = example + 1
            (project / "project.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(sys, "argv", ["test", "--project", "test"]), self.assertRaisesRegex(ValueError, "older example length"):
                sync.main()

    def test_scene_with_examples(self): self.exercise("scene", 19.5)
    def test_line_with_examples(self): self.exercise("line", 19.5)
    def test_legacy_no_examples(self): self.exercise("scene", 0)
    def test_continuous_scene(self): self.exercise("scene", 19.5, True)
    def test_continuous_line(self): self.exercise("line", 19.5, True)


if __name__ == "__main__":
    unittest.main()
