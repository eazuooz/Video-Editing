"""Adapt parent's measured timeline to finite per-line spatial clips and holds.

Input: {scenes:[{id,frames,seconds,lineStarts:[seconds,...]}]}. Each line index
maps to the current revision-v2 lesson, not the historical narration.
"""
from pathlib import Path
import argparse,json,shutil

ROOT=Path(__file__).resolve().parents[5]
LOCAL=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v2'
LESSON=ROOT/'projects/game-math-euler-axis-angle/production/revision-v2/lesson.json'

# Tuple(normalized before, normalized after, motion seconds). A static line
# renders exactly1frame, and the compositor holds that authored diagram state.
PROFILES={
 '03':[(0,0,0),(.12,.24,2.4),(.24,.24,0),(.32,.44,2.4),(.48,.91,6),(.91,.91,0),(.91,.91,0)],
 '04':[(.02,.16,2.4),(.19,.32,2.4),(.36,.49,2.4),(.49,.49,0),(.49,.49,0),(.49,.49,0)],
 '06':[(.02,.30,6),(.30,.30,0),(.30,.30,0),(.30,.30,0),(.56,.62,1.5),(.62,.83,3),(.30,.30,0),(.30,.30,0)],
 '07':[(0,0,0),(.10,.25,2.4),(.29,.43,2.4),(.54,.68,2.4),(.73,.86,2.4),(.90,.90,0)],
 '09':[(0,0,0),(.02,.15,3),(.22,.38,2.4),(.48,.64,3),(.80,.80,0),(.90,.90,0)],
 '10':[(.02,.34,4),(.35,.35,0),(.35,.35,0),(.51,.64,2.4),(.64,.64,0),(.84,.94,2.4)],
 '12':[(.10,.10,0),(.20,.20,0),(.30,.30,0),(.48,.56,2.4),(.70,.70,0),(.80,.80,0)],
 '16':[(0,0,0),(1,1,0),(0,.5,3),(.5,.5,0),(.5,.5,0),(.5,.5,0)],
 '18':[(0,0,0),(.10,.10,0),(.20,.46,3),(.46,.46,0),(.72,.84,2.4),(.84,.84,0)],
 '19':[(0,0,0),(.10,.10,0),(.20,.20,0),(.30,.30,0),(.50,.50,0),(.64,.76,2.4),(.84,.96,2.4)],
 '21':[(.16,.78,4),(.78,.78,0),(.78,.78,0),(.85,.94,2.4),(.97,1,2.4),(1,1,0)],
 '22':[(0,0,0),(.18,.18,0),(.18,.65,3),(.65,.65,0),(.65,.65,0),(.65,.65,0)]
}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--timeline',required=True);ap.add_argument('--output-dir')
    ap.add_argument('--job');ap.add_argument('--placement');ap.add_argument('--scene',action='append')
    args=ap.parse_args()
    timeline=json.loads(Path(args.timeline).read_text(encoding='utf-8-sig'))
    lesson=json.loads(LESSON.read_text(encoding='utf8'));by_id={str(s['id']).zfill(2):s for s in lesson['scenes']}
    destination=Path(args.output_dir) if args.output_dir else LOCAL/'unity-spatial-clips'
    destination.mkdir(parents=True,exist_ok=True)
    clips=[];placements=[]
    for scene in timeline['scenes']:
        sid=str(scene['id']).zfill(2)
        if sid not in PROFILES or (args.scene and sid not in args.scene):continue
        count=int(scene['frames']);seconds=float(scene.get('seconds',count/60))
        if abs(seconds*60-count)>1.01:raise ValueError(f'{sid}: timeline seconds and frames disagree.')
        starts=[float(t) for t in scene['lineStarts']]
        if len(starts)!=len(by_id[sid]['ko']):raise ValueError(f'{sid}: lineStarts must match current revision-v2 narration lines exactly.')
        if len(starts)!=len(PROFILES[sid]):raise ValueError(f'{sid}: capture profile length mismatch.')
        frame_starts=[max(0,min(count,int(round(s*60)))) for s in starts]
        if any(b<=a for a,b in zip(frame_starts,frame_starts[1:])):raise ValueError(f'{sid}: nonincreasing line starts.')
        if frame_starts[0]>0:
            placements.append(dict(sceneId=sid,kind='initial-hold',startFrame=0,endFrame=frame_starts[0],normalized=PROFILES[sid][0][0]))
        ends=frame_starts[1:]+[count]
        for i,(start,end,profile) in enumerate(zip(frame_starts,ends,PROFILES[sid])):
            a,b,move_seconds=profile;budget=end-start
            if budget<1:raise ValueError(f'{sid} line{i}: zero frame budget.')
            capture_frames=min(budget,max(1,round(move_seconds*60))) if a!=b else 1
            stem=f'{sid}-line-{i+1:02d}'
            clip=dict(sceneId=sid,fileStem=stem,frames=capture_frames,startNormalized=a,endNormalized=b)
            clips.append(clip)
            placements.append(dict(sceneId=sid,lineIndex=i,lineNumber=i+1,startFrame=start,endFrame=end,
                startSeconds=start/60,endSeconds=end/60,source=str(destination/(stem+'.mp4')),
                anchors=str(destination/(stem+'.anchors.ndjson')),captureFrames=capture_frames,
                holdFinalFrames=budget-capture_frames,normalizedBefore=a,normalizedAfter=b,
                narration=by_id[sid]['ko'][i],resetAtCue=(i>0 and abs(PROFILES[sid][i-1][1]-a)>.01),
                resetMeaning='Purposeful comparison/reset at the narrated cue; not a continuous trajectory claim.'))
    if not clips:raise ValueError('No selected spatial scene matched the measured timeline.')
    job=dict(outputDirectory=str(destination.resolve()),ffmpegPath=shutil.which('ffmpeg'),renderPngPreviewsOnly=False,clips=clips)
    job_path=Path(args.job) if args.job else LOCAL/'unity-spatial-job.json'
    placement_path=Path(args.placement) if args.placement else LOCAL/'unity-spatial-placement.json'
    job_path.write_text(json.dumps(job,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    placement_path.write_text(json.dumps(dict(schemaVersion=1,timeline=str(Path(args.timeline).resolve()),
        narrationSource=str(LESSON.relative_to(ROOT)),fps=60,output=[1920,1080],
        meaning='Finite60fps authored motion then explicit held explanation state; no gameplay loops/slowdown.',
        captionReserve=dict(center=[960,970],font=48,maxLines=2,yMin=880),placements=placements),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(job=str(job_path),placement=str(placement_path),clips=len(clips),
        renderedFrames=sum(c['frames'] for c in clips),renderedSeconds=sum(c['frames'] for c in clips)/60),ensure_ascii=False))

if __name__=='__main__':main()
