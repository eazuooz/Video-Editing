# Video production defaults

- Per-video Git delivery approved 2026-10-01: after each video's render, QA and local output collection finish, commit and push its approved production work and reusable instructions. Run media/rebuild checks first; never commit video, narration, game sound, BGM or media archives. Preserve user changes, keep incomplete human/rights review status accurate, and record commit/push evidence in the batch queue. Latest user request: `하나끝나면 커밋 푸시도 해줘~`.

- Fresh game examples approved 2026-10-01: for every new video, review game candidates and the repository's recent used-game/source history before selecting footage. Prefer new titles and fresh source segments that illustrate the actual chapter; do not automatically recycle the same games or clips. Record chosen and rejected candidates, concept fit, rights, and prior-use checks in each project's sources. Latest user request: `게임영상도 조금 새롭게 해줘 항상 썼던것만 쓰는데 매 영상마다 게임 새로검토하고 사용해줘`.

- Upload hold approved 2026-10-01: the latest user request is video production only, until the user reviews the videos and explicitly resumes uploading. Automated work may render, verify and collect local deliverables, but must not create even private YouTube uploads, public schedules, or apply Studio metadata/cards/end screens/ads settings. The existing one-button upload is private with its public schedule cancelled. Read the current authorization in `docs/YOUTUBE_PUBLISHING.md` and `shared/publishing/youtube-defaults.json` before any platform action.

- YouTube publishing defaults approved 2026-10-01: read `docs/YOUTUBE_PUBLISHING.md` and `shared/publishing/youtube-defaults.json` before uploading. Preserve the supplied yellow-strip/white/large-black-text/game-cat thumbnail concept; place fresh video description above the existing channel footer while retaining coaching/community/membership links. Omit public description credits per user request but preserve internal source/rights records. Manually upload both output KO/EN SRTs; add English as a language and publish its separate title and description. Add one programming-coaching link card at 00:00 (user accepted beginning-only); add a relevant channel playlist and this channel's subscribe button only in the 10-second membership outro, without obscuring member identities. Enable ads and observe automatic ad suitability checks; record actual results, not assumed approval. User selected three uploads per week Tuesday/Thursday/Sunday 20:00 Asia/Seoul, 2–3 days apart; schedule only completed videos when publication is requested. Record platform limits and verify actual Studio settings. Keep review uploads private until scheduling/publication is authorized; do not silently alter published older videos.

- Screen composition approved 2026-09-30: channel cat-logo intro → full-screen gameplay with captions over the footage → original white 2.5D explanation scenes → one 10-second membership thank-you scene with the original profile/name/badge image and channel logo. Read `docs/VIDEO_SCREEN_LAYOUT.md` and preserve its user reference images. Gameplay must not be inset in a white PPT frame; all explanatory presentation scenes must use 2.5D depth, motion and meaningful comparisons. Keep broad design examples varied; this one-button revision requires two additional game titles beyond Kirby. Reuse the existing cat intro assets, or rebuild the card from the original logo when its render is missing.

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
- New-video screen-time default (2026-09-29): actual gameplay/development footage 60% / original explanation 40% of the body, excluding channel intro and membership outro. Allow up to 62% / 38% for natural pacing; do not force each scene to the same ratio. Favor 2.5D comparisons, arrows and animated emphasis over static text slides. Record targets and measured totals in `project.json.editing` and `rebuild.json`. Preserve completed videos.
- The old 19.5-second external-example slot is a planning baseline only; the body-wide 60:40 target takes precedence for new projects. Read `project.json.editing` and the actual per-scene timeline; never hard-code old values into scenes/audio/subtitles.
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
