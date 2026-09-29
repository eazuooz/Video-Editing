# Video production defaults

- Git media policy (2026-09-29): never commit video, narration, sound, BGM, or compressed/split media archives. Preserve local files; external storage is required. Keep project-level `rebuild.json` updated with `node scripts/build-rebuild-manifests.cjs <slug>` and run `npm run media:check` / `npm run rebuild:check` before committing. See `docs/MEDIA_STORAGE.md`; do not reintroduce media through old branches or force-add.

- Delivery default: after every completed render or subtitle revision, collect the current clean MP4, Korean-captioned MP4, KO SRT and EN SRT into repository-root `output/<slug>/` using `node scripts/collect-video-output.cjs <slug>`. Keep intermediates and old versions out of output; preserve source files. Deliver `output/index.html` as the browse entry point. Preserve pending-review/rights/outro warnings; collecting files does not mean publish approval. See `docs/VIDEO_WORKFLOW.md`.

- Membership outro identity display: preserve the user-supplied profile image, displayed name/handle, and membership badge together. Text-only cards were rejected. Use the original screenshot/row assets, never generated substitutes; request the source image file if unavailable.

- Every new final video ends with one 10-second membership thank-you scene. Follow `docs/MEMBERSHIP_OUTRO.md`; use the shared editable member list and the exact requested title `멤버쉽가입 감사드립니다.`. Do not guess truncated handles or silently update published older videos. Extend the final mix to cover the outro; preserve body subtitle timing.

Before editing or creating a video, read `docs/VIDEO_WORKFLOW.md`,
`docs/VIDEO_VISUAL_STYLE.md`, `docs/NARRATION_AUDIO_STANDARD.md`, and its project manifest.

- Default visual style: white research presentation, matching the user's RenderFormer PDF.
  Use shared `motion-canvas/src/styles/research-paper.ts`; no dark neon dashboard styling.
- Default narration captions for new videos: `boxed-white-forest-v1` in `docs/CAPTION_STYLE.md` (approved 2026-09-19): opaque white square-corner box, black text/thin border, hard forest-green offset shadow. Preserve editable text, a clean master and separate KO/EN SRT alongside the Korean captioned render. Check every cue for wrapping and gameplay/UI overlap; do not restyle finished older videos automatically.
- One independent Motion Canvas scene per script scene, with an actual example followed by an original explanation.
- This is a game-development channel: use real code/editor/debugger/profiler/playtest footage for illustrative B-roll, including licensed foreign dev tutorials. Avoid generic office/phone/money stock unless specifically requested. Match the visible action to the chapter, prefer distinct sources, and distinguish illustrative footage from evidence of AI pricing or real workplace claims.
- Default external-example slot: 19.5 seconds, about 3x the old 6.5-second default.
  Read `project.json.editing`; do not hard-code old values into new scenes/audio/subtitles.
- Short originals need related additional cuts, not loops or artificial slow-down.
- Update the mix, scene starts and BOTH Korean/English SRT together after retiming.
- BGM stays continuous under source sound. Honor separate script, voice and music approvals.
- Meme references are not licenses. Record source and rights; use original reinterpretations where needed.
- Never call a silent visual draft a completed narrated video, and do not regenerate published older projects unless requested.

# Video-based wiki documents

- Put the corresponding published YouTube video embed at the very top of every video-based wiki article.
- Write the article so readers can understand it without watching the video: use approachable narrative prose, actual video screenshots, and captions explaining the action and concept.
- Verify the channel's published video URL; do not substitute a reference/B-roll source link.
- Preserve page locations and titles the user changes during editing. The AI-era developer-learning article belongs under `게임 업계 이야기, 프로그래밍 이야기`.
