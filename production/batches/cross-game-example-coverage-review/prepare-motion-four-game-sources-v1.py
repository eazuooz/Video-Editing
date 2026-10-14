"""Read-only baseline audit and local-only playback setup for motion's four-game revision."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
MEDIA = ROOT / 'shared/assets/presenting-game-scores/raw'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def main():
    R.mkdir(parents=True,exist_ok=True)
    target=R/'source-preflight-v1.json'
    assert not target.exists(), 'Preserve completed preparation; read its report instead.'
    project=ROOT/'projects/motion-sickness-games/project.json'
    m=json.loads(project.read_text('utf-8-sig'))
    protected=[project, ROOT/m['paths']['script'],ROOT/m['paths']['scriptEn'],ROOT/m['paths']['currentMeasuredScenePlan'],ROOT/m['paths']['captionsKo'],ROOT/m['paths']['captionsEn'],ROOT/m['paths']['currentTeachingRevision'],ROOT/m['publishing']['receipt'],ROOT/m['publishing']['scheduleEvidence']]
    for p in (ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1').glob('*direct-review*.json'): protected.append(p)
    protected=list(dict.fromkeys(protected))
    before=[dict(path=rel(p),sha256=sha(p),bytes=p.stat().st_size) for p in protected]
    sources=[]
    for key,path,expected,url in [
        ('portal2','shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4','0d233cfcc3eb86b1e7722d257512ed6cfcc2b6276eac0b349fded54c516843bb','https://www.youtube.com/watch?v=yFRbGppLaUI'),
        ('alyx','shared/assets/responsive-game-feedback/raw/alyx-official.mp4','696eac2cf843d0c0a33d5019726a71c0ceb4a1b0f1cf92d8922d3f07b1d854cd','https://www.youtube.com/watch?v=LTLotwKpLgk')]:
        p=ROOT/path; actual=sha(p);assert actual==expected,(key,actual)
        link=MEDIA/f'motion-four-games-{key}-v1.mp4'
        if not link.exists(): os.link(p,link)
        assert os.path.samefile(p,link)
        probe=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-show_streams','-show_format','-of','json',str(p)]))
        v=next(x for x in probe['streams'] if x['codec_type']=='video')
        sources.append(dict(key=key,path=path,sha256=actual,bytes=p.stat().st_size,url=url,hardlink=rel(link),sameFile=True,video={k:v.get(k) for k in ['width','height','r_frame_rate','avg_frame_rate','time_base','duration','nb_frames']},footageAdopted=False,normalSpeedPlaybackReviewed=False,allNativeSelectedPixelsReviewed=False,sourceAudioAdopted=False))
    html='''<!doctype html><meta charset="utf-8"><title>Motion four-game source comparison v1</title><style>body{background:#111;color:#eee;font:16px sans-serif;margin:16px}video{width:min(100%,1100px);display:block;background:black}button{margin:6px;padding:10px}pre{white-space:pre-wrap}</style><h1>Motion four-game source comparison — original muted 1×</h1><p>Planning candidates only. Browser stop time is not exact native in/out.</p><div id="buttons"></div><video id="v" controls muted preload="metadata"></video><pre id="state"></pre><script>
const v=document.querySelector('#v'),s=document.querySelector('#state');let current=null;const rows=[['portal-aim', 'portal2',16,40],['portal-traverse','portal2',58,82],['portal-cube','portal2',84,99],['alyx-train','alyx',0,14],['alyx-arrival','alyx',24,42],['alyx-platform','alyx',48,69],['alyx-hand','alyx',108,124],['alyx-locomotion','alyx',164,180],['alyx-combat','alyx',180,216]];function state(){s.textContent=JSON.stringify({key:current?.[0],candidateIn:current?.[2],candidateOut:current?.[3],currentTime:v.currentTime,paused:v.paused,muted:v.muted,playbackRate:v.playbackRate,readyState:v.readyState,width:v.videoWidth,height:v.videoHeight},null,2)}
for(const row of rows){let b=document.createElement('button');b.textContent=`${row[0]} ${row[2]}–${row[3]}s`;b.onclick=()=>{current=row;v.pause();v.src=`motion-four-games-${row[1]}-v1.mp4`;v.load();v.onloadedmetadata=()=>{v.currentTime=row[2];v.playbackRate=1;v.muted=true;state()};};document.querySelector('#buttons').append(b)}let play=document.createElement('button');play.textContent='Play selected at 1×';play.onclick=()=>v.play();document.querySelector('#buttons').append(play);let pause=document.createElement('button');pause.textContent='Pause';pause.onclick=()=>v.pause();document.querySelector('#buttons').append(pause);v.ontimeupdate=()=>{if(current&&v.currentTime>=current[3])v.pause();state()};v.onplay=state;v.onpause=state;v.onseeked=state;state();
</script>'''
    page=MEDIA/'motion-four-game-source-comparison-v1.html';assert not page.exists();page.write_text(html,'utf-8')
    assert all(sha(ROOT/x['path'])==x['sha256'] for x in before)
    report=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),status='candidate-screening-before-adoption',baselineVideoId='mBDd9VzSTkA',originalSchedule='2026-10-12T09:00:00+09:00',sourcePage=rel(page),sources=sources,protectedBaseline=before,protectedBaselineUnchanged=True,baselineGames=['PowerWash Simulator','The Talos Principle 2'],candidateNewGames=['Portal 2','Half-Life: Alyx'],minimumGames=4,actualSelectedDistinctGames=2,coverageApproved=False,newScriptCreated=False,ttsStarted=False,finalPairCreated=False,newVideoId=None,deletedVideos=[],policy=dict(url='https://store.steampowered.com/video_policy',readAt=datetime.now(timezone.utc).isoformat(),scope='Valve content instructional free-access videos; YouTube partner ads permitted; no paid access, resale or separately distributed game assets; third-party content requires separate permission',sourceAudioExcluded=True,finalPublicRightsReview=False),localOnlyNewMediaFiles=0,hardlinksCreated=2,newServerStarted=False)
    save(target,report)
    print(json.dumps(dict(report=rel(target),baselineProtected=len(before),sourceCount=len(sources),hashesMatch=True,newMediaCopy=0),ensure_ascii=False))
if __name__=='__main__':main()
