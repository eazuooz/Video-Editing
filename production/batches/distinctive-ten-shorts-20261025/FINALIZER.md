# Finite local finalizer

This consumes the existing voice queue's PCM. It never creates TTS, uploads,
schedules, deletes a platform video, changes worklists, or marks human review done.
The only outputs are this finite batch's local media, immutable deliveries and
local progress records. No production execution was performed while implementing it.

Validate without writing production state or running media jobs:

```powershell
python -B -X utf8 production/batches/distinctive-ten-shorts-20261025/finish-ready-videos.py --validate-only
python -B -X utf8 production/batches/distinctive-ten-shorts-20261025/finish-ready-videos.py --self-test
```

After all assigned code corrections are complete, root obtains the exact static
code map with `--readiness-template` and saves that JSON to
`production/batches/distinctive-ten-shorts-20261025/local/finalizer-readiness.json`.
Set `projects[slug].codeReadyForActualProduction` to true only for internally ready
projects. Preserve `revision`, `internalProductionReadinessOnly` and the exact
`productionCodeSha256` maps. This is a code readiness receipt, not a user approval
or evidence of full playback/listening. Generated captions, visual timing and
mutable scene config JSON are intentionally excluded from static code maps.
Relative Motion Canvas imports, native Unity code and the dependency lockfile
are included, including shared Outer Wilds/Viewfinder and Diablo actor code.

Execution after that internal preparation:

```powershell
python -B -X utf8 production/batches/distinctive-ten-shorts-20261025/finish-ready-videos.py --execute --wait-minutes 720
```

`--slug SLUG` limits the finite pass. Default execution makes one pass without
waiting. `--wait-minutes` is bounded to 12 hours, not a recurring automation.
`--retry-failed` is available after inspecting and resolving a preserved failure;
it does not overwrite a partial pair, stale mix or differing successful artifact.
Missing PCM and external resource boundaries defer the project. An ASR mismatch
never creates a reconciliation automatically: strict caption alignment stops that
project, retains the raw recognition/logs and continues another prepared project.

The voice queue and finalizer share `batch_job_lock.SerialJobLock`. It uses an
exclusive-create lock at the owned C: batch `locks/serial-job.lock`, with PID,
process creation time and random ownership token. Only its owner releases it;
stale locks are never automatically stolen or deleted. The finalizer accepts the
registered queue interpreter and its exact queue launcher ancestors, but blocks
uncoordinated jobs. It holds the lock for one project's pipeline and rechecks user
game/Unity/resource activity before every new costly stage. In-flight jobs are
never force-killed when a game starts; the next stage is deferred.

Stages: full CPU voice ASR → strict measured captions → project-specific actual
visual preparation → serial CPU Motion Canvas rendering on existing port 9267 →
licensed music/native-audio mix and continuity report → full CPU final-mix ASR →
clean/captioned pair → exact-frame/decode/AAC integrity → generated QA images and
mobile file → four-output local delivery, exact title/description and hashes.
The native Unity route uses `run-after-voice.ps1 -CaptureOnly` and CPU/WARP, while
still respecting the user's active game/editor boundary.

Progress: `production/batches/distinctive-ten-shorts-20261025/local/finalizer-status.json`.
Per-project state/logs: `production/local/finite-finalizer-v1/`.
User-readable overview: `C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025/delivery/index.html`.
Each master-hash delivery contains clean/captioned MP4, KO/EN SRT, metadata and
an exact-file report. The HTML shows Korean progress labels and links to technical
details separately. It distinguishes `generatedForReview`, pending internal visual
and listening review, and pending actual human review. Generating QA images is not
viewing them; an ASR result is not listening; no `completed 10/10` claim is made.
Public-use/monetization conditions remain in the original source records, including
the unresolved Outer Wilds conditions; a local file does not grant publication rights.
