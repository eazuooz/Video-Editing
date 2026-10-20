# Unity asset-library code integration

These tools inspect and adapt the user-owned local asset library without embedding
vendor source in Git. Compiled tools, full source backups, candidates and evidence
remain under `unity/VideoEditing/Library/YamyamAssetLibrary/`.

Run from the repository root with the matching installed Unity editor:

```powershell
scripts/unity-asset-library-code/Invoke-CodeTool.ps1 -Project unity/VideoEditing -Mode Inventory
scripts/unity-asset-library-code/Invoke-CodeTool.ps1 -Project unity/VideoEditing -Mode Audit
scripts/unity-asset-library-code/Invoke-CodeTool.ps1 -Project unity/VideoEditing -Mode Plan
scripts/unity-asset-library-code/Invoke-CodeTool.ps1 -Project unity/VideoEditing -Mode Candidates
scripts/unity-asset-library-code/Invoke-CodeTool.ps1 -Project unity/VideoEditing -Mode VerifyGzip
```

`Build` compiles only the three authored Roslyn utilities. These commands never
start Unity or operate the desktop. `Audit` reads completed-stage and blocked-work
receipt paths; wait for extraction and GUID recovery to finish before the final
audit, candidate generation or application.

The plan scopes actual cross-product type collisions, exact ShaderGUI identities
and real duplicate-name `Shader.Find` lookups. Valid same-product partial classes
are retained. Automatic vendor setup and identified Editor UI features are opt-in;
no project-wide scripting symbols are enabled. Mixed runtime settings, optional
integrations and binary plugin importer changes require inspected per-file plan
entries rather than blanket source removal.

The source rewriter writes separate candidates and checks Editor, opt-in and
player syntax. It also supports scoped GZip stream ports, optional Cinemachine
injection and explicit conditional Editor API members. Compiler/API checks and
actual Unity validation still follow; syntax checks alone are not an import pass.
`VerifyGzip` compiles the actual local candidate beside an interface-only fixture;
it executes no vendor DLL and checks all four overload combinations, stream
ownership, empty/random/offset inputs, corruption and the preserved GZip header.

Apply only after the final reviewed plan and candidates are complete:

```powershell
python scripts/unity-asset-library-code/apply_vendor_adaptations.py --project unity/VideoEditing --plan unity/VideoEditing/Library/YamyamAssetLibrary/vendor-adaptation-plan.json
python scripts/unity-asset-library-code/apply_vendor_adaptations.py --project unity/VideoEditing --plan unity/VideoEditing/Library/YamyamAssetLibrary/vendor-adaptation-plan.json --apply
```

The first command is a dry run. Application requires every product to be complete
and all source/manifest hashes to match. It edits only the prepared stage, keeps
local originals under `adaptation-backups/`, updates exact manifest/receipt hashes
and writes `vendor-adaptation-report.json`. Download archives, the real project's
Assets, package manifests and project settings are outside this tool's write scope.
The explicit isolated copy at `Library/YamyamAssetLibrary/headless-project/Assets`
is also permitted after the canonical manifest's stage root is moved there.
Each subsequent adaptation preserves its predecessor report, immutable per-run
report/plan and metadata backups. An application exception rolls back only paths
written by that invocation.

The final code preflight must use the actual compiler as well as declarations.
`compile_vendor_stage.py` invokes the installed Roslyn compiler with the existing
Unity response-file API snapshot for each enabled assembly and Editor/player
symbols. It writes DLLs only under Library and executes no vendor code. Its package
reference snapshot is deliberately broad, so isolated Unity import remains the
authority for assembly-definition and plugin reference visibility.

For the two verified post-audit compatibility ports, refresh `Audit`, preserve the
initial plan, then generate `plan_vendor_adaptations.py --compiler-ports-only`
with `--audit` and `--out` pointing at Library JSON files. Generate `Candidates`
and apply that exact plan. This ports the optional caustics feature to the actual
URP RenderGraph raster API while preserving its legacy source and shader uniforms,
and replaces the manual core-source downloader's unencrypted ZIP extraction with
the framework API. It does not create the vendor's missing optional caustics shader.
The `--pipeline-closure-only` plan records the particles setup module's dependency
on its gated automatic setup UI; the initial plan includes this same closure.
The required Addressables dependency belongs in the isolated project first, then
the real package manifest/lockfile only after validation; do not quarantine the
runtime resource manager simply to hide a missing package.

