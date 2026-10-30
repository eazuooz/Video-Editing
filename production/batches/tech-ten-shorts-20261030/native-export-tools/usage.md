# Preserve the seven native scene versions

These are exact source copies of the tested local helpers at `C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/native-export-tools`. They are not capture source inputs. Do not install or run the Unity helper until all seven full native captures have successful, current receipts and the isolated capture project is idle. Preserve the main Unity Editor and all other applications.

Run the existing local Python helper first:

```powershell
python -B -X utf8 C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/native-export-tools/export-native-editable.py prepare --job C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/native-export-tools/jobs/export-final-01.json
```

This checks receipt artifacts, final voice/timing bindings and immutable source snapshots for exactly seven native topics. It prints a separate Unity `-batchmode -nographics` command; it does not launch it. After capture work ends, copy the C# helper into the isolated `unity-capture/Assets/Editor/TechTenArchive/` directory and run that printed command under the normal resource guard. The Unity method only reads existing scenes and dependencies; it does not open, build, save or reserialize scenes. Do not add it to the active capture source or main Editor.

After the dependency manifest run succeeds:

```powershell
python -B -X utf8 C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/native-export-tools/export-native-editable.py collect --job C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/native-export-tools/jobs/export-final-01.json
```

Outputs are local to `C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/editable-native/<slug>/<receiptSHA>/`: editable `project/`, `git-text-projection/`, source/receipt evidence and `editable-export.json`. Existing differing files stop the operation. Each scene is bound to its receipt hash and capture-time `sourceTreeSha256`; scripts and shaders come from that immutable snapshot, even if the shared capture project's current code has changed. Dependency/meta/settings hashes are export-time observations, not invented capture-time evidence. Package-manager dependencies remain locked, hashed references; no Library cache is copied.

The local project preserves required FBX/textures and KayKit license/provenance. The Git projection excludes binary media/vendor assets and keeps only the explicit text allowlist, including import `.meta`. The copier never stages or commits files. Inspect the manifest before any separately scoped repository copy. Runtime reopening and human review remain unverified until actually performed.

CPU validation: the C# helper compiled against the installed Unity6000.6 reference assemblies, and the local fixture test passed seven-capture gating, exact captured-code restoration, scene/source binding, local binary preservation with Git exclusion, `.meta` retention, idempotence, path-traversal rejection and altered-artifact rejection. No Unity process was launched by those checks. Run fixture tests only from the existing local helper directory so their retained QA outputs stay outside the repository.
