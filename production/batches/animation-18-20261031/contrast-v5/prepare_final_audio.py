"""Prepare changed speech only. Never starts TTS, ASR, GPU or platform work.

scripts: apply reviewed KO/EN changes, preserving every other sentence.
prepare: inspect complete available takes and make reviewed-boundary candidates
and complete-mix passages. ASR/semantic clause timing remains explicitly pending.
captions: use the parent's final assembly EDL for current provisional SRT/ASS.
"""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,math,re,sys,time,subprocess,os
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=H/'local/final-audio'
SOURCE=H/'narration/source-verified-revisions.json';TIMING=H/'baseline-sentence-timing.json';RATE=48000;SPF=800
sys.dont_write_bytecode=True
sys.path.insert(0,str(R/'projects/animation-breaking-down-attack-animations/production/grid-v1'))
import caption_pipeline as cp

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);value=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if p.exists()and p.read_text('utf8')==value:return
    pending=p.with_suffix(p.suffix+'.'+str(os.getpid())+'.pending');pending.write_text(value,'utf8');replace_atomic(pending,p)

def replace_atomic(source,destination):
    for attempt in range(50):
        try:os.replace(source,destination);return
        except PermissionError:
            if attempt==49:raise
            time.sleep(.1)

def save_mix(p,data):
    """Keep unchanged published mix bytes/mtime; replace changed candidates atomically."""
    p=Path(p);serialized=np.asarray(data,dtype=np.float32)
    if p.exists():
        info=sf.info(p)
        if(info.samplerate==RATE and info.subtype=='FLOAT'and info.channels==serialized.shape[1]and info.frames==len(serialized)):
            existing,_=sf.read(p,dtype='float32',always_2d=True)
            # libsndfile FLOAT WAV PEAK chunks contain wall-clock timestamps.
            # Compare the serialized sample values before writing any new WAV;
            # byte comparison after rewriting would churn otherwise equal mixes.
            if np.array_equal(existing,serialized):return
    pending=p.with_suffix('.'+str(os.getpid())+'.pending.wav');sf.write(pending,serialized,RATE,subtype='FLOAT');replace_atomic(pending,p)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p):return Path(p).absolute().relative_to(R).as_posix()
def norm(s):return ''.join(c.lower()for c in s if c.isalnum())
def nonspace(s):return ''.join(s.split())
def text(s):return ' '.join(s['lines'])
def auth():
    c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert c['fullLocalProductionAuthorized']and c['renderAuthorized'];return c
def all_changes(source,e):return e['changes']+[x for x in source['existingApprovedChanges']if x['episode']==e['id']]

def compose_sample_maps(first,second):
    """Compose source->middle and middle->destination, all half-open samples."""
    result=[]
    for b in second:
        for a in first:
            lo=max(a['outputStart'],b['sourceStart']);hi=min(a['outputStart']+a['samples'],b['sourceStart']+b['samples'])
            if lo<hi:result.append({'sourceStart':a['sourceStart']+lo-a['outputStart'],
                'outputStart':b['outputStart']+lo-b['sourceStart'],'samples':hi-lo})
    return sorted(result,key=lambda x:x['outputStart'])

