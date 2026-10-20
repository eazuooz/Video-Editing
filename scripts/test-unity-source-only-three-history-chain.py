"""Replay all three real temporary preservation transactions; no Unity/assets."""
import copy, importlib.util, json, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("three_install",Path(__file__).with_name("install-unity-asset-library.py"));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ThreeHistoryFixture(unittest.TestCase):
    def test_three_actual_transactions_and_immutable_replay(self):
        def load(name, filename):
            spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
            value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
        initial_module = load("install_initial_chain_fixture", "test-quarantine-unity-source-only-terrain.py")
        group_module = load("install_group_chain_fixture", "test-quarantine-unity-source-only-group.py")
        initial = initial_module.SourceOnlyFixtures(); initial.setUp()
        group = group_module.GroupFixtures(); group.setUp()
        try:
            # Both actual temporary transactions share one84-product project.
            # Match033's real canonical folder while keeping the group fixture's
            # separate usable assets and original package index evidence.
            folder = initial_module.tool.FOLDER
            def rewrite(value):
                if isinstance(value, str): return value.replace("033-fixture", folder)
                if isinstance(value, dict): return {key: rewrite(item) for key, item in value.items()}
                if isinstance(value, list): return [rewrite(item) for item in value]
                return value
            (group.stage / "033-fixture").rename(group.stage / folder)
            group.products["033"] = rewrite(group.products["033"])
            group.targets, group.terrains, group.evidence, group.graph = (rewrite(value) for value in (group.targets, group.terrains, group.evidence, group.graph))
            group.paths = {rewrite(path) for path in group.paths}
            group.empty, group.prefab, group.scene = (rewrite(path) for path in (group.empty, group.prefab, group.scene))
            template_rows = copy.deepcopy(initial.product["files"])
            template_bytes = {row["path"]: (initial.stage / row["path"]).read_bytes() for row in template_rows}
            initial.project, initial.work, initial.headless, initial.stage = group.project, group.work, group.headless, group.stage
            initial.product = group.products["033"]; initial.products = list(group.products.values())
            initial.archive = Path(initial.product["inputs"][0]["path"])
            initial.main = group.main
            initial.manifest = dict(group.manifest, products=initial.products)
            initial.manifest_path = group.manifest_path
            initial.runtime_path = group.headless / "Library/YamyamAssetLibrary/initial-proof/report.json"
            initial.runtime_path.parent.mkdir(parents=True)
            initial.missing_path = group.work / "initial-missing-evidence.json"
            initial.missing.update(package=str(initial.archive), packageBytes=initial.archive.stat().st_size)
            for row in template_rows:
                raw = template_bytes[row["path"]]
                initial.add(row["path"], raw, row.get("guid"))
            initial.finish(); initial_report, _ = initial.run_tool(True)
            group.manifest = json.loads(group.manifest_path.read_bytes())
            group.products = {product["id"]: product for product in group.manifest["products"]}
            group.finish(); group_report, group_report_path = group.run_tool(True)
            manifest, _ = m.read_json(group.manifest_path)
            validation = {"completedUtc": m.utc()}
            optional_module = load("three_optional_fixture", "test-quarantine-unity-optional-demos.py")
            optional = optional_module.OptionalFixtures(); optional.setUp()
            try:
                template = optional
                payloads = [(p["id"], copy.deepcopy(r), (optional.stage / r["path"]).read_bytes()) for p in optional.products.values() for r in p["files"] if r["path"].removesuffix(".meta") in optional.paths]
                snapshot = json.loads((optional.work / "missing-script-validation-snapshot.json").read_bytes())
                graph = json.loads((optional.work / "optional-demo-incoming-consumers.json").read_bytes())
                probe = json.loads((optional.work / "optional-demo-script-resolution-probe.json").read_bytes())
                optional.project, optional.work, optional.headless, optional.stage = group.project, group.work, group.headless, group.stage
                optional.products = {p["id"]: p for p in manifest["products"]}; optional.manifest = manifest
                optional.manifest_path = group.manifest_path; optional.paths = {rewrite(p) for p in optional.paths}
                for pid, row, raw in payloads: optional.add(pid, rewrite(row["path"]), raw, row.get("guid"))
                optional.write(optional.work / "missing-script-validation-snapshot.json", rewrite(snapshot))
                optional.write(optional.work / "binary-scene-script-references.json", {"scenes": []})
                optional.write(optional.work / "optional-demo-script-resolution-probe.json", probe)
                graph = rewrite(graph); graph["diagnosisSha256"] = m.sha((optional.work / "missing-script-validation-snapshot.json").read_bytes())
                optional.write(optional.work / "optional-demo-incoming-consumers.json", graph); optional.flush()
                optional.plan, _ = optional_module.m.prepare(optional.project); optional.plan_path = optional.work / "incomplete-optional-demo-script-group-plan.json"
                optional.runtime_path = optional.headless / "Library/YamyamAssetLibrary/optional-demo-group-proof-report.json"
                optional.runtime = group_module.GroupFixtures.runtime_for(optional, optional.plan); optional.runtime["kind"] = optional_module.m.KIND
                optional.runtime["scriptResolutionEvidenceSha256"] = m.sha((optional.work / "optional-demo-script-resolution-probe.json").read_bytes())
                optional.runtime["scriptResolutions"] = [dict(c, actualResolved=c["expectedResolved"], resolvedClass=c["expectedClass"], matches=True) for c in probe["cases"]]
                optional.write(optional.runtime_path, optional.runtime)
                report, _ = optional.run_tool(True); current = json.loads(optional.manifest_path.read_bytes())
                accepted = m.validate_source_only(optional.project, optional.stage, current, {"completedUtc": "2099-01-01T00:00:00Z"})
                self.assertEqual(130, accepted["files"]); self.assertEqual(3, len(accepted["runs"])); self.assertEqual(130, len(accepted["verifiedFiles"]))
                self.assertEqual(98, len(report["files"]))
                changed = copy.deepcopy(current); changed["sourceOnlyHistory"][1], changed["sourceOnlyHistory"][2] = changed["sourceOnlyHistory"][2], changed["sourceOnlyHistory"][1]
                with self.assertRaisesRegex(ValueError, "exact immutable"): m.validate_source_only(optional.project, optional.stage, changed, {"completedUtc": "2099-01-01T00:00:00Z"})
            finally: optional.tearDown()
        finally: initial.tearDown(); group.tearDown()

if __name__=="__main__":unittest.main()
