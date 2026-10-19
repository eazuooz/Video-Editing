"""Read-only clip QA: verify receipts, extract 12 selected pixels once, derive mobile.

Does not render or modify production media/narration/timing. Reuses extracted pixels
only when their exact clip SHA, sample frames and extractor signature match.
"""
from pathlib import Path
import hashlib, json, subprocess
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parents[4]
P = R / 'projects/game-math-euler-axis-angle'
H = Path(__file__).parent
E = P / 'production/local/revision-v5/gizmos'
O = P / 'production/local/revision-v5/preflight-final'
REPORT = H / 'gizmo-review.json'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    assert read(R/'shared/publishing/video-production-control.json')['selectedVideo'] == P.name
    plan = read(H/'gizmo-plan.json')
    timeline = read(P/plan['timeline'])
    annotations = read(P/plan['sourceAnnotation'])
    outputs = read(E/'outputs.json')
    caption_ass = P/'production/local/revision-v3/captions.ko.ass'
    O.mkdir(parents=True, exist_ok=True)
    samples, checks = [], []
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
    for repl in outputs['replacements']:
        name = repl['id']; receipt = read(E/(name+'.json')); inp = receipt['inputs']
        w = next(x for x in plan['windows'] if x['id']==name)
        tracker = next(x for x in annotations['windows'] if x['id']==name)
        cut = next(c for c in timeline['cuts'] if c['scene']==tracker['scene'] and c['sourceId']==tracker['sourceId'] and c['sourceStart']<=w['start'] and c['sourceEnd']>=w['end'])
        assert sha(E/(name+'.ass')) == inp['assSha256']
        assert sha(caption_ass) == inp['captionAssSha256']
        assert inp['sourceSha256'] == cut['sourceSha256']
        assert inp['sourceStart'] == w['start']
        assert inp['globalStartFrame'] == repl['globalStartFrame'] == cut['globalStartFrame']+round((w['start']-cut['sourceStart'])*60)
        assert inp['frames'] == repl['frames'] == round(w['end']*60)-round(w['start']*60)
        assert receipt['files'] == repl['files']
        for kind, entry in repl['files'].items():
            assert sha(R/entry['file']) == entry['sha256'], (name, kind, 'file SHA changed')
        clip = R/repl['files']['captioned']['file']; clip_sha = sha(clip)
        probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames','-of','json',str(clip)], text=True))['streams'][0]
        assert (probe['width'], probe['height'], probe['r_frame_rate'], int(probe['nb_frames'])) == (1920,1080,'60/1',repl['frames'])
        frame_nums = [39, repl['frames']//2, round(repl['frames']-0.12*60)]
        stamp = dict(clipSha256=clip_sha, sampleFrames=frame_nums, extractorSha256=sha(Path(__file__)))
        cache = O/(name+'-extraction.json')
        paths = [O/(name+f'-sample-{i+1:02}.jpg') for i in range(3)]
        if not (cache.exists() and read(cache)==stamp and all(x.exists() for x in paths)):
            select = '+'.join('eq(n\\,%d)'%n for n in frame_nums)
            subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(clip),'-an','-vf','select='+select,'-fps_mode','vfr','-frames:v','3','-q:v','2',str(O/(name+'-sample-%02d.jpg'))],check=True)
            save(cache,stamp)
        for i,(frame,path) in enumerate(zip(frame_nums,paths)):
            im = Image.open(path).convert('RGB'); assert im.size==(1920,1080)
            mobile = path.with_name(path.stem+'-mobile.jpg')
            im.resize((375,211),Image.Resampling.LANCZOS).save(mobile,quality=96)
            samples.append(dict(id=name, phase=['early','middle','end'][i], localFrame=frame, localSeconds=frame/60, sourceSeconds=w['start']+frame/60, globalFrame=repl['globalStartFrame']+frame, globalSeconds=(repl['globalStartFrame']+frame)/60, native=path.relative_to(R).as_posix(), nativeSha256=sha(path), mobile=mobile.relative_to(R).as_posix(), mobileSha256=sha(mobile)))
        assert sha(clip)==clip_sha, 'Clip changed during extraction'
        checks.append(dict(id=name, receiptInputsVerified=True, allCleanAndCaptionedFileHashesVerified=True, captionedSha256=clip_sha, assSha256=inp['assSha256'], stream=probe, originalSourceHashComparedToCanonicalManifest=True, originalRawSourceRehashed=False))
    board = Image.new('RGB',(1125,4*242),'#151515'); draw=ImageDraw.Draw(board)
    for i,s in enumerate(samples):
        x=(i%3)*375; y=(i//3)*242
        board.paste(Image.open(R/s['mobile']),(x,y))
        draw.text((x+5,y+214),s['id']+' '+s['phase']+' %.3fs'%s['localSeconds'],font=font,fill='white')
    board_path=O/'mobile-12-samples.jpg'; board.save(board_path,quality=96)
    report=dict(revision=plan['revision'], scope='Four current captioned replacement clips: 12 native samples and their 375px derivatives only; moving playback and complete final-master review are separate.', rendererSha256=sha(H/'gizmo-render.py'), planSha256=sha(H/'gizmo-plan.json'), outputsSha256=sha(E/'outputs.json'), sourceAnnotationSha256=sha(P/plan['sourceAnnotation']), timelineSha256=sha(P/plan['timeline']), captionAssSha256=sha(caption_ass), receipts=checks, samples=samples, mobileBoard=board_path.relative_to(R).as_posix(), staticDirectReview='pending', movingPlayback='pending root review', humanListening='pending; no audio generated or changed', productionMediaChanged=False)
    save(REPORT,report)
    print(json.dumps(dict(report=str(REPORT),samples=len(samples),checks=len(checks),mobileBoard=str(board_path)),ensure_ascii=False))

if __name__=='__main__': main()