def a01_stems():
    """No separation. Reuse processed voice samples only in known old-game spans."""
    auth();p=R/'projects/animation-assigning';grid=p/'production/local/grid-v1/edit';dest=L/'A01/stems';dest.mkdir(parents=True,exist_ok=True)
    original=read(grid/'audio-build.json');voice=grid/'narration-stem.wav';music=grid/'music-stem.wav';game=grid/'game-stem.wav';mix=p/'production/local/relations-v4/mix.wav'
    for file in (voice,music,game):
        expected=next(x['sha256']for x in original['outputs']if Path(x['path']).name==file.name);assert sha(file)==expected
    files=[grid/'audio-build.json',voice,music,game,p/'production/local/unreal-kit-v2/timeline.json',p/'production/local/pacing-v3/audio-proof.json',p/'production/local/relations-v4/opening-edl.json']
    ducked=dest/'grid-music-ducked.wav';receipt=dest/'grid-music-ducked.json'
    graph='[0:a][1:a]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[out]'
    signature={'voice':sha(voice),'music':sha(music),'filter':graph,'output':'48k stereo FLOAT; no final shared limiter'}
    if not(ducked.exists()and receipt.exists()and read(receipt).get('inputs')==signature and read(receipt).get('sha256')==sha(ducked)):
        subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(music),'-i',str(voice),'-filter_complex_threads','1','-filter_complex',graph,
            '-map','[out]','-ar','48000','-ac','2','-c:a','pcm_f32le','-threads','4',str(ducked)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        save(receipt,{'inputs':signature,'sha256':sha(ducked)})
    timeline=read(files[4]);pacing=read(files[5]);opening=read(files[6]);assert pacing['preservationMode']=='preserve-final-mix'
    edges=[]
    for c in timeline['segments']:
        if c['kind']!='added':continue
        for label,start in [('start',c['oldStart']*SPF),('end',c['oldEnd']*SPF-1440)]:
            x=read_segment(game,start,start+1440);count=int(np.count_nonzero(x));assert count==0,'Added boundary carries old game audio; extend the proven remapping before use'
            edges.append({'voice':c['voice'],'side':label,'gridStartSample':start,'samples':1440,'oldGameNonzeroSamples':count})
    first=[{'sourceStart':c['oldStart']*SPF,'outputStart':c['start']*SPF,'samples':c['frames']*SPF}for c in timeline['segments']if c['kind']!='added']
    second=[{'sourceStart':x['oldStartSample'],'outputStart':x['newStartSample'],'samples':x['oldEndSample']-x['oldStartSample']}for x in pacing['segments']]
    third=[{'sourceStart':x['sourceStartSample'],'outputStart':x['outputStartSample'],'samples':x['samples']}for x in opening['audioEdl']if x['kind']=='baseline']
    mapped=compose_sample_maps(compose_sample_maps(first,second),third)
    audio_plan=read(R/original['inputs']['plan']['path']);assert sha(R/original['inputs']['plan']['path'])==original['inputs']['plan']['sha256']
    enabled={x['cut']for x in original['gameAudio']};cuts=[x for x in audio_plan['cuts']if x['id']in enabled]
    ranges=[]
    for m in mapped:
        for c in cuts:
            lo=max(m['sourceStart'],c['startFrame']*SPF);hi=min(m['sourceStart']+m['samples'],c['endFrame']*SPF)
            if lo<hi:ranges.append({'id':'A01-old-game-'+c['id']+'-'+str(lo),'oldGameCutId':c['id'],'gridSourceStartSample':lo,
                'startSample':m['outputStart']+lo-m['sourceStart'],'endSample':m['outputStart']+hi-m['sourceStart'],'samples':hi-lo})
    ranges.sort(key=lambda x:x['startSample']);assert all(a['endSample']<=b['startSample']for a,b in zip(ranges,ranges[1:]))
    # This candidate is not the final master. Outside its proven ranges every
    # original current sample is retained. Caller selects exact audio overrides.
    candidate=dest/'relations-old-game-clean-candidate.wav';evidence=[];cursor=0
    with sf.SoundFile(mix)as source,sf.SoundFile(candidate,'w',samplerate=RATE,channels=2,subtype='FLOAT')as output:
        assert source.samplerate==RATE and source.channels==2
        for q in ranges:
            n=q['startSample']-cursor
            if n:source.seek(cursor);output.write(source.read(n,dtype='float32',always_2d=True))
            start=q['gridSourceStartSample'];vo=read_segment(voice,start,start+q['samples']);bed=read_segment(ducked,start,start+q['samples']);new=vo+bed
            assert float(np.max(abs(new)))<.98,'Clean source mix needs a reviewed bed-level adjustment, not voice limiting'
            output.write(new);cursor=q['endSample'];evidence.append({**q,'voicePcmSourceSha256':sha(voice),'processedVoiceCopiedWithoutGainOrSpeedChange':True,
                'musicPcmSourceSha256':sha(ducked),'peak':float(np.max(abs(new))),'newSamples':q['samples'],'source':rel(candidate),'sourceStartSample':q['startSample'],
                'audioKind':'complete-mix','sourceVerified':False,'status':'candidate-source-ancestry-proven-listening-and-final-game-scope-review-pending'})
        source.seek(cursor);output.write(source.read(dtype='float32',always_2d=True))
    # Serialize/re-read proof of unchanged complement, not merely a hash promise.
    preserved=0;cursor=0
    with sf.SoundFile(mix)as old,sf.SoundFile(candidate)as new:
        for end,nextcursor in [(q['startSample'],q['endSample'])for q in ranges]+[(old.frames,old.frames)]:
            old.seek(cursor);new.seek(cursor)
            while cursor<end:
                count=min(480000,end-cursor);assert np.array_equal(old.read(count,dtype='float32'),new.read(count,dtype='float32'));cursor+=count;preserved+=count
            cursor=nextcursor
    info={'episode':'A01','status':'exact-stem-ancestry-candidate-not-final-mix','baselineMixSha256':sha(mix),'source':rel(candidate),'sourceSha256':sha(candidate),
        'sources':[{'path':rel(x),'sha256':sha(x)}for x in files], 'ranges':evidence,'retainedGridToRelationsMappings':mapped,'untouchedSamplesExact':preserved,
        'addedBoundaryCrossfadeGameChecks':edges,
        'voiceMethod':'Copy original processed narration-stem sample slices unchanged; use original music-stem with the identical narration sidechain. No source separator.',
        'limitations':['Original shared final limiter is intentionally not recreated; the sum dynamics can differ in these changed source-audio ranges.',
            'UE-added passages and relationships are preserved from current mix; no old-game claim is made outside exact retained grid ranges.',
            'Caller must merge ranges with changed-speech intervals and new-game audio before assembly; overlapping audio edits must not be submitted.'],
        'humanListening':False,'newTtsGenerated':False,'sourceSeparationUsed':False}
    save(dest/'stem-remap.json',info);print('A01 candidate ranges',len(ranges),'unchanged samples',preserved)
def cues(p):
    def sec(t):
        h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
    result=[]
    for block in re.split(r'\n\s*\n',Path(p).read_text('utf-8-sig').strip()):
        lines=block.splitlines();a,b=map(sec,lines[1].split(' --> '));result.append({'start':a,'end':b,'text':'\n'.join(lines[2:])})
    return result

