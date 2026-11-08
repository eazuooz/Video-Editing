"""CPU-only, frame/sample-accurate contrast-v5 assembly. No work on import.

Use the qwen3-tts/.venv Python (numpy, soundfile). plan/selfcheck do not encode.
sample renders only8 seconds of A01. render accepts one explicitly selected
episode, never an automatic batch. Existing clean masters are read-only.
The final443-row integration manifest is the sole explanation input.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, subprocess
import numpy as np
import soundfile as sf

H=Path(__file__).resolve().parent; B=H.parent; R=B.parents[2]
L=H/'local/explanation-assembly'; FPS=60; RATE=48000; SPF=800
EXTERNAL_PICTURE_KINDS=('independent-gameplay','authored-explanation','retimed-authored-explanation')
INTEGRATION=H/'renderer/integration-caption-safe.json'
if not INTEGRATION.exists():INTEGRATION=H/'renderer/integration-manifest.json'
BASE=B/'relations-v4/review-manifest.json'
spec=importlib.util.spec_from_file_location('contrast_edit_core',H/'edit_core.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
ENC=['-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-bf','0','-g','120','-sc_threshold','0',
     '-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):
    p=Path(p);assert p.resolve().is_relative_to(L.resolve()),'Output must stay in owned local assembly directory'
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def path(p):return (R/Path(p)).resolve()
def relative(p):
    # Read-only media may resolve through the existing C-drive junction.
    p=Path(os.path.abspath(p))
    try:return p.relative_to(R).as_posix()
    except ValueError:return p.as_posix()
def overlap(a,b,c,d):return max(a,c)<min(b,d)
def run(args):subprocess.run([str(x)for x in args],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))['streams']
def authorization(ep):
    c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert c['renderAuthorized']and c['fullLocalProductionAuthorized']and ep in c['episodes']and ep!='A03'
def identity(p,expected):
    p=path(p);assert p.is_file()and sha(p)==expected,('File identity changed',str(p));return p

def caption_intervals(p):
    def sec(t):
        h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
    return [(round(sec(a)*RATE),round(sec(b)*RATE))for a,b in re.findall(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)',Path(p).read_text('utf-8-sig'))]

def music_window(ep,record,picture):
    """Locate exact music samples through both prior EDLs, never round to frames."""
    p=R/'projects'/ep['slug'];opening=read(p/'production/local/relations-v4/opening-edl.json')
    proof_file=p/'production/local/pacing-v3/audio-proof.json';proof=read(proof_file)
    bridge=next(x for x in proof['insertedMusicBridges']if x['key']=='demo-keys')
    a,b=bridge['startSample'],bridge['startSample']+bridge['samples']
    owners=[x for x in opening['audioEdl']if x['kind']=='baseline'and x['sourceStartSample']<=a and b<=x['sourceStartSample']+x['samples']]
    assert len(owners)==1,'Music bridge not retained as one exact PCM region'
    owner=owners[0];start=owner['outputStartSample']+a-owner['sourceStartSample'];end=start+b-a
    assert abs(start-picture['startFrame']*SPF)<SPF and abs(end-picture['endFrame']*SPF)<SPF
    for f in record['files']:
        if f['kind']in ('ko.srt','en.srt'):
            assert not any(overlap(start,end,x,y)for x,y in caption_intervals(path(f['path']))),'Music interval intersects a caption'
    return {'id':picture['id'],'kind':'extend-proven-music-only','startSample':start,'endSample':end,
        'newSamples':end-start+picture['deltaFrames']*SPF,'source':relative(p/'production/local/relations-v4/mix.wav'),
        'sourceStartSample':start,'pictureEditId':picture['id'],'sourceVerified':True,
        'provenance':{'file':relative(proof_file),'sha256':sha(proof_file),'bridge':bridge,
          'openingEdlSHA256':sha(p/'production/local/relations-v4/opening-edl.json'),'exactRetainedOwner':owner},
        'pictureBoundaryOffsetSamples':start-picture['startFrame']*SPF}

def no_overlap(rows,start,end,label):
    rows=sorted(rows,key=lambda r:r[start]);assert all(a[end]<=b[start]for a,b in zip(rows,rows[1:])),label

def picture_override(epid,q,original,maps):
    """Intentional replacement precedence, bounded by exact IDs and speech proof."""
    for r in maps:
        assert not overlap(q['startFrame'],q['endFrame'],r['outputStartFrame'],r['outputEndFrame']),('Protected relationship map',q['id'])
    hits=[r for r in original if overlap(q['startFrame'],q['endFrame'],r['startFrame'],r['endFrame'])]
    assert all(r['kind']!='explanation-duration-extension'for r in hits),'Built-in A15 extension cannot be overridden'
    expected=q.get('expectedUnderlyingExplanationIds',[])
    assert len(expected)==len(set(expected)) and set(expected)=={r['id']for r in hits},('Game/explanation picture collision: declare every underlying ID exactly',q['id'])
    if hits:
        proof=q.get('narrationEvidence');assert proof,'Explanation override requires exact narration evidence'
        evidence=identity(proof['path'],proof['sha256']);assert evidence.suffix.lower()=='.json'
        ids=proof['sentenceIds'];assert ids and len(ids)==len(set(ids))
        timing=read(H/'baseline-sentence-timing.json');rec=next(r for r in timing['records']if r['id']==epid)
        byid={s['id']:s for s in rec['sentences']};assert set(ids)<=set(byid),'Unknown narration IDs'
        assert all(overlap(q['startFrame'],q['endFrame'],byid[s]['startSeconds']*FPS,byid[s]['endSeconds']*FPS)for s in ids),'Narration proof does not coincide with replacement'
        q['overrideValidation']={'underlyingIds':expected,'narrationEvidence':proof,'baselineTimingSha256':sha(H/'baseline-sentence-timing.json'),
            'speechRanges':[{k:byid[s][k]for k in ('id','startSeconds','endSeconds')}for s in ids],
            'policy':'Replacement wins only in its declared interval; unchanged overlay fragments retain exact source frames.'}

def audio_edl(total,edits,baseline):
    no_overlap(edits,'startSample','endSample','Overlapping audio edits')
    at=0;out=0;parts=[]
    for e in sorted(edits,key=lambda x:x['startSample']):
        a,b=e['startSample'],e['endSample'];n=e['newSamples']
        assert all(isinstance(x,int)for x in (a,b,n))and at<=a<b<=total and n>0
        if a>at:
            parts.append({'kind':'preserve','source':baseline,'sourceStartSample':at,'samples':a-at,'outputStartSample':out});out+=a-at
        parts.append({**e,'samples':n,'outputStartSample':out});out+=n;at=b
    if at<total:parts.append({'kind':'preserve','source':baseline,'sourceStartSample':at,'samples':total-at,'outputStartSample':out});out+=total-at
    for x in parts:x['outputEndSample']=x['outputStartSample']+x['samples']
    return parts,out

def build_episode(ep,record,extension):
    authorization(ep['id']);clean=next(x for x in record['files']if x['kind']=='clean.mp4')
    baseline=identity(clean['path'],clean['sha256']);total=record['frames'];p=R/'projects'/ep['slug']
    pcm=p/'production/local/relations-v4/mix.wav';identity(pcm,record['audioProof']['mixSha256']);info=sf.info(pcm)
    assert info.samplerate==RATE and info.channels==2 and info.frames==total*SPF
    overlays=[];replacements=[];audio=[]
    for r in ep['rows']:
        identity(r['output'],r['sha256'])
        q={'id':r['id'],'kind':'authored-explanation','startFrame':r['relationFrameStart'],'endFrame':r['relationFrameEnd'],
           'newFrames':r['newFrames'],'picture':r['output'],'pictureSha256':r['sha256'],'sourceStartFrame':0,'sourceVerified':True}
        if q['newFrames']==q['endFrame']-q['startFrame']:overlays.append(q)
        else:
            assert ep['id']=='A15'and r['id']=='A15-keys-three-complete-native-passes'
            q['deltaFrames']=q['newFrames']-(q['endFrame']-q['startFrame']);assert q['deltaFrames']==230
            q['kind']='explanation-duration-extension';replacements.append(q);audio.append(music_window(ep,record,q))
    original=list(overlays)+list(replacements);ids={x['id']for x in original}
    for raw in extension.get('pictureEdits',[]):
        q=dict(raw);assert q['id']not in ids,'Duplicate built-in or extension edit';ids.add(q['id'])
        assert q['kind']in EXTERNAL_PICTURE_KINDS and q.get('sourceVerified')is True
        assert all(isinstance(q[x],int)for x in ('startFrame','endFrame','newFrames'))
        assert 0<=q['startFrame']<q['endFrame']<=total and q['newFrames']>0
        picture_override(ep['id'],q,original,ep['preservedRelationRegions'])
        src=identity(q['picture'],q['pictureSha256']);v=probe(src);v=next(x for x in v if x['codec_type']=='video')
        assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1','Prepare an exact1920x1080/60 native-timed passage before assembly'
        q.setdefault('sourceStartFrame',0);assert isinstance(q['sourceStartFrame'],int)and q['sourceStartFrame']>=0
        assert int(v['nb_frames'])>=q['sourceStartFrame']+q['newFrames']
        replacements.append(q)
    no_overlap(overlays,'startFrame','endFrame','Overlapping built-in explanation plates')
    no_overlap(replacements,'startFrame','endFrame','Overlapping external/built-in duration replacements')
    byid={x['id']:x for x in replacements};linked=set()
    for raw in extension.get('audioEdits',[]):
        q=dict(raw);assert q['id']not in ids,'Duplicate edit id';ids.add(q['id'])
        assert q.get('sourceVerified')is True and q['audioKind']=='complete-mix','Supply reviewed complete mix, not unblended dry TTS'
        for check in q.get('inputChecks',[]):identity(check['path'],check['sha256'])
        assert q['startSample']>=0 and q['endSample']<=total*SPF
        src=identity(q['source'],q['sourceSha256']);si=sf.info(src)
        assert si.samplerate==RATE and si.channels==2
        q.setdefault('sourceStartSample',0);assert si.frames>=q['sourceStartSample']+q['newSamples']
        delta=q['newSamples']-(q['endSample']-q['startSample']);pic=byid.get(q.get('pictureEditId'))
        if pic:
            assert pic['kind']in EXTERNAL_PICTURE_KINDS,'Built-in A15 audio cannot be replaced again'
            assert pic['id']not in linked;linked.add(pic['id'])
            assert delta==(pic['newFrames']-(pic['endFrame']-pic['startFrame']))*SPF
            assert abs(q['startSample']-pic['startFrame']*SPF)<=SPF and abs(q['endSample']-pic['endFrame']*SPF)<=SPF,'Audio/picture splice boundaries differ by more than one frame'
        else:assert delta==0,'Length-changing speech needs its matching prepared picture edit'
        for x in ep['preservedRelationRegions']:
            assert not overlap(q['startSample'],q['endSample'],x['outputStartFrame']*SPF,x['outputEndFrame']*SPF),'Protected map PCM'
        q['kind']='replace-complete-mix';audio.append(q)
    for q in replacements:
        if q['kind']in EXTERNAL_PICTURE_KINDS and q['newFrames']!=q['endFrame']-q['startFrame']:assert q['id']in linked,'Length-changing picture lacks matched PCM'
    picture=core.picture_edl(total,relative(baseline),overlays,replacements)
    allrows={x['id']:x for x in overlays+replacements}
    for row in picture:
        if row['id']=='baseline':row['sourceSha256']=clean['sha256']
        else:
            src=allrows[row['id']];row['kind']=src['kind'];row['sourceStartFrame']+=src.get('sourceStartFrame',0);row['sourceSha256']=src['pictureSha256']
    sound,samples=audio_edl(total*SPF,audio,relative(pcm));frames=picture[-1]['outputEndFrame'];assert samples==frames*SPF
    return {'schemaVersion':1,'id':ep['id'],'slug':ep['slug'],'baselineRevision':'relations-v4','baselineReviewSHA256':sha(BASE),
        'integrationManifestSHA256':sha(INTEGRATION),'editCoreSHA256':sha(H/'edit_core.py'),'assemblyCodeSHA256':sha(Path(__file__)),
        'baselineFrames':total,'frames':frames,'additionalFrames':frames-total,'sampleRate':RATE,'audioSamples':samples,
        'baselinePicture':relative(baseline),'baselinePictureSha256':clean['sha256'],'baselinePcm':relative(pcm),'baselinePcmSha256':sha(pcm),
        'pictureEdl':picture,'audioEdl':sound,'pictureEdits':overlays+replacements,'audioEdits':audio,
        'captionInputs':[x for x in record['files']if x['kind']in ('ko.srt','en.srt')],
        'captionPolicy':'Keep fixed caption style. Retain and shift unaffected cues using exact audio sample deltas. Replace changed speech cues from reviewed new timings; no stale captions burned here.',
        'pictureOnlyDeltaFrames':sum(x['newFrames']-(x['endFrame']-x['startFrame'])for x in replacements),
        'stage':'virtual-edl-validated-not-rendered','noAudioStretch':True,'sourceApproval':'Own explanation QA and caller-provided independently reviewed game/mix evidence only.'}

def plan_all(extra=None,selected=None):
    manifest=read(INTEGRATION);assert manifest['status']=='ready-for-parent-final-assembly'and manifest['precedenceResolved']
    assert len(manifest['episodes'])==17 and sum(len(x['rows'])for x in manifest['episodes'])==443
    ext=read(extra)if extra else {'schemaVersion':1,'clock':'relations-v4','baselineReviewSHA256':sha(BASE),'episodes':[]}
    assert ext['schemaVersion']==1 and ext['clock']=='relations-v4'and ext['baselineReviewSHA256']==sha(BASE)
    ex={e['id']:e for e in ext['episodes']};assert len(ex)==len(ext['episodes'])and set(ex)<={e['id']for e in manifest['episodes']}
    if selected:assert selected in {e['id']for e in manifest['episodes']},'Selected episode must belong to the approved17 (A03 excluded)'
    records={r['id']:r for r in read(BASE)['records']};plans=[]
    for ep in manifest['episodes']:
        if selected and ep['id']!=selected:continue
        d=build_episode(ep,records[ep['id']],ex.get(ep['id'],{}));save(L/ep['id']/'edl.json',d);plans.append({'id':ep['id'],'frames':d['frames'],'delta':d['additionalFrames'],'file':relative(L/ep['id']/'edl.json')})
    save(L/(f'planning-report-{selected}.json'if selected else'planning-report.json'),{'status':'selected-episode-virtual-edl-validated'if selected else'all17-virtual-edls-validated','episodes':plans,'noWholeVideoRendersStarted':True,
        'noGPU':True,'onlyExplanationInput':relative(INTEGRATION),'integrationManifestSHA256':sha(INTEGRATION),'extensionInput':str(extra)if extra else None})
    return plans

def crop_edl(rows,start,end,startkey,endkey,sourcekey,lengthkey):
    out=[]
    for r in rows:
        a,b=max(start,r[startkey]),min(end,r[endkey])
        if a>=b:continue
        q=dict(r);q[sourcekey]=r.get(sourcekey,0)+(a-r[startkey]);q[lengthkey]=b-a;q[startkey]=a-start;q[endkey]=b-start
        if 'oldStartFrame'in r and r['oldEndFrame']-r['oldStartFrame']==r[endkey]-r[startkey]:
            q['oldStartFrame']=r['oldStartFrame']+a-r[startkey];q['oldEndFrame']=q['oldStartFrame']+b-a
        out.append(q)
    assert out[0][startkey]==0 and out[-1][endkey]==end-start
    return out

def music_loop(source,length):
    # Only a verified music bridge is synthesized; no retained speech is faded.
    fade=min(480,len(source)//4);step=len(source)-fade;out=np.zeros((length+len(source),source.shape[1]),np.float32)
    for at in range(0,length,step):
        block=source.copy()
        if at:block[:fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None]
        block[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
        out[at:at+len(block)]+=block
    out=out[:length];out[:fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None];out[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
    return out

def assemble_audio(rows,output):
    evidence=[]
    with sf.SoundFile(output,'w',samplerate=RATE,channels=2,subtype='FLOAT')as dest:
        for row in rows:
            source=path(row['source']);start=row.get('sourceStartSample',0);n=row['samples']
            if row['kind']=='extend-proven-music-only':
                with sf.SoundFile(source)as f:f.seek(start);chunk=f.read(row['endSample']-row['startSample'],dtype='float32',always_2d=True)
                dest.write(music_loop(chunk,n));continue
            digest=hashlib.sha256()
            with sf.SoundFile(source)as f:
                f.seek(start);left=n
                while left:
                    chunk=f.read(min(left,48000*8),dtype='float32',always_2d=True);assert len(chunk)>0
                    assert np.isfinite(chunk).all()and np.max(np.abs(chunk))<1,'Invalid/clipping complete PCM'
                    dest.write(chunk);digest.update(chunk.tobytes());left-=len(chunk)
            evidence.append({'kind':row['kind'],'sourceStartSample':start,'outputStartSample':row['outputStartSample'],'samples':n,'sourcePcmSha256':digest.hexdigest()})
    with sf.SoundFile(output)as check:
        for e in evidence:
            check.seek(e['outputStartSample']);left=e['samples'];digest=hashlib.sha256()
            while left:
                data=check.read(min(left,48000*8),dtype='float32',always_2d=True);assert len(data)>0;digest.update(data.tobytes());left-=len(data)
            assert digest.hexdigest()==e['sourcePcmSha256'];e['exactSerializedEquality']=True
    return {'output':relative(output),'sha256':sha(output),'allPreservedPcmSamplesEqual':True,'segments':evidence,'noVoiceStretchOrFade':True}

def segment(row,directory):
    sig=hashlib.sha256(json.dumps({'sourceSha':row['sourceSha256'],'start':row['sourceStartFrame'],'frames':row['frames'],'encoder':ENC},sort_keys=True).encode()).hexdigest()
    dest=directory/(sig+'.mp4');receipt=dest.with_suffix('.json')
    if dest.exists()and receipt.exists()and read(receipt).get('sha256')==sha(dest):return dest
    src=identity(row['source'],row['sourceSha256']);start=row['sourceStartFrame'];seek=max(0,start//FPS-2);trim=start-seek*FPS
    # Integer-second seek plus integer-frame trim avoids fractional seek rounding.
    filt=f'trim=start_frame={trim}:end_frame={trim+row["frames"]},setpts=N/(60*TB)'
    run(['ffmpeg','-v','error','-nostdin','-y','-threads','4','-ss',seek,'-i',src,'-filter_threads','1','-vf',filt,'-frames:v',row['frames'],'-an',*ENC,'-movflags','+faststart',dest])
    v=probe(dest);assert len(v)==1 and(v[0]['width'],v[0]['height'],v[0]['avg_frame_rate'],int(v[0]['nb_frames']))==(1920,1080,'60/1',row['frames'])
    save(receipt,{'signature':sig,'sha256':sha(dest),'frames':row['frames'],'source':relative(src),'sourceStartFrame':start,'noAudio':True})
    return dest

def render_plan(plan,start=None,end=None):
    authorization(plan['id']);assert plan['integrationManifestSHA256']==sha(INTEGRATION)
    assert plan['assemblyCodeSHA256']==sha(Path(__file__))and plan['editCoreSHA256']==sha(H/'edit_core.py'),'Regenerate EDL after code changes'
    identity(plan['baselinePicture'],plan['baselinePictureSha256']);identity(plan['baselinePcm'],plan['baselinePcmSha256'])
    for row in plan['audioEdits']:
        if row['kind']=='replace-complete-mix':identity(row['source'],row['sourceSha256'])
    sample=start is not None
    if sample:assert plan['id']=='A01'and 0<=start<end<=plan['frames']and end-start<=600
    else:start,end=0,plan['frames']
    folder=L/plan['id']/('sample'if sample else'captionless');folder.mkdir(parents=True,exist_ok=True);parts=folder/'parts';parts.mkdir(exist_ok=True)
    pic=crop_edl(plan['pictureEdl'],start,end,'outputStartFrame','outputEndFrame','sourceStartFrame','frames')
    aud=crop_edl(plan['audioEdl'],start*SPF,end*SPF,'outputStartSample','outputEndSample','sourceStartSample','samples')
    assert not sample or all(x['kind']=='preserve'for x in aud),'A01 sample must preserve original PCM only'
    files=[segment(r,parts)for r in pic];concat=folder/'concat.txt'
    concat.write_text('ffconcat version 1.0\n'+''.join("file '"+str(p.resolve()).replace('\\','/').replace("'","'\\''")+"'\n"for p in files),'utf8')
    silent=folder/'picture.mp4';run(['ffmpeg','-v','error','-nostdin','-y','-f','concat','-safe','0','-i',concat,'-map','0:v','-c','copy','-movflags','+faststart',silent])
    wav=folder/'mix.wav';audio_proof=assemble_audio(aud,wav);assert sf.info(wav).frames==(end-start)*SPF
    mezz=folder/'mezzanine.mkv';run(['ffmpeg','-v','error','-nostdin','-y','-i',silent,'-i',wav,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','pcm_f32le',mezz])
    v=probe(silent)[0];assert int(v['nb_frames'])==end-start and v['avg_frame_rate']=='60/1'
    run(['ffmpeg','-v','error','-threads','4','-i',mezz,'-f','null','-'])
    # Decoded serialized mezzanine PCM must equal the WAV samples, not only duration.
    got=subprocess.check_output(['ffmpeg','-v','error','-i',mezz,'-map','0:a','-acodec','pcm_f32le','-f','hash','-hash','sha256','-'],text=True).strip()
    digest=hashlib.sha256()
    with sf.SoundFile(wav)as f:
        while True:
            data=f.read(48000*8,dtype='float32',always_2d=True)
            if not len(data):break
            digest.update(data.tobytes())
    assert got=='SHA256='+digest.hexdigest()
    preview=None
    if sample:
        preview=folder/'A01-sample.mp4';run(['ffmpeg','-v','error','-nostdin','-y','-i',mezz,'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',preview])
    receipt={'stage':'short-sample-only'if sample else'captionless-mezzanine-ready','id':plan['id'],'rangeFrames':[start,end],
        'frames':end-start,'pictureEdl':pic,'audioEdl':aud,'audioProof':audio_proof,'mezzanine':relative(mezz),'mezzanineSha256':sha(mezz),
        'preview':relative(preview)if preview else None,'fullDecode':'passed','mezzaninePcmEqualsWavExactly':True,'fps':60,'resolution':[1920,1080],
        'captioned':False,'wholeVideoRendered':not sample,'humanViewed':False,'humanListened':False,'device':'CPU4/one sequential worker'}
    save(folder/'receipt.json',receipt);return receipt

def sample_qa():
    from PIL import Image,ImageDraw
    folder=L/'A01/sample';r=read(folder/'receipt.json');video=folder/'picture.mp4';samples=[]
    times=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))['frames']
    stamps=np.array([float(x['best_effort_timestamp_time'])for x in times]);assert len(stamps)==480 and np.max(np.abs(stamps-np.arange(480)/FPS))<.000002
    for n in (54,60,120,240,360,444):
        dest=folder/f'frame-{n:03}.png';run(['ffmpeg','-v','error','-nostdin','-y','-i',video,'-vf',f'select=eq(n\\,{n})','-frames:v','1',dest])
        with Image.open(dest)as im:im.resize((375,211)).save(dest.with_name(dest.stem+'-375.png'))
        samples.append({'frame':n,'path':relative(dest)})
    # Independent direct-frame extraction of the original sources validates the
    # join; it does not reuse the assembly's integer-seek/trim implementation.
    differences=[]
    for n in (59,60,180,300,420):
        row=next(x for x in r['pictureEdl']if x['outputStartFrame']<=n<x['outputEndFrame']);source_frame=row['sourceStartFrame']+n-row['outputStartFrame']
        def raw(file,frame):
            return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-threads','4','-i',str(path(file)),'-vf',f'select=eq(n\\,{frame})','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']),np.uint8).astype(np.int16)
        actual=raw(video,n);expected=raw(row['source'],source_frame);assert actual.shape==expected.shape
        error=float(np.abs(actual-expected).mean());assert error<3,(n,'Wrong source/cut or excessive encode error',error)
        differences.append({'outputFrame':n,'expectedSourceFrame':source_frame,'sourceId':row['id'],'meanAbsoluteRgbDifference':error})
    sheet=Image.new('RGB',(1125,422),'#080c0a')
    for i,s in enumerate(samples):
        with Image.open(path(s['path']))as im:sheet.paste(im.resize((375,211)),((i%3)*375,(i//3)*211))
    sheet.save(folder/'contact.png')
    save(folder/'visual-qa.json',{'scope':'8-second A01 actual encoded sample, no full-video or human listening claim.','pictureSHA256':sha(video),
        'uniform60fps480Frames':True,'directSourceBoundaryChecks':differences,'samples':samples,'modelImageInspection':'pending','humanViewed':False,'humanListened':False})

def selfcheck():
    core.selfcheck();L.mkdir(parents=True,exist_ok=True)
    a=[{'id':'music','kind':'extend-proven-music-only','startSample':30*SPF-160,'endSample':50*SPF-160,'newSamples':40*SPF,'source':'fixture.wav','sourceStartSample':30*SPF-160}]
    rows,n=audio_edl(100*SPF,a,'fixture.wav');assert n==120*SPF
    assert rows[-1]['sourceStartSample']==50*SPF-160 and rows[-1]['outputStartSample']==70*SPF-160
    # Preservation checks use serialized float PCM, including the160samples that
    # would be lost if a music window were incorrectly rounded to picture frames.
    test=L/'selfcheck';test.mkdir(exist_ok=True);source=test/'fixture.wav';dest=test/'result.wav'
    x=(np.sin(np.arange(100*SPF)*.017)*.1).astype(np.float32);data=np.column_stack([x,-x]);sf.write(source,data,RATE,subtype='FLOAT')
    for row in rows:row['source']=relative(source)
    evidence=assemble_audio(rows,dest);out,_=sf.read(dest,dtype='float32',always_2d=True)
    assert np.array_equal(out[:30*SPF-160],data[:30*SPF-160])and np.array_equal(out[70*SPF-160:],data[50*SPF-160:])
    bad=[{'startFrame':10,'endFrame':30},{'startFrame':29,'endFrame':40}]
    try:no_overlap(bad,'startFrame','endFrame','collision')
    except AssertionError:pass
    else:raise AssertionError('Collision accepted')
    good=[{'startFrame':10,'endFrame':30},{'startFrame':30,'endFrame':40}];no_overlap(good,'startFrame','endFrame','adjacency')
    manifest=read(INTEGRATION);ep=next(e for e in manifest['episodes']if e['id']=='A01');record=next(e for e in read(BASE)['records']if e['id']=='A01')
    r=ep['rows'][0]
    collision={'id':'deliberate-collision-fixture','kind':'independent-gameplay','startFrame':r['relationFrameStart'],'endFrame':r['relationFrameEnd'],
        'newFrames':r['newFrames'],'picture':'not-a-real-source.mp4','pictureSha256':'unused','sourceVerified':True}
    try:build_episode(ep,record,{'pictureEdits':[collision]})
    except AssertionError as error:assert 'Game/explanation picture collision'in str(error)
    else:raise AssertionError('Actual explanation collision accepted')
    collision['id']=r['id']
    try:build_episode(ep,record,{'pictureEdits':[collision]})
    except AssertionError as error:assert 'Duplicate'in str(error)
    else:raise AssertionError('Built-in edit applied a second time')
    # A deliberately evidenced middle override retains both original fragments.
    timingfile=H/'baseline-sentence-timing.json';sentence=next(x for x in read(timingfile)['records']if x['id']=='A01')['sentences'][0]
    aa=int(sentence['startSeconds']*FPS);bb=int(sentence['endSeconds']*FPS)
    under={'id':'owned-fixture','kind':'authored-explanation','startFrame':aa-10,'endFrame':bb+10,'picture':'own.mp4','newFrames':bb-aa+20}
    override={'id':'replacement-fixture','kind':'independent-gameplay','startFrame':aa,'endFrame':bb,'newFrames':bb-aa+9,'picture':'new.mp4','sourceVerified':True,
        'expectedUnderlyingExplanationIds':['owned-fixture'],'narrationEvidence':{'path':relative(timingfile),'sha256':sha(timingfile),'sentenceIds':[sentence['id']]}}
    picture_override('A01',override,[under],[])
    resolved=core.picture_edl(bb+20,'old.mp4',[under],[override]);owned=[x for x in resolved if x['id']=='owned-fixture']
    assert [(x['frames'],x['sourceStartFrame'])for x in owned]==[(10,0),(10,bb-aa+10)]
    assert resolved[-1]['outputEndFrame']==bb+29
    for original,maps,label in [([dict(under,kind='explanation-duration-extension')],[],'A15'),([],[{'outputStartFrame':aa,'outputEndFrame':bb}],'map')]:
        try:picture_override('A01',override,original,maps)
        except AssertionError:pass
        else:raise AssertionError(label+' override accepted')
    save(L/'selfcheck.json',{'passed':True,'tests':['edit_core preservation/boundary suite','sample-accurate160sample music offset','serialized untouched PCM equality','touching picture ranges allowed, actual overlap rejected'],
        'actualManifestCollisionRejected':True,'duplicateBuiltInEditRejected':True,'explicitNarrationOverridePreservesBothFragments':True,
        'mapAndA15OverrideRejected':True,'syntheticPcmProof':evidence,'wholeVideoEncoded':False})

def schema():
    integer={'type':'integer','minimum':0};positive={'type':'integer','minimum':1};fingerprint={'type':'string','pattern':'^[0-9a-f]{64}$'}
    picture={'type':'object','required':['id','kind','startFrame','endFrame','newFrames','picture','pictureSha256','sourceVerified'],
        'properties':{'id':{'type':'string'},'kind':{'enum':list(EXTERNAL_PICTURE_KINDS)},'startFrame':integer,'endFrame':positive,'newFrames':positive,
            'picture':{'type':'string'},'pictureSha256':fingerprint,'sourceStartFrame':integer,'sourceVerified':{'const':True},
            'expectedUnderlyingExplanationIds':{'type':'array','uniqueItems':True,'items':{'type':'string'}},
            'narrationEvidence':{'type':'object','required':['path','sha256','sentenceIds'],'properties':{
                'path':{'type':'string'},'sha256':fingerprint,'sentenceIds':{'type':'array','minItems':1,'uniqueItems':True,'items':{'type':'string'}}}}}}
    sound={'type':'object','required':['id','audioKind','startSample','endSample','newSamples','source','sourceSha256','sourceVerified'],
        'properties':{'id':{'type':'string'},'audioKind':{'const':'complete-mix'},'startSample':integer,'endSample':positive,'newSamples':positive,
            'source':{'type':'string'},'sourceSha256':fingerprint,'sourceStartSample':integer,'sourceVerified':{'const':True},'pictureEditId':{'type':'string'},
            'inputChecks':{'type':'array','items':{'type':'object','required':['path','sha256'],'properties':{'path':{'type':'string'},'sha256':fingerprint}}}}}
    save(L/'extensions.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Contrast-v5 baseline-clock external edits','type':'object',
      'required':['schemaVersion','clock','baselineReviewSHA256','episodes'],'properties':{'schemaVersion':{'const':1},'clock':{'const':'relations-v4'},
      'baselineReviewSHA256':fingerprint,'episodes':{'type':'array','items':{'type':'object','required':['id'],'properties':{'id':{'enum':[e['id']for e in read(INTEGRATION)['episodes']]},
          'pictureEdits':{'type':'array','items':picture},'audioEdits':{'type':'array','items':sound}}}}},
      '$comment':'Runtime additionally verifies hashes, review flags, bounds, exact sample/frame delta, shared-map protection and cross-track picture conflicts.'})
    d={'schemaVersion':1,'clock':'relations-v4','baselineReviewSHA256':sha(BASE),'episodes':[{'id':'A01',
      'pictureEdits':[{'id':'A01-new-game-example','kind':'independent-gameplay','startFrame':120,'endFrame':180,'newFrames':60,
        'picture':'REPLACE_WITH_PREPARED_1080P60_PASSAGE.mp4','pictureSha256':'SHA256','sourceStartFrame':0,'sourceVerified':True}],
      'audioEdits':[{'id':'A01-new-complete-mix','audioKind':'complete-mix','startSample':96000,'endSample':144000,'newSamples':48000,
        'source':'REPLACE_WITH_REVIEWED_48K_STEREO_COMPLETE_MIX.wav','sourceSha256':'SHA256','sourceStartSample':0,'sourceVerified':True,'pictureEditId':'A01-new-game-example'}]}],
      '_instructions':['This is an example, not approved footage/timing. Remove all example rows before real use.','Picture ranges are integer60fps frames; audio ranges are exact48k samples. Ends exclusive.','An intentional explanation override must declare exact expectedUnderlyingExplanationIds and narrationEvidence path/sha256/sentenceIds. Each sentence must intersect the baseline interval. Left/right explanation fragments remain intact.','Protected maps and the built-in A15 duration extension cannot be overridden. External edits may not overlap one another.','Kinds: independent-gameplay, authored-explanation, retimed-authored-explanation. These labels do not verify source evidence by themselves.','Same-length audio-only changes are allowed without pictureEditId. Length changes require a linked prepared picture with the exact same delta.','Audio boundaries may differ from linked frame edges by at most800samples; no voice stretching/padding is inferred.','Supply complete mixed PCM. Dry TTS must be mixed and reviewed before integration.','A15 is inserted once automatically. Do not add its observation extension to this file.','No downloaded gameplay is considered approved merely by this template. sourceVerified must reflect actual review.']}
    save(L/'extension-example.json',d)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['plan','selfcheck','sample','sample-qa','render']);ap.add_argument('--extensions');ap.add_argument('--episode');a=ap.parse_args()
    os.environ.update(OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4')
    if a.command=='selfcheck':selfcheck();schema()
    elif a.command=='plan':schema();plans=plan_all(a.extensions,a.episode);print('Validated',len(plans),'virtual EDLs; total added frames',sum(p['delta']for p in plans))
    elif a.command=='sample':
        p=read(L/'A01/edl.json');r=render_plan(p,4897,5377);print('A01 sample ready:',r['preview'])
    elif a.command=='sample-qa':sample_qa();print('A01 boundary/PTS/sample QA ready')
    else:
        assert a.episode and a.episode!='A03','Render takes exactly one explicitly selected episode; no implicit batch'
        print(render_plan(read(L/a.episode/'edl.json')))
if __name__=='__main__':main()
