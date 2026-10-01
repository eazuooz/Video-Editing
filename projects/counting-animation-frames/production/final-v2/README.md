# Frame-count revision: actual fighting-game examples

User request: `게임 애니메이션 프레임 세기 영상 너무 피피티만 많아 중간에 실제 게임영상 예시 잘 삽입해줘야할거같아 내용을 보니 격투게임이 적절할거같아`.

The current 197.600-second edit interleaves fresh SF6 Ryu/Chun-Li and GGST Sol actions across chapters02–06. Commercial footage grew from17.200s to70.017s; executable test footage fell from94.167s to44.233s. White2.5D comparisons occupy71.350s. Combined actual footage is61.557% of the185.600s body, excluding the original2s intro and10s member ending. The six narration chunks, scene boundaries and50 KO/EN cue times are unchanged. All exact numbers remain original-test data, not claimed commercial move values. GGST's2020 closed-beta version is labeled on screen.

Final evidence: `qa.json`, `asr-direct-review.json`, `fighting-cut-audit.json`, `mix-refresh-evidence.json`, current all-cue sheets and `../delivery-output.json`. Both final MP4s completely decoded; current AAC hashes match; measured mix is−16.09LUFS/−1.96dBTP. Fifty cues and58 cue/cut regions were directly read after the last caption-position correction. Original member profile/name/badge rows and exact title remain together. Human listening and public rights review are still pending.

All binaries remain local. Before rebuilding, restore source files from an external backup and compare `sources/source-files.json` hashes. `preserved-v1.json` records the archived old media and existing piZTx_239R8 upload; do not replace its receipt or infer that upload contains final-v2. Do not run the old final-v1 prepare command against this revised layout.

Rebuild in this repository with the installed FFmpeg, Motion Canvas dependencies and Qwen Python runtime:

```powershell
node projects/counting-animation-frames/production/revise-fighting-examples.cjs prepare
node projects/counting-animation-frames/production/repair-source-fade-v2.cjs
node projects/counting-animation-frames/production/repair-source-transitions-v2.cjs
node projects/counting-animation-frames/production/repair-out-of-action-shot-v2.cjs
node projects/counting-animation-frames/production/audit-fighting-cuts.cjs
node projects/counting-animation-frames/production/run-revision-v2.cjs
```

The single runner records its actual PID, child PID, stage and log in `../revision-v2.json` and the batch queue. Its live-process guard prevents duplicate work. A picture-only refresh may use `--refresh-edit --retain-identical-mix-asr`; ASR reuse is permitted only when the complete rebuilt decoded PCM is byte-identical. The raw whole-mix ASR hallucinates a subtitle credit over the BGM-only ending; independent whole-body ASR and zero narration samples throughout the10s ending establish why that is a recognizer error. Preserve both raw outputs and that exception.

After every rebuild, inspect the full ASR, every cue/cut sheet and exact action before running `finalize-revision-v2.cjs --direct-review-complete`. Then collect and check:

```powershell
node scripts/collect-video-output.cjs counting-animation-frames
node scripts/build-rebuild-manifests.cjs counting-animation-frames
npm run media:check
npm run rebuild:check
```

Public release belongs to the user. Original Nimbus library bytes, truncated original member handles, human listening and external media backup stay pending. The old private upload's automated ad/copyright results cover final-v1 only.
