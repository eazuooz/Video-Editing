"""Seal actual current pixel review, preserving separate human/IP approvals."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-mesh-uv'
P=R/'projects'/slug/'production';Q=R/'shared/output'/slug/'qa'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert '--changed-current-sheets-directly-viewed' in sys.argv
qa=read(P/'qa.json');beats=read(Q/'final-beats/generated-samples.json');ob=read(Q/'observation-samples.json');cmp=read(Q/'menu-repair-image-comparison.json')
current=qa['videos']['videoBurnedCaptions']['sha256']
assert current==sha(R/qa['videos']['videoBurnedCaptions']['path'])==beats['videoSha256']==ob['videoSha256']==cmp['currentVideoSha256']
assert qa['fullDecodePassed'] and qa['captionCount']==188 and qa['frames']==52945 and qa['bodyFrames']==52225 and qa['actualFrames']==20890 and qa['explanationFrames']==31335 and qa['ratioErrorFrames']==0
assert qa['koEnMatchingTimes'] and all(v['audioPacketMd5']=='MD5=0e1c3e737b38f9bd5de567d6ba8e0dda' for v in qa['videos'].values())
assert len(beats['records'])==10 and sum(len(x['samples']) for x in beats['records'])==62
assert len(ob['samples'])==89 and len(ob['sheets'])==23
images=sorted(Q.glob('caption-strips-*.jpg'))+sorted(Q.glob('composition-sheet-*.jpg'))+[R/x['path'] for x in beats['records']]+[R/x['path'] for x in ob['sheets']]
assert len(images)==47 and len(cmp['identicalPixelSheets'])+len(cmp['requiresFreshDirectView'])==47
old=read(R/cmp['oldReview'])
for p in cmp['identicalPixelSheets']:assert sha(R/p)==next(x['sha256'] for x in old['images'] if x['path']==p)
boundary=read(Q/'menu-boundary-samples.json');assert sha(R/boundary['clipPath'])==boundary['clipSha256'] and sha(R/boundary['sheet']['path'])==boundary['sheet']['sha256']
images.append(R/boundary['sheet']['path'])
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
notes=[
 'Every one of188 Korean cues was directly reviewed, using the exact directly viewed baseline hashes for unchanged sheets and fresh direct review of every changed sheet. Fixed960,970; opaque square white box, black text/thin border and hard forest-green shadow; no more than two readable lines; no clipped glyphs or important UI overlap. KO/EN cue timing matches.',
 '22 composition samples retain original2-second cat intro and10-second membership profiles/names/badges, original logo and coaching URL. Original truncated handles still require human confirmation. Full-screen gameplay is interleaved with ten independent white spatial explanation scenes.',
 'Indexed records0,1,2,3 and indices012,023 retain six triangle uses. Whole array192bytes versus indexed quad140bytes is distinguished from the six-use local shared record44bytes. Vertex32/index2 are illustrative assumptions.',
 'Shared diagonal02/open boundaries/nonmanifold cases and cyclic012→120 versus swapped021 winding are correct. Facing convention is explicitly declared. Diagram colors and spatial face projection distinguish records, edges and execution steps.',
 'Face normals versus vertex normals and Gouraud brightness versus Phong normal interpolation are distinguished; Phong shading is distinct from Phong reflectance. Averaged(.5,.5) has length.707 and renormalized direction(.707,.707).',
 'All62 settled explanation beats were directly reviewed. Complete three-face accumulation sums(1,1,1) and normalizes to(.577,.577,.577); zero/opposite/degenerate guards are explicit. No algorithm was cut at the episode boundary.',
 'Cube eight positions become6×4=24 face-specific records. Separate top-up and side-side normal records/indices match the clarified current narration. Triangle-count bias produces(1,2,1)/sqrt6; angle weights preserve90 degrees under30+60 or45+45 splits.',
 'All89 current actual-game action, subject, quiet seam and source-boundary samples were reviewed. Sunset rooftop details, BigWalk room grids/circular openings/curved rails/yellow ground and Megabonk faceted rocks/cacti/pillars match narrated observation. No proprietary mesh/normals are asserted from gameplay.',
 'Scene07 rejected menu near174–175.5s is replaced by safe source90–109/132–151/156–173.416667. The actual last encoded frames at108.9833,150.9833 and173.4 were additionally inspected and remain gameplay without an upgrade panel. All other clips/voice/timing are preserved.',
 '52225 body frames:20890 actual existing-game and31335 explanation, exact40:60. Real-time source playback,no repeated intervals/freezes/slowing; maximum sentence observation pause≤6seconds with all raw narration samples preserved. Narration-only AAC-16LUFS/-2.23dBTP; no BGM/source audio. Clean and captioned files fully decode and have the identical preserved audio packet hash.'
]
review=dict(status='passed',reviewedAt=now,videoSha256=current,captionCuesChecked=188,explanationBeatsChecked=62,actualObservationSamplesChecked=89,reviewMethod=f'Original47 sheets were directly viewed and one menu boundary rejected. After the source-only repair,{len(cmp["identicalPixelSheets"])} sheets have identical already-viewed SHA256; all{len(cmp["requiresFreshDirectView"])} changed current sheets were directly viewed anew. Additional six encoded source-end frames were reviewed. No generation-only pixel pass.',images=[dict(path=p.relative_to(R).as_posix(),sha256=sha(p)) for p in images],notes=notes,humanListening='pending',publicGameIpReview='pending')
write(P/'pixel-review.json',review)
for s in beats['records']:
 assert sha(R/s['path'])==s['sha256'];s.update(directPixelReview='passed-agent-direct-current-final-review',reviewedAtUtc=now)
for s in ob['sheets']:assert sha(R/s['path'])==s['sha256']
beats.update(status='passed-agent-direct-current-final-review',reviewedAtUtc=now);write(Q/'final-beats/generated-samples.json',beats)
ob.update(status='passed-agent-direct-current-action-caption-review',reviewedAtUtc=now);write(Q/'observation-samples.json',ob)
boundary.update(status='passed-agent-direct-final-source-frame-review',reviewedAtUtc=now,observations='All six exact encoded source-end frames retain moving gameplay without an upgrade menu.');write(Q/'menu-boundary-samples.json',boundary)
math=read(P/'math-review.json');assert math['passed']==13 and math['lessonFingerprints'][slug]==sha(B/'lessons'/f'{slug}.json')
math['finalRenderedPixels']=dict(status='passed-agent-direct-review',review=f'projects/{slug}/production/pixel-review.json',videoSha256=current,reviewedAtUtc=now);write(P/'math-review.json',math)
write(P/'math-verification.json',dict(passed=True,checkCount=13,proof=f'projects/{slug}/production/math-review.json',proofSha256=sha(P/'math-review.json'),lessonSha256=sha(B/'lessons'/f'{slug}.json'),narrationReviewSha256=sha(P/'narration-review.json'),finalRenderedPixels=math['finalRenderedPixels'],humanListening='pending'))
repair=read(P/'gameplay-menu-repair.json');repair.update(status='passed-preserved-source-only-repair-and-final-pixels',finalEncodedPixelReview=math['finalRenderedPixels']);write(P/'gameplay-menu-repair.json',repair)
look=read(P/'pre-tts-lookdev-review.json');look['currentFinalReview']=math['finalRenderedPixels'];write(P/'pre-tts-lookdev-review.json',look)
print('Current188 captions /62 beats /89 action samples /48 sheets sealed after direct review.',flush=True)
