"""Frame/audio/subtitle checks and actual output contact sheets for human review."""
from pathlib import Path
import json, subprocess, io, os
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
WORK=Path(__file__).parent/os.environ.get('DECONSTRUCT_REVISION','final-v1')
manifest=json.loads((ROOT/os.environ.get('DECONSTRUCT_MANIFEST','projects/deconstruct-analyze-rebuild/project.json')).read_text(encoding='utf-8'))
plan=json.loads((WORK/'plan.json').read_text(encoding='utf-8'))
def run(args): return subprocess.check_output(args,stderr=subprocess.STDOUT).decode('utf-8',errors='replace')
results={}
if plan.get('revision') == 'final-v2':
    import numpy as np
    import soundfile as sf
    import hashlib
    baseline=WORK.parent/'private-expansion-baseline'
    original_plan=json.loads((baseline/'production/final-v1/plan.json').read_text(encoding='utf-8'))
    retention=json.loads((WORK/'original-frame-retention.json').read_text(encoding='utf-8'))
    assert retention['allOriginalFramesRetained'] and retention['allOriginalBodyFrames']==original_plan['bodyFrames']
    original_checks=[]
    composed,rate=sf.read(ROOT/manifest['paths']['narration'],dtype='int16')
    for i,part in enumerate(plan['audioParts']):
        piece,piece_rate=sf.read(WORK/f'voice-part-{i+1:02d}.wav',dtype='int16')
        assert piece_rate==rate==24000
        a=round(part['bodyStart']*rate)
        assert np.array_equal(piece,composed[a:a+len(piece)]), 'Composed voice drift'
        source,source_rate=sf.read(ROOT/part['source'],dtype='int16')
        assert source_rate==rate
        begin=round(part['sourceStart']*rate)
        expected=source[begin:begin+len(piece)]
        assert np.array_equal(piece[:len(expected)],expected), 'Original/new voice samples changed'
        assert not np.any(piece[len(expected):]), 'Narration padding contains speech'
        original_checks.append({'kind':part['kind'],'frames':part['frames'],'sourceSha256':hashlib.sha256((ROOT/part['source']).read_bytes()).hexdigest(),'samplesRetained':len(expected),'exactPcmRetained':True})
    def frame_hashes(file):
        output=run(['ffmpeg','-v','error','-i',str(file),'-an','-vf','scale=192:108:flags=area','-f','framehash','-hash','sha256','-'])
        return [line.split(',')[-1].strip() for line in output.splitlines() if line and not line.startswith('#')]
    baseline_hashes=frame_hashes(baseline/'clean.mp4')
    final_hashes=frame_hashes(ROOT/manifest['paths']['videoClean'])
    original_picture=[]
    for scene in plan['scenes']:
        if scene['role']!='preserved-original':continue
        before=next(s for s in original_plan['scenes'] if s['id']==scene['originalId'])
        a,b=round(before['start']*60),round(scene['start']*60)
        assert final_hashes[b:b+scene['frames']]==baseline_hashes[a:a+scene['frames']], 'Original explanation frame lost/changed after concat'
        original_picture.append({'scene':scene['id'],'frames':scene['frames'],'everyOriginalFrameUnchanged':True})
    assert final_hashes[:120]==baseline_hashes[:120]
    assert final_hashes[-600:]==baseline_hashes[-600:]
    assert abs(plan['gameplaySeconds']*60-plan['bodyFrames']*.6)<=1
    results['additivePreservation']={'originalBodyFrames':original_plan['bodyFrames'],'originalExplanationFrames':plan['originalExplanationFrames'],'allOriginalNarrationPcmRetained':True,'allOriginalPicturesRetained':True,'originalPictureScenes':original_picture,'voiceParts':original_checks,'introAndOutroOriginalFramesRetained':True,'ratioClassification':plan['classification'],'ratioMaxErrorFrames':abs(plan['gameplaySeconds']*60-plan['bodyFrames']*.6)}
for key in ['videoClean','videoBurnedCaptions']:
    source=ROOT/manifest['paths'][key]
    meta=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==plan['totalFrames'], (key,v['nb_frames'],plan['totalFrames'])
    assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
    assert any(s['codec_type']=='audio' for s in meta['streams'])
    assert abs(float(meta['format']['duration'])-plan['seconds'])<.06
    run(['ffmpeg','-v','error','-i',str(source),'-f','null','-'])
    results[key]={'frames':int(v['nb_frames']),'seconds':float(meta['format']['duration']),'fullDecodePassed':True}
