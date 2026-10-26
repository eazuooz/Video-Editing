# Serial finishing entry points

This finishing source was prepared without running it. The parent's original
audio-v1 PCM and both ASR reports are preserved. Current audio-v2 preparation
regenerates only paragraphs1/2/5 and copies unchanged3/4/6 byte-for-byte after
hash/text/paragraph-ASR checks. No audio-v2 PCM is produced by `--check`.
Parent owns finite-batch selection, resource checks
and every launch. The helper guards reject another selected project, active
game/Editor or foreign costly-job lease. All new media stays under this
project's checked C: `production/local` junction.

1. Run `render-voice.py --check` for read-only readiness. The parent's later
   normal invocation generates only the three selected paragraphs using the
   approved voice and assembles `local/audio-v2/voice/narration.wav`. Run current
   complete ASR/caption timing for that new hash; preserve every audio-v1 file.
   Spoken title is `스플래툰 투`, while the display remains `스플래툰 2`.
   `쉐이딩`/`셰이딩` is normalized as alternate spelling of the same loanword.
   Both actual v2 raw ASRs wrote the title as `스플래툰 2`; the exact p1-3 phrase
   `그런데 스플래툰 2 개발 중에는` may therefore map to its already approved
   spoken form `그런데 스플래툰 투 개발 중에는`. This unique contextual spelling
   correspondence preserves every raw token, character count and timestamp.
   It does not allow `두`→`투` or any other word repair. Actual listening stays pending.
   `time-captions.py` defaults to the complete raw ASR. To use a separate raw
   recognition of every PCM paragraph, explicitly pass
   `--asr-path asr-voice-paragraphs-CURRENT_HASH_PREFIX.json --asr-reason "Concrete recognition discrepancy"`.
   The prefix is the first12characters of the new PCM's actual SHA256. This
   requires the original full report, both current PCM hashes, unprompted raw
   recognition flags and the exact `voice/narration.timing.json` hash. All six
   paragraphs, original words and ASR-only padding offsets must verify; it does
   not combine preferred words from different reports. The selection and both
   raw-report hashes are recorded in captions and alignment outputs.
   Current spoken text contains no Arabic numerals or decimals. No generic
   numeral/decimal substitution is enabled: standalone `2`, `두`, and `투`
   remain distinct. Only the complete p1-3 title phrase above has an explicit
   contextual correspondence; the display spelling is separately retained.
   Any reconciliation file must bind this exact selected raw report and can
   contain only the recorded `쉐이딩`→`셰이딩` orthographic mapping.
   For the current `81585b4dd719` PCM, use the original full report (the default):
   it covers every word after the one title spelling correspondence. The
   separate paragraph report says `저기` for `적이` and remains a mismatch.
2. `prepare-actual-visuals.py --check` is read-only; `prepare` requires actual
   PCM/29clauses and extracts two native cuts, writes the6-section timing and
   `local/unity-full-job-v1.json`. It does not launch Unity.
3. Parent launches the capture entry point
   `YamyamCoding.Shorts.SplatoonInkReadability.Editor.InkReadabilityCapture.Run`
   using `-inkReadabilityJob` and that JSON, without `-quit`. Exact project is
   `C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/unity-capture`.
   Sequence output is the own C: `local/unity-full-v1`,1920×1080/60. A still-only
   preview job is separately supplied. Never replace prior runs; version the
   job/output if parameters change. Editor delayed initialization preserves
   prior scenes; conditional active-scene changes avoid already-active errors.
4. Review actual native playback, Unity pixels and target motion/occlusion.
   Nine observed source focus keys are already recorded in `visual-config.json`
   and become exact timeline keys during preparation. Their sparse-sample
   interpolation still needs moving review; adjust only from actual pixels.
   Then run `capture-ready --native-reviewed --anchors-reviewed`.
   These flags record internal viewing only, never human final approval.
5. `prepare-header.py` creates the fixed1080×440 headline. `finish-audio.py mix`
   uses the approved Pixel Peeker Polka bed and unchanged natural-speed narration
   with actual paragraph-level evidence. Native source soundtrack is explicitly
   excluded; no replacement game effects are invented. `report` checks aligned
   levels, joins, AAC true peak and preserves listening flags.
6. Start `motion-canvas/vite.ink-readability.config.ts` on port9278 only at the
   scheduled render stage. `node production/render-visual.cjs UNIQUE-NAME`
   renders the complete current frame range; optional first/count creates a
   clearly partial review render. Own scope endpoint and five current hashes
   are checked. No existing output or receipt is overwritten.
7. `finish-video.py pair ABSOLUTE-VISUAL.mp4` requires the exact successful full
   render receipt, current hashes, real FHD source, matching voice/captions and
   header. It writes clean/captioned MP4 and KO/EN SRT into
   `production/local/final-reviewed` (or the explicit manifest final directory).
   `integrity` fully decodes both, checks regular60fps and identical AAC;
   `qa` extracts sequential cue/join images and a mobile review video.
8. Inspect/listen to actual full outputs and record remaining technical review,
   deliver local links and masterSHA256 for human review. Nothing here uploads,
   starts the next video or substitutes technical checks for human viewing.

Actual labels read captured shader values, not guessed game measurements.
Shade removal and specular rise follow their spoken cues. The specular rise
finishes before the later diving action changes phase. Thus each A/B change
keeps the same geometry/light/camera/phase; the later action is separately
narrated. Final comparison clarity depends on real shader/pixel review.