`extract_binary_scene_scripts.py --project unity/VideoEditing` reads only the
binary scenes already listed by `scene-header-census.json`, using pinned
[UnityPy](https://github.com/K0lb3/UnityPy) installed into the task's local
`Library/YamyamAssetLibrary/tool-dependencies` folder. Install with pip `--target`
and `UnityPy==1.25.4`; the small pure-Python `tpk_ar` dependency needs its source
distribution when a wheel is unavailable. No global/user Python environment is
changed. The parser disables the C type-tree accelerator, never dereferences
external pointers, and never opens/saves scenes or decodes images/audio.

The report binds each reference list to the exact parsed scene SHA256/byte count.
It records signed64-bit local IDs as strings and leaves null/internal references
and decode failures explicit. GUIDs from the external table are canonicalized by
swapping the two hexadecimal nibbles of each source byte; byte offsets and actual
vendor/official MonoScript metadata comparisons prove this representation. Unity
must subsequently resolve GUID/localID and compiled class; successful offline
decoding alone does not establish that a referenced MonoBehaviour is installed.

`python scripts/repair-unity-binary-references.py --project unity/VideoEditing` performs a
dry run against the completed version2 binary GUID audit. It reparses exact
external-table offsets, proves the intended same-product GUID owner and its
source/meta hashes, and locates every whole-file occurrence of all collided GUID
spellings. Any occurrence outside a reviewed16-byte external field blocks repair.
The original archives and actual main Assets tree cannot be repair targets;
symlinks and Windows junction/reparse components are rejected before resolving
the local stage boundary.

After the isolated Editor has exited, `--apply --editor-stopped` additionally
requires the exact `--expected-manifest-sha256` and `--expected-audit-sha256`
values from the reviewed dry run. Each transaction preserves full source binary
and canonical metadata backups, changes only the checked16-byte fields, reparses
the candidate, updates receipt/manifest hashes and retains immutable run reports.
Any write failure rolls back that transaction. Run
`python scripts/test-repair-unity-binary-references.py` for synthetic endian,
format17/22/23, ownership, stale-input, outside-field and rollback fixtures.
Regenerate the seven-scene offline reference report after binary repair because
its scene SHA256 bindings intentionally become stale.

If Unity converted an original binary path to text during its authorized import,
the refreshed version2 audit must explicitly classify it as `converted-yaml`,
bind its `convertedTextProof` to the current SHA256, byte count and GUID-map hash,
and prove every old GUID spelling absent. The repair tool independently verifies
the Unity YAML header and scans all spellings plus case-insensitive32hex tokens;
it skips only these clean, recorded conversions. An unclassified text file,
stale proof, or surviving collided reference blocks the entire transaction.

`python scripts/quarantine-unity-source-only-terrain.py --project unity/VideoEditing`
is a dry run for exactly two known incomplete product033 TerrainData assets and
their metadata. A fresh isolated `RunDependencyProofHeadless` report must bind the
current canonical manifest/receipt, every current non-folder library input path,
and all four current asset/meta SHA256 values and GUIDs. It must prove no inbound
dependency from any other root asset. Original archive inspection must also show
the six missing texture GUIDs are unavailable, while the current TerrainData still
contains those references. No previous candidate plan authorizes a move.

Apply only after that Editor exits, with `--apply --editor-stopped` and exact
`--expected-manifest-sha256`, `--expected-runtime-proof-sha256` and
`--expected-missing-evidence-sha256` values. Four exact files move to the owned
`Library/YamyamAssetLibrary/SourceOnly` folder with full backups and explicit
`sourceOnlyFiles` provenance; canonical receipt/manifest updates share rollback
with the moves. Original archives, every other asset and historical896-path
binary-audit coverage remain unchanged. Run
`python scripts/test-quarantine-unity-source-only-terrain.py` for its synthetic
scope, proof-binding, preservation and rollback fixtures.

`python scripts/quarantine-unity-source-only-group.py prepare --project unity/VideoEditing`
prepares the separate, narrow incomplete-provider group plan under Library. It
binds the original package GUID indexes, twelve missing-reference TerrainData and
only the incoming serialized demo scene/prefab closure. A valid empty TerrainData
and usable outgoing models/materials never enter that group. The actual supplied
library produces nineteen assets: twelve TerrainData and seven demo scenes. This
preparation does not move any file or update the canonical catalog.

After `YamyamAssetLibraryProviderGroupProof.RunHeadless` exits normally, review
the current proof and run the default dry run:

```powershell
python scripts/quarantine-unity-source-only-group.py quarantine `
  --project unity/VideoEditing `
  --group-plan unity/VideoEditing/Library/YamyamAssetLibrary/incomplete-provider-demo-group-plan.json `
  --runtime-proof unity/VideoEditing/Library/YamyamAssetLibrary/headless-project/Library/YamyamAssetLibrary/provider-group-proof-report.json
```

The runtime proof must use that same plan path and current manifest/receipts,
cover every outside-group root with recursive `AssetDatabase.GetDependencies`,
bind exact asset/meta SHA256 values and GUIDs, and prove zero inbound references.
It cannot open scenes, load TerrainData, save assets or change source archives.
Apply requires `--apply --editor-stopped` plus the reviewed
`--expected-manifest-sha256`, `--expected-group-plan-sha256` and
`--expected-runtime-proof-sha256`. The transaction moves exact source bytes to
`Library/YamyamAssetLibrary/SourceOnly`, with full backups and receipt/manifest
rollback; later foreign writes are preserved if rollback encounters a conflict.
Historical binary collision/recovery fields retain all original896 paths. The
v2 audit resolves a quarantined binary only through its complete immutable
transaction, source/meta GUID, manifest snapshot and exact preserved backup.

Run `python scripts/test-quarantine-unity-source-only-group.py` for synthetic
prepare-scope, stale-proof, source-absence, native-reference, exact-move,
bookkeeping/report failure and concurrent rollback fixtures. SourceOnly lives
under a Unity cache directory; final delivery also needs a verified permanent
local copy outside Library, in addition to the unchanged original archives.