audio_hashes={}
for key in ['audioMix','videoClean','videoBurnedCaptions']:
    audio_hashes[key]=run(['ffmpeg','-v','error','-i',str(ROOT/manifest['paths'][key]),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).strip()
assert len(set(audio_hashes.values()))==1,audio_hashes
results['sameCopiedAacAudio']=audio_hashes
points=[(1.65,'original channel intro')]
for s in plan['scenes']:
    for segment in s.get('segments',[]):
        points.append((segment['timelineStart']+segment['seconds']*.5,f"{s['id']} {segment['key']}"))
    if not s.get('segments'):
        points.append((s['start']+min(3,s['gameSeconds']/2),f"{s['id']} gameplay"))
        points.append((s['start']+s['gameSeconds']+min(3,s['diagramSeconds']/2),f"{s['id']} explanation"))
points.append((plan['bodyEnd']+5,'original membership rows + logo'))
for s in plan['scenes']:
    for cut in s['cuts']:
        if cut['key'] in ['meat','hollow','portal']:
            points.append((cut['timelineStart']+cut['seconds']*.5,cut['title']))
dest=WORK/'screenshots';dest.mkdir(exist_ok=True)
sheet=Image.new('RGB',(1920,((len(points)+2)//3)*390),'white');draw=ImageDraw.Draw(sheet)
for i,(t,label) in enumerate(points):
    target=dest/f'{i+1:02d}.png'
    subprocess.check_call(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(ROOT/manifest['paths']['videoBurnedCaptions']),'-frames:v','1',str(target)])
    im=Image.open(target);im.thumbnail((630,355));sheet.paste(im,((i%3)*640,(i//3)*390));draw.text(((i%3)*640+10,(i//3)*390+357),f'{t:.3f}s / {label}',fill='black')
sheet.save(WORK/'final-contact-sheet.jpg')
Image.open(dest/'03.png').resize((384,216)).save(WORK/'mobile-caption-check.png')
# Every caption segment is captured from the delivered captioned movie, including
# cue placement changes at gameplay/diagram cuts. These sheets are visually reviewed.
layouts=json.loads((WORK/'caption-layout-qa.json').read_text(encoding='utf-8'))['cues']
assert all(e['end']>e['start'] for e in layouts), 'Empty caption segment'
pages=[]
for i,e in enumerate(layouts):
    page=i//16
    if page==len(pages):pages.append(Image.new('RGB',(1920,1200),'white'))
    t=(e['start']+e['end'])/2
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(ROOT/manifest['paths']['videoBurnedCaptions']),'-frames:v','1','-vf','scale=480:270','-f','image2pipe','-c:v','mjpeg','-'])
    im=Image.open(io.BytesIO(data));sheet=pages[page];x=(i%4)*480;y=((i%16)//4)*300
    sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+8,y+275),f"cue {e['cue']} / {t:.2f}s / {e['picture']}",fill='black')
for i,page in enumerate(pages):page.save(WORK/f'caption-cues-{i+1:02d}.jpg')
def srt_times(file):
    import re
    return re.findall(r'(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})',Path(file).read_text(encoding='utf-8'))
ko=srt_times(ROOT/manifest['paths']['captionsKo']);en=srt_times(ROOT/manifest['paths']['captionsEn']);assert ko==en and len(ko)>0
def seconds(t):
    h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
assert seconds(ko[0][0])>=plan['introSeconds']-.01 and seconds(ko[-1][1])<=plan['bodyEnd']+.01
results['captionChecks']={'cues':len(ko),'identicalKoEnTiming':True,'introAndOutroHaveNoNarrationCues':True,'capturedSegments':len(layouts),'noEmptyCaptionSegments':True,'allSegmentsAvoidProtectedUi':all(not e['overlap'] for e in layouts)}
audio=run(['ffmpeg','-hide_banner','-i',str(ROOT/manifest['paths']['audioMix']),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
results['mixMeasurement']=json.JSONDecoder().raw_decode(audio[audio.rfind('{'):])[0]
assert float(results['mixMeasurement']['input_tp'])<=-1.45,results['mixMeasurement']
results.update({'introSeconds':plan['introSeconds'],'bodySeconds':plan['bodySeconds'],'outroSeconds':10,'gameplaySeconds':plan['gameplaySeconds'],'explanationSeconds':plan['explanationSeconds'],'gameplayShare':plan['gameplayShare'],'humanListeningApproval':'pending','visualReview':'pending'})
(WORK/'qa.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