def scripts():
    source=read(SOURCE);control=auth();report=[]
    for e in source['episodes']:
        assert e['id']in control['episodes']and e['id']!='A03';base={}
        for lang in ('ko','en'):
            f=R/e['baseline'][lang]['path'];assert sha(f)==e['baseline'][lang]['sha256'];base[lang]=read(f)
        ko={s['id']:s for s in base['ko']['scenes']};en={s['id']:s for s in base['en']['scenes']}
        alignment=source['englishAlignment'].get(e['id'],{}).get('mapping',[{'koId':x,'enIds':[x]}for x in ko])
        used=[v for a in alignment for v in a['enIds']];assert used==list(en),'Each original EN row must occur exactly once in order'
        mapped={a['koId']:{'id':a['koId'],'title':en[a['enIds'][0]]['title'],'lines':[' '.join(text(en[v])for v in a['enIds'])]}for a in alignment}
        assert list(mapped)==list(ko)
        changes={x['id']:x for x in all_changes(source,e)};assert len(changes)==len(all_changes(source,e))
        outko=deepcopy(base['ko']);outen=deepcopy(base['en']);outen['scenes']=list(deepcopy(mapped).values())
        checks=[]
        for ks,es in zip(outko['scenes'],outen['scenes']):
            sid=ks['id'];c=changes.get(sid)
            if c:
                assert c['sourceVerified']and c['completeKoEnReadThrough']
                assert text(ks)==c['baselineKoText'];assert text(es)==c['baselineEnText']
                ks['lines']=[c['ko']];es['lines']=[c['en']]
            else:assert ks==ko[sid]and es==mapped[sid]
            checks.append({'id':sid,'changed':bool(c),'koPreserved':not c,'enPreservedAfterSemanticIdAlignment':not c})
        dest=R/'projects'/e['slug']/'production/contrast-v5';save(dest/'final.ko.json',outko);save(dest/'final.en.json',outen)
        report.append({'id':e['id'],'slug':e['slug'],'changedIds':list(changes),'unchanged':len(ko)-len(changes),'sentences':len(ko),
            'allOriginalEnglishRowsUsedExactlyOnceBeforeChanges':True,'unchangedKoAndAlignedEnglishExact':True,
            'koSha256':sha(dest/'final.ko.json'),'enSha256':sha(dest/'final.en.json'),'checks':checks})
    save(L/'script-preservation.json',{'sourceSha256':sha(SOURCE),'status':'all-reviewed-changes-applied-other-text-exact','episodes':report,'ttsStarted':False})
    return source,report

def read_segment(file,a,b):
    with sf.SoundFile(file)as f:
        assert f.samplerate==RATE;f.seek(max(0,a));return f.read(max(0,b-a),dtype='float32',always_2d=True)
def rms(a):return float(np.sqrt(np.mean(np.square(a,dtype=np.float64))))if len(a)else 0.
def windows(a,size=480):
    count=len(a)//size
    return np.sqrt(np.mean(a[:count*size].reshape(count,size,-1).astype(np.float64)**2,axis=(1,2)))if count else np.array([0.])
def valley(file,lo,hi,preferred,fallback):
    if hi<=lo:return int(fallback),{'method':'no-inter-sentence-gap; retain exact existing cue edge','needsListening':True,'fallbackSample':int(fallback)}
    a=read_segment(file,lo,hi);w=windows(a);positions=lo+np.arange(len(w))*480+240
    score=w/(max(float(np.median(w)),1e-7))+.08*np.abs(positions-preferred)/max(480,hi-lo)
    i=int(np.argmin(score));point=int(np.clip(positions[i],lo,hi))
    return point,{'method':'minimum10ms-RMS-inside-caption-gap','candidateRmsDbfs':20*math.log10(max(w[i],1e-9)),
        'searchSamples':[lo,hi],'needsListening':True,'asrConfirmed':False}

def take_file(ep,c):
    if ep=='A10':return H/'local/voice/chunks'/f'A10S{c["id"]}-scene.wav'
    spoken=c.get('spokenKo',c['ko']);key=ep+'S'+c['id']+'X'+hashlib.sha256(spoken.encode()).hexdigest()[:10]
    return H/'local/voice-reviewed/chunks'/(key+'-scene.wav')
