"""Read-only compiler/API preflight; never launches Unity or executes vendor code.

This uses the current project's existing Unity compiler response file as a
reference/API snapshot. Unity's subsequent isolated import remains authoritative
for asmdef/plugin import resolution and player build assembly visibility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def version_matches(actual, expression):
    """The inspected asmdefs use minimum releases; also support closed/open ranges."""
    def numeric(value):
        found = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", value.strip())
        return tuple(int(part or 0) for part in found.groups()) if found else None
    installed = numeric(actual)
    if installed is None:
        return False
    expression = expression.strip()
    if expression[:1] in "[(" and expression[-1:] in ")]":
        bounds = expression[1:-1].split(",")
        if len(bounds) == 1:
            return installed == numeric(bounds[0])
        lower, upper = (numeric(bound) if bound.strip() else None for bound in bounds)
        return (lower is None or installed >= lower if expression.startswith("[") else lower is None or installed > lower) and (
            upper is None or installed <= upper if expression.endswith("]") else upper is None or installed < upper)
    minimum = numeric(expression)
    return minimum is not None and installed >= minimum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--baseline-rsp", required=True, type=Path)
    parser.add_argument("--dotnet", required=True, type=Path)
    parser.add_argument("--csc", required=True, type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    work = project / "Library/YamyamAssetLibrary"
    audit = json.loads((work / "vendor-roslyn-preflight.json").read_text(encoding="utf-8-sig"))
    manifest = work / "staging-manifest.json"
    if audit["manifestSha256"] != hashlib.sha256(manifest.read_bytes()).hexdigest():
        raise ValueError("Refresh the audit after final adaptations before compiler preflight")
    output = work / "offline-vendor-compile"
    output.mkdir(exist_ok=True)
    baseline = args.baseline_rsp.read_text(encoding="utf-8-sig").splitlines()
    references = []
    defines = set()
    for line in baseline:
        if line.startswith(("-r:", "/reference:")):
            value = line.split(":", 1)[1].strip('"')
            path = Path(value) if Path(value).is_absolute() else project / value
            if path.exists():
                references.append(path)
        if line.startswith(("-define:", "/define:")):
            defines.update(re.split(r"[;,]", line.split(":", 1)[1]))
    for dll in audit["dlls"]:
        if dll["assembly"] == "GameFramework":
            references.append(Path(dll["absolutePath"]))
    # A baseline runtime assembly may omit auto-referenced Editor package DLLs.
    # Add the already compiled package API snapshot, never any source assembly.
    for path in (project / "Library/ScriptAssemblies").glob("*.dll"):
        if not path.name.startswith(("Assembly-CSharp", "Yamyam")):
            references.append(path)
    references = list(dict.fromkeys(path.resolve() for path in references))
    groups = {entry["definition"]["name"]: {"sources": [], "definition": entry["definition"]} for entry in audit["assemblies"]}
    groups.update({"YamyamVendor.Runtime": {"sources": [], "definition": {}},
                   "YamyamVendor.Editor": {"sources": [], "definition": {"includePlatforms": ["Editor"]}}})
    package_versions = json.loads((project / "Packages/packages-lock.json").read_text(encoding="utf-8-sig"))["dependencies"]
    for script in audit["scripts"]:
        group = script["assembly"] if script.get("asmdefPath") else "YamyamVendor.Editor" if script["inEditorDirectory"] else "YamyamVendor.Runtime"
        if group not in groups:
            raise ValueError("Unknown source assembly " + group)
        groups[group]["sources"].append(script["absolutePath"])
    def active(definition, symbols, editor):
        if definition.get("includePlatforms") and ("Editor" not in definition["includePlatforms"] if editor else "Editor" in definition["includePlatforms"]):
            return False
        for constraint in definition.get("defineConstraints", []):
            if not any((token.strip()[1:] not in symbols if token.strip().startswith("!") else token.strip() in symbols) for token in constraint.split("||")):
                return False
        return True
    reports = []
    for mode in ("Editor", "Player"):
        symbols = defines if mode == "Editor" else {symbol for symbol in defines if not symbol.startswith("UNITY_EDITOR")}
        remaining = {}
        for name, original in groups.items():
            group = dict(original)
            group["symbols"] = set(symbols)
            for definition in group["definition"].get("versionDefines", []):
                version = package_versions.get(definition["name"], {}).get("version", "")
                if version_matches(version, definition["expression"]):
                    group["symbols"].add(definition["define"])
            if active(group["definition"], group["symbols"], mode == "Editor") and group["sources"]:
                remaining[name] = group
        completed = {}
        while remaining:
            runnable = [(name, group) for name, group in remaining.items()
                        if all(reference not in remaining for reference in group["definition"].get("references", []))]
            # Predefined assemblies can reference all enabled auto-referenced asmdefs.
            runnable = [(name, group) for name, group in runnable if not name.startswith("YamyamVendor.") or
                        not any(not key.startswith("YamyamVendor.") for key in remaining)] or runnable
            if not runnable:
                raise ValueError("Vendor assembly dependency cycle: " + ", ".join(remaining))
            for name, group in runnable:
                if name == "YamyamVendor.Editor" and "YamyamVendor.Runtime" in remaining:
                    continue
                target = output / mode / (name + ".dll")
                target.parent.mkdir(exist_ok=True)
                current_refs = references + list(completed.values())
                lines = ["/nostdlib+", "/target:library", "/langversion:9.0", "/unsafe+", "/nologo", "/warn:0", '/out:"' + str(target) + '"']
                lines += ["/define:" + symbol for symbol in sorted(group["symbols"])]
                lines += ['/reference:"' + str(path) + '"' for path in current_refs]
                lines += ['"' + source + '"' for source in group["sources"]]
                response = target.with_suffix(".rsp")
                response.write_text("\n".join(lines), encoding="utf-8")
                result = subprocess.run([str(args.dotnet), str(args.csc), "/noconfig", "@" + str(response)], cwd=project, capture_output=True, text=True, encoding="utf-8", errors="replace")
                log = target.with_suffix(".log")
                log.write_text(result.stdout + result.stderr, encoding="utf-8")
                reports.append({"mode": mode, "assembly": name, "sources": len(group["sources"]), "exitCode": result.returncode, "log": str(log)})
                print(json.dumps(reports[-1]), flush=True)
                if result.returncode == 0:
                    completed[name] = target
                del remaining[name]
    report = {"schemaVersion": 1, "manifestSha256": audit["manifestSha256"], "executedVendorCode": False, "unityLaunched": False,
              "baselineRsp": str(args.baseline_rsp), "results": reports, "allPassed": all(result["exitCode"] == 0 for result in reports),
              "limitation": "Existing package reference snapshot is intentionally broad. Isolated Unity import remains authoritative for asmdef/plugin visibility."}
    (work / "offline-vendor-compile.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