def take_data(file):
    if not file.exists()or time.time()-file.stat().st_mtime<3:return None
    # Generation writes candidate WAVs before tail checks/retries finish. A
    # stable mtime alone is not evidence of the selected final take.
    logs=[H/'local/tts-cpu.log']if file.name.startswith('A10S')else[H/'local'/name for name in
        ('tts-reviewed-cpu.log','tts-reviewed-final.log','tts-reviewed-final-cpu-fallback.log','tts-reviewed-final-gpu.log')]
    completion=None
    for log in sorted([p for p in logs if p.exists()],key=lambda p:p.stat().st_mtime):
        lines=[line for line in log.read_text('utf8',errors='replace').splitlines()if re.match(r'^(Rendered|Checked) '+re.escape(file.stem)+r'\b',line)]
        if lines:
            completion={'log':rel(log),'line':lines[-1]}
    if completion is None or not completion['line'].startswith('Rendered '):return None
    a,sr=sf.read(file,dtype='float32',always_2d=True);assert len(a)>sr*.15 and np.isfinite(a).all()and np.max(abs(a))<1
    if sr!=RATE:
        g=math.gcd(sr,RATE);a=resample_poly(a,RATE//g,sr//g,axis=0).astype(np.float32)
    if a.shape[1]==1:a=np.repeat(a,2,axis=1)
    assert a.shape[1]==2
    env=windows(a);threshold=max(.0002,float(np.percentile(env,90))*.04);active=np.flatnonzero(env>threshold)
    assert len(active)
    return a,{'path':rel(file),'sha256':sha(file),'sourceRate':sr,'sourceFrames':sf.info(file).frames,'resampledFrames':len(a),
        'speechEnvelopeCandidateSamples':[int(active[0]*480),min(len(a),int((active[-1]+1)*480))],
        'method':'waveform activity only; not word recognition','fullTakeRetained':True,'speed':1.0,'asrConfirmed':False,'finalRenderedEvidence':completion}

def groups_for(e,source,timing):
    cs={c['id']:c for c in all_changes(source,e)};out=[]
    for i,s in enumerate(timing['sentences']):
        if s['id']not in cs:continue
        item={'timing':s,'change':cs[s['id']],'index':i}
        if out and i==out[-1][-1]['index']+1 and s['startSeconds']-out[-1][-1]['timing']['endSeconds']<=.9:out[-1].append(item)
        else:out.append([item])
    return out

def background(p,base_mix,start,n):
    pacing=read(p/'production/pacing-v3/edit-plan.json');bed=R/pacing['music'];a,sr=sf.read(bed,dtype='float32',always_2d=True)
    assert sr==RATE and a.shape[1]==2
    opening=read(p/'production/local/relations-v4/opening-edl.json');music=[x for x in opening['audioEdl']if x['kind']=='music-replay'and x['samples']>12000]
    if music:
        q=music[0];target=rms(read_segment(base_mix,q['outputStartSample']+2400,q['outputEndSample']-2400));method='RMS of proven current music-only replay'
    elif pacing.get('audioMode')!='preserve-final-mix':
        # A02 pacing-v3 decodes the raw song, then normalizes the in-memory bed
        # to -28 dB RMS before the recorded master gain. The decoded file itself
        # is not a pre-normalized stem; using its raw RMS would raise BGM ~15dB.
        target=10**(-28/20)*float(pacing['masterGain']);method='pacing-v3/render.py original raw-song normalization: -28 dB RMS then recorded masterGain'
    else:target=rms(a)*float(pacing.get('masterGain',1.));method='existing prepared music stem and recorded masterGain'
    index=(np.arange(n)+start)%len(a);out=a[index].copy();gain=target/max(rms(a),1e-7);out*=gain
    return out,{'path':rel(bed),'sha256':sha(bed),'gain':gain,'method':method,'targetRmsDbfs':20*math.log10(max(target,1e-9))}

def prepare(selected=None):
    source,_=scripts();timings={e['id']:e for e in read(TIMING)['records']};bases={r['id']:r for r in read(H/'baseline-review-manifest.json')['records']};episodes=[]
    for e in source['episodes']:
        if selected and e['id']not in selected:continue
        p=R/'projects'/e['slug'];local=L/e['id'];local.mkdir(parents=True,exist_ok=True);mix=p/'production/local/relations-v4/mix.wav';base=bases[e['id']]
        assert sha(mix)==base['audioProof']['mixSha256'];sentences=timings[e['id']]['sentences'];rows=[]
        for group in groups_for(e,source,timings[e['id']]):
            first,last=group[0]['timing'],group[-1]['timing'];a=int(round(first['startSeconds']*RATE));b=int(round(last['endSeconds']*RATE));i,j=group[0]['index'],group[-1]['index']
            prior=int(round(sentences[i-1]['endSeconds']*RATE))if i else 2*RATE
            following=int(round(sentences[j+1]['startSeconds']*RATE))if j+1<len(sentences)else (base['frames']-600)*SPF
            start,sv=valley(mix,max(prior+480 if i else prior,a-8640),a,a-2400,a)
            end,ev=valley(mix,b,min(following-480,b+9600),b+2400,b)
            assert start>=2*RATE and end<=(base['frames']-600)*SPF,'Protect original branding and membership PCM'
            gid=e['id']+'-speech-'+first['id']+('-'+last['id']if last['id']!=first['id']else'')
            takes=[take_data(take_file(e['id'],x['change']))for x in group]
            row={'id':gid,'sentenceIds':[x['timing']['id']for x in group],'startSample':start,'endSample':end,'baselineStartFrame':start//SPF,
                'baselineEndFrame':math.ceil(end/SPF),'oldCueStartIndex':first['cueStartIndex'],'oldCueEndIndexExclusive':last['cueEndIndexExclusive'],
                'boundaryReview':{'start':sv,'end':ev,'status':'waveform-candidates-human-and-ASR-review-pending'},'status':'waiting-for-takes','takes':[]}
            missing=[rel(take_file(e['id'],x['change']))for x,t in zip(group,takes)if t is None]
            if missing:row['missing']=missing;rows.append(row);continue
            prefix=2880;suffix=5760;parts=[];placements=[];cursor=prefix
            for k,(item,take)in enumerate(zip(group,takes)):
                data,info=take;parts.append(data);placements.append({'sentenceId':item['timing']['id'],'offsetSample':cursor,'samples':len(data),'ko':item['change']['ko'],'en':item['change']['en'],'take':info});cursor+=len(data)
                if k<len(group)-1:
                    gap=min(.3,max(.15,group[k+1]['timing']['startSeconds']-item['timing']['endSeconds']));cursor+=round(gap*RATE)
            need=cursor+suffix;old=end-start;delta=math.ceil(max(0,need-old)/SPF);n=old+delta*SPF
            bed,bedproof=background(p,mix,start,n);voice=np.zeros_like(bed)
            for place,part in zip(placements,parts):voice[place['offsetSample']:place['offsetSample']+len(part)]+=part
            oldenv=windows(read_segment(mix,a,b));newenv=windows(voice);oldactive=oldenv[oldenv>=np.percentile(oldenv,60)];newactive=newenv[newenv>=max(.001,float(np.percentile(newenv,60)))]
            target=float(np.median(oldactive));current=float(np.median(newactive));gain=float(np.clip(target/max(current,1e-7),.5,2.))
            output=bed+voice*gain;peak=float(np.max(abs(output)));scale=min(1.,.94/max(peak,.001));output*=scale
            # Six-millisecond joins affect the newly made gap/bed only. Full raw
            # takes start60ms later and end at least120ms before the output edge.
            fade=288;ramp=np.linspace(0,1,fade)[:,None]
            left=read_segment(mix,start-1,start)[0];right=read_segment(mix,end,end+1)[0]
            # Match the adjacent preserved sample only in the new music-only
            # padding. This avoids a zero-to-BGM step without importing old speech.
            output[:fade]=left*(1-ramp)+output[:fade]*ramp
            output[-fade:]=output[-fade:]*(1-ramp)+right*ramp
            file=local/(gid+'.wav');save_mix(file,output)
            row.update(status='complete-mix-prepared-review-pending',newSamples=n,deltaFrames=delta,source=rel(file),sourceSha256=sha(file),
                sourceStartSample=0,audioKind='complete-mix',sourceVerified=False,placements=placements,bed=bedproof,voiceGain=gain,peakScale=scale,
                fullTakeUncut=True,speed=1.0,activeVoiceTargetRmsDbfs=20*math.log10(max(target,1e-9)),asrWordAlignmentConfirmed=False)
            row['newPaddingBoundaryBridge']={'samples':fade,'milliseconds':6,'method':'Linear endpoint-continuity bridge in new music padding only; no voice samples faded','oldAdjacentSamples':[left.tolist(),right.tolist()]}
            row['extensionRequirement']={'oldRelationRangeFrames':[row['baselineStartFrame'],row['baselineEndFrame']],'deltaFrames':delta,
                'requiredPictureFrames':row['baselineEndFrame']-row['baselineStartFrame']+delta,'audioRangeSamples':[start,end],
                'note':'Same-length passage if delta0. Otherwise prepare a picture passage; do not speed up narration or assume repeated motion.'}
            rows.append(row)
        out={'id':e['id'],'slug':e['slug'],'sourceRevisionsSha256':sha(SOURCE),'baselinePcmSha256':sha(mix),'groups':rows,
            'unchangedPcmPolicy':'Only these exact sample ranges may change. Parent-provided game-audio additions require their own explicit ranges/stem evidence.',
            'originalGameAudioEvidence':('A04–A18 assemble_episode.py mix() contains narration + Nimbus Eveningland, no game stem.'if int(e['id'][1:])>=4 else
                'A02 fighters-v4 build_revision reconstructs voice + Nimbus and explicitly mutes old game sources.'if e['id']=='A02'else
                'A01 exact processed-stem alternative exists in local/final-audio/A01/stems/stem-remap.json; caller applies only authorized source-audio ranges.'),
            'wordAlignmentStatus':'No ASR. Only expected phrase text and waveform silence are available; review required.'}
        save(local/'audio-plan.json',out);episodes.append(out)
    if selected and (L/'audio-preparation.json').exists():
        prior=read(L/'audio-preparation.json')
        if prior['sourceSha256']==sha(SOURCE):episodes+=[e for e in prior['episodes']if e['id']not in selected]
        episodes.sort(key=lambda e:e['id'])
    save(L/'audio-preparation.json',{'sourceSha256':sha(SOURCE),'episodes':episodes,'ttsStarted':False,'fullEpisodeMixesCreated':False})
    save(L/'extension-requirements.json',{'clock':'relations-v4','episodes':[{'id':e['id'],'requirements':[{'id':g['id'],**g['extensionRequirement']}for g in e['groups']if g.get('deltaFrames',0)>0]}for e in episodes],
        'pendingTakeGroups':[g['id']for e in episodes for g in e['groups']if g['status']=='waiting-for-takes']})
    print('Prepared',sum('source'in g for e in episodes for g in e['groups']),'groups; waiting',sum(g['status']=='waiting-for-takes'for e in episodes for g in e['groups']))
    return episodes

def split_expected(s,limit):
    # These are draft text chunks, not semantically approved bilingual clauses.
    words=s.split();out=[];part=[]
    for word in words:
        if part and len(nonspace(' '.join(part+[word])))>limit:out.append(' '.join(part));part=[]
        part.append(word)
        if re.search(r'[,.!?;:]$',word)and len(nonspace(' '.join(part)))>=max(8,limit//3):out.append(' '.join(part));part=[]
    if part:out.append(' '.join(part))
    assert nonspace(''.join(out))==nonspace(s);return out

def cue_boundaries(data,parts,active):
    weights=np.array([len(nonspace(s))for s in parts]);total=weights.sum();lo,hi=active;bounds=[lo];env=windows(data)
    for fraction in np.cumsum(weights)[:-1]/total:
        center=lo+(hi-lo)*fraction;aa=max(bounds[-1]+2400,int(center-7200));bb=min(hi-2400,int(center+7200))
        candidates=np.arange(max(0,aa//480),min(len(env),bb//480)+1);candidates=candidates[candidates<len(env)]
        if not len(candidates):point=max(bounds[-1]+1,min(hi-1,round(center)))
        else:
            score=env[candidates]/max(float(np.percentile(env,80)),1e-7)+.4*np.abs(candidates*480-center)/7200;point=int(candidates[np.argmin(score)]*480)
        bounds.append(point)
    bounds.append(hi);assert all(a<b for a,b in zip(bounds,bounds[1:]));return bounds

def actual_clause_intervals(ep,placement,parts,data):
    """Only exact or explicitly text-reviewed independent ASR may drive cues."""
    take=placement['take'];folder=H/'local/asr-changed';matches=[]
    current=R/take['path']
    if not current.exists()or sha(current)!=take['sha256']:
        active=[placement['offsetSample']+x for x in take['speechEnvelopeCandidateSamples']];bounds=cue_boundaries(data,parts,active)
        return list(zip(bounds,bounds[1:])),{'method':'provisional stale-take fallback; rebuild before use','asrConfirmed':False,
            'fallbackReason':'Coordinator replaced the source WAV; this prepared mix is obsolete','humanListening':False}
    for file in (folder/'raw').glob('*.json')if(folder/'raw').exists()else[]:
        raw=read(file)
        if raw['audio_sha256']==take['sha256']and raw['episode']==ep and raw['sentenceId']==placement['sentenceId']:matches.append((file,raw))
    reason='Matching independent word ASR not available'
    if matches:
        file,raw=matches[-1];aliases={};approved=norm(raw['text'])==norm(placement['ko']);reviewfile=folder/'text-review.json'
        if not approved and reviewfile.exists():
            review=read(reviewfile);r=next((x for x in review['entries']if x['episode']==ep and x['sentenceId']==placement['sentenceId']and x['audioSha256']==take['sha256']),None)
            if r and r.get('acceptedForCaptionAlignment')is True:approved=True;aliases=r.get('alignmentAliases',{})
        if approved:
            try:
                starts,ends,proof=cp.align_characters(placement['ko'],raw['chunks'],raw['duration'],aliases,.96)
                cursor=0;intervals=[]
                for p in parts:
                    count=len(cp.normalized(p,aliases));a=starts[cursor];b=ends[cursor+count-1];cursor+=count
                    intervals.append((placement['offsetSample']+round(a*RATE),placement['offsetSample']+round(b*RATE)))
                assert cursor==len(starts)and all(a<b for a,b in intervals)
                return intervals,{'method':'independent ASR word endpoints; character interpolation only within recognized words and explicitly recorded matched-character gaps',
                    'asrConfirmed':True,'asrPath':rel(file),'asrSha256':sha(file),'audioSha256':take['sha256'],'alignment':proof,'aliases':aliases,'humanListening':False}
            except (ValueError,AssertionError,IndexError)as error:reason='Word alignment validation pending: '+str(error)
        else:reason='Independent ASR differs from expected text; semantic difference review pending'
    active=[placement['offsetSample']+x for x in take['speechEnvelopeCandidateSamples']];bounds=cue_boundaries(data,parts,active)
    return list(zip(bounds,bounds[1:])),{'method':'expected paired clauses + low-energy valley candidates','asrConfirmed':False,'fallbackReason':reason,'humanListening':False}

def align_ready():
    """Export current take-local semantic clause times without a final picture."""
    clauses=read(L/'caption-clauses.json');assert clauses['sourceRevisionsSha256']==sha(SOURCE)
    lookup={(q['episode'],q['sentenceId']):q for q in clauses['scenes']};entries=[];prepared=read(L/'audio-preparation.json')
    assert prepared['sourceSha256']==sha(SOURCE)
    for episode in prepared['episodes']:
        current_plan=read(L/episode['id']/'audio-plan.json')
        episode['groups']=current_plan['groups']
        for group in episode['groups']:
            if 'source'not in group:continue
            assert sha(R/group['source'])==group['sourceSha256'];data,_=sf.read(R/group['source'],dtype='float32',always_2d=True)
            for place in group['placements']:
                pairs=lookup[(episode['id'],place['sentenceId'])]['parts'];intervals,proof=actual_clause_intervals(episode['id'],place,[p['ko']for p in pairs],data)
                entries.append({'episode':episode['id'],'sentenceId':place['sentenceId'],'groupId':group['id'],'takeSha256':place['take']['sha256'],
                    'groupSourceSha256':group['sourceSha256'],'placementOffsetSample':place['offsetSample'],**proof,
                    'clauses':[{'ko':p['ko'],'en':p['en'],'groupStartSample':a,'groupEndSample':b,
                        'takeStartSeconds':(a-place['offsetSample'])/RATE,'takeEndSeconds':(b-place['offsetSample'])/RATE}for p,(a,b)in zip(pairs,intervals)]})
            verified=[x for x in entries if x['episode']==episode['id']and x['groupId']==group['id']]
            problems=[];inputs=[]
            if len(verified)!=len(group['placements'])or not all(x['asrConfirmed']for x in verified):problems.append('One or more complete passages lack accepted independent ASR text/word alignment')
            for place in group['placements']:
                current=take_data(R/place['take']['path'])
                if current is None or current[1]['sha256']!=place['take']['sha256']:problems.append('Take is active, incomplete or changed: '+place['sentenceId'])
                inputs.append({'path':place['take']['path'],'sha256':place['take']['sha256']})
                if not(place['offsetSample']>=2880 and place['offsetSample']+place['samples']<=group['newSamples']-5760):problems.append('Full take exceeds protected new padding')
            if not(group['fullTakeUncut']and group['speed']==1.0):problems.append('Voice duration policy failed')
            if not np.isfinite(data).all()or float(np.max(abs(data)))>=.99:problems.append('Nonfinite or clipping mixed PCM')
            if len(data)!=group['newSamples']or len(data)-(group['endSample']-group['startSample'])!=group['deltaFrames']*SPF:problems.append('Sample/frame delta mismatch')
            baseline=R/'projects'/episode['slug']/'production/local/relations-v4/mix.wav'
            left=read_segment(baseline,group['startSample']-1,group['startSample'])[0];right=read_segment(baseline,group['endSample'],group['endSample']+1)[0]
            steps=[float(np.max(abs(data[0]-left))),float(np.max(abs(data[-1]-right)))]
            if max(steps)>.002:problems.append('New padding join step requires a reviewed bridge')
            proof={'scope':'Technical verification of this complete replacement mix; not human listening or final encoded delivery',
                'allPassagesIndependentAsrTextAccepted':not any(not x['asrConfirmed']for x in verified),'asrRecords':[{'sentenceId':x['sentenceId'],
                    'audioSha256':x['takeSha256'],'asrPath':x.get('asrPath'),'asrSha256':x.get('asrSha256'),'alignment':x.get('alignment'),'aliases':x.get('aliases',{})}for x in verified],
                'fullTakesUncut':group['fullTakeUncut'],'voiceSpeed':group['speed'],'sourceRevisionsSha256':sha(SOURCE),
                'mixSha256':group['sourceSha256'],'sampleRate':RATE,'samples':len(data),'samplePeak':float(np.max(abs(data))),
                'adjacentPreservedSampleSteps':steps,'brandingProtected':group['startSample']>=96000,'inputChecks':inputs,
                'problems':problems,'humanListening':False,'humanReviewed':False,'finalEncodedReview':False,
                'outsideRangePolicy':'Assembly must retain the exact baseline complement; no full master has been created by this verifier.'}
            group['technicalMixVerified']=not problems;group['technicalMixVerification']=proof;group['humanReviewed']=False
            group['sourceVerified']=not problems
            group['status']='complete-mix-technically-verified-local-review-pending'if not problems else'complete-mix-prepared-review-pending'
            group['inputChecks']=inputs
        current_plan['groups']=episode['groups'];save(L/episode['id']/'audio-plan.json',current_plan)
    save(L/'audio-preparation.json',prepared)
    save(L/'word-alignment.json',{'sourceRevisionsSha256':sha(SOURCE),'captionClausesSha256':sha(L/'caption-clauses.json'),
        'status':'incremental-word-alignment-with-explicit-fallbacks','entries':entries,'wordAlignedPassages':sum(x['asrConfirmed']for x in entries),
        'fallbacks':[{'episode':x['episode'],'sentenceId':x['sentenceId'],'reason':x['fallbackReason']}for x in entries if not x['asrConfirmed']],
        'humanListening':False,'GPUUsed':False})
    print('Word-aligned',sum(x['asrConfirmed']for x in entries),'of',len(entries),'prepared passages')

def captions(ep,assembly):
    source=read(SOURCE);e=next(x for x in source['episodes']if x['id']==ep);audio=read(L/ep/'audio-plan.json');assert audio['sourceRevisionsSha256']==sha(SOURCE)
    assert all(g['status']!='waiting-for-takes'for g in audio['groups']),'Do not publish captions with missing changed speech'
    edit=read(assembly);assert edit['id']==ep;audioedl=edit['audioEdl'];changes=audio['groups'];base=next(x for x in read(H/'baseline-review-manifest.json')['records']if x['id']==ep)
    clauses=read(L/'caption-clauses.json');assert clauses['sourceRevisionsSha256']==sha(SOURCE)
    clausemap={(q['episode'],q['sentenceId']):q for q in clauses['scenes']}
    def mapped(sample):
        owners=[]
        for r in audioedl:
            if r['kind']=='preserve':start=r['sourceStartSample'];end=start+r['samples']
            elif r['samples']==r['endSample']-r['startSample']:start,end=r['startSample'],r['endSample']
            else:continue
            if start<=sample<=end:owners.append((r,start))
        assert owners,('Unchanged caption endpoint is not in preserved PCM',sample)
        r,start=owners[-1];return (r['outputStartSample']+sample-start)/RATE
    folder=L/ep/'captions';folder.mkdir(exist_ok=True);review=[];font=cp.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),500);bold=cp.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),700)
    for lang in ('ko','en'):
        old=cues(R/next(x['path']for x in base['files']if x['kind']==lang+'.srt'));result=[]
        for c in old:
            a,b=round(c['start']*RATE),round(c['end']*RATE)
            hit=[g for g in changes if max(a,g['startSample'])<min(b,g['endSample'])]
            if hit:
                assert len(hit)==1 and a>=hit[0]['startSample']-480 and b<=hit[0]['endSample']+480,'Splice bisects an unchanged subtitle'
            else:result.append({'start':mapped(a),'end':mapped(b),'text':c['text'],'preservedText':True,'oldStart':c['start'],'oldEnd':c['end']})
        for g in changes:
            owners=[r for r in audioedl if r.get('id')in (g['id'],g['id']+'-audio')]
            assert len(owners)==1,('Expected one changed-speech audio edit',g['id'])
            placed=owners[0];assert placed['source']==g['source']and placed['samples']==g['newSamples']
            data,_=sf.read(R/g['source'],dtype='float32',always_2d=True)
            for q in g['placements']:
                authored=clausemap[(ep,q['sentenceId'])];parts=[p[lang]for p in authored['parts']]
                assert nonspace(''.join(parts))==nonspace(q[lang]),'Authored clauses must preserve original text'
                # English uses the same semantic units/times as the Korean voice.
                intervals,alignment=actual_clause_intervals(ep,q,[p['ko']for p in authored['parts']],data)
                for i,s in enumerate(parts):
                    wrapped=cp.wrap(s,font);assert wrapped is not None
                    result.append({'start':(placed['outputStartSample']+intervals[i][0])/RATE,'end':(placed['outputStartSample']+intervals[i][1])/RATE,
                        'text':'\n'.join(wrapped),'preservedText':False,'sentenceId':q['sentenceId']})
                review.append({'language':lang,'sentenceId':q['sentenceId'],'parts':parts,**alignment,
                    'semanticBilingualClauseReview':'model text review; linked phrase-order exceptions recorded',
                    'adjacentCueGroup':authored['adjacentCueGroup'],'listening':'pending'})
        result.sort(key=lambda c:c['start']);assert all(a['end']<=b['start']+.002 for a,b in zip(result,result[1:])),(ep,lang,'Caption overlap')
        # Old EN SRTs sometimes use an unwrapped single line. Preserve their
        # words/times while wrapping for actual fixed-font ASS geometry.
        if lang=='en':
            for c in result:
                lines=cp.wrap(' '.join(c['text'].split()),font);assert lines is not None,(ep,lang,c)
                c['text']='\n'.join(lines)
        expected=read(R/'projects'/e['slug']/'production/contrast-v5'/f'final.{lang}.json')
        assert norm(''.join(c['text']for c in result))==norm(''.join(text(s)for s in expected['scenes'])),(ep,lang,'Caption content mismatch')
        (folder/f'captions.provisional.{lang}.srt').write_text(''.join(f'{i+1}\n{cp.srt_stamp(c["start"])} --> {cp.srt_stamp(c["end"])}\n{c["text"]}\n\n'for i,c in enumerate(result)),'utf8')
        events=[];oldass={}
        if lang=='ko':
            oldfile=R/'projects'/e['slug']/'production/local/relations-v4/captions.ass'
            def seconds(stamp):
                h,m,s=stamp.split(':');return int(h)*3600+int(m)*60+float(s)
            for line in oldfile.read_text('utf-8-sig').splitlines():
                if not line.startswith('Dialogue:'):continue
                fields=line.split(',',9);key=(round(seconds(fields[1])*100),round(seconds(fields[2])*100));oldass.setdefault(key,[]).append(fields)
        exacteventgroups=0
        for c in result:
            key=(round(c.get('oldStart',-1)*100),round(c.get('oldEnd',-1)*100))
            if c['preservedText']and key in oldass:
                for fields in oldass[key]:
                    values=fields.copy();values[1]=cp.ass_stamp(c['start']);values[2]=cp.ass_stamp(c['end'])
                    events.append(','.join(values)+'\n')
                exacteventgroups+=1;continue
            row={'start':c['start'],'end':c['end'],lang:c['text'],'emphasis':{lang:None}}
            events.append(cp.ass_events(row,cp.geometry(c['text'],font,bold,None),lang))
        (folder/f'captions.provisional.{lang}.ass').write_text(cp.ass_header('Noto Sans KR')+''.join(events),'utf8')
        save(folder/f'preservation.{lang}.json',{'unchangedTextCues':sum(c['preservedText']for c in result),'unchangedAssEventGroupsPreserved':exacteventgroups,
            'newCueTiming':'provisional paired-clause waveform alignment, not recognized word alignment'})
    save(folder/'review.json',{'status':'word-asr-aligned-encoded-review-pending'if all(x['asrConfirmed']for x in review)else'contains-provisional-fallbacks',
        'assemblySha256':sha(Path(assembly)),'groups':review,'fallbackPassages':sorted({x['sentenceId']for x in review if not x['asrConfirmed']}),
        'fixedStyle':'boxed-white-forest-v1','humanListening':False})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['scripts','prepare','captions','stem-a01','align-ready']);ap.add_argument('--episodes',nargs='*');ap.add_argument('--episode');ap.add_argument('--assembly');a=ap.parse_args()
    if a.command=='scripts':_,r=scripts();print('Preserved script pairs:',len(r))
    elif a.command=='prepare':prepare(a.episodes)
    elif a.command=='stem-a01':a01_stems()
    elif a.command=='align-ready':align_ready()
    else:assert a.episode and a.assembly;captions(a.episode,a.assembly)
if __name__=='__main__':main()
