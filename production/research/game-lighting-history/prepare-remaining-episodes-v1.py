"""Create the reviewed CPU inputs; never allocates CUDA or marks final video QA."""
from pathlib import Path
import copy, hashlib, json, subprocess
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def checked(args):
    p=subprocess.run(['node','scripts/review-video-duplicates.cjs',*args],cwd=ROOT,
                     capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
    print(p.stdout,end='',flush=True)
    if p.returncode: raise RuntimeError(p.stderr)
def parse(n):
    scenes=[]
    for line in (BASE/f'episode-0{n}-pairs.txt').read_text(encoding='utf-8').splitlines():
        if line.startswith('@ '):
            ident,title=line[2:].split(' | ',1)
            scenes.append(dict(id=ident,title=title,ko=[],en=[]))
        elif line.strip():
            ko,en=line.split(' || ',1);scenes[-1]['ko'].append(ko);scenes[-1]['en'].append(en)
    assert len({x['id'] for x in scenes})==len(scenes)
    assert all(x['ko'] and len(x['ko'])==len(x['en']) for x in scenes)
    assert max(sum(map(len,x['ko'])) for x in scenes)<1200, 'Split long continuous scene before token ceiling'
    return scenes
reasons={
2:'Episode2 reviews photon arrival/density estimation, engine static baking, LPV, AA and light-list assignment, linear color, brief material connections, SSR information limits, LTC, water and volume transport. Episode1 owns sector lighting/lightmaps/RNM/shadow-volume/CSM/deferred ordering. Existing PBR lectures derive material equations, not this transport/data/volume chronology; older frame-rate and DX12 API lectures do not teach the worked photon/volume/SSR sequence. Brief prerequisites are explicitly bridges. Full106 KO/EN paragraph pairs authored and directly read; original source content is independently expanded, not a copied translation.',
3:'Episode3 compares world representations, BVH interval traversal and BLAS/TLAS/hybrid updates, sampling, DDGI/ReSTIR, culling/resource budgets, Nanite and Lumen caches. Existing camera/frustum/depth math teaches coordinate transforms, not this lighting/cache sequence; existing DLSS5 reaction/RenderFormer topics are not repeated and neural architectures are excluded. Episode2 owns SSR and volume integration, episode4 owns VSM/path-tracing/RR/display-frame/final-resource inspection. All84 KO/EN paragraph pairs directly read, including the initially omitted second half.',
4:'Episode4 separates VSM pages/cache/SMRT, visibility-buffer/mobile tile storage, path samples/MIS/Russian roulette, RR, MegaLights, transparency, DLSS4/4.5/5 roles, post-processing and an actual-resource inspection methodology. Older DLSS5 reaction is a product discussion and older DX12 API lectures teach resource/API setup; this episode connects stored resources to computed/reconstructed/displayed pixels with worked layer examples. Episode3 owns detailed BVH/ReSTIR/Lumen derivation. All87 KO/EN paragraph pairs authored and directly read; no fabricated captured pass IDs or timings. NeRF/RenderFormer/3DGS architecture content excluded.'}
evidence='production/research/game-lighting-history/current-series-duplicate-review.json; projects/game-lighting-history-01/production/current-input-rereview-v9.json: prior actual read-only Studio search/metadata/transcript comparisons, current saved-private receipts CbX6KQ-_zsc/c96qTnlHBVU/lf765yYhPdM. Current projection-depth manifest/README fully read again: 633.6667s no-BGM40:60 depth/interpolation lecture, local reviewed output with upload only prepared. No new UI observation is claimed. Remaining47 current project inputs checked against prior reviewed inventory; no newly discovered foreign project. Own sibling scripts fully authored/read and compared at complete episode boundaries.'
def main():
    baseline=read(ROOT/'projects/game-lighting-history-01/project.json')
    pack=read(BASE/'research-pack.json')
    # Keep the source pack's source references; no footage acquisition approval.
    chapters=pack.get('chapters',[])
    now=datetime.now(timezone.utc).isoformat()
    for n in [2,3,4]:
        slug=f'game-lighting-history-0{n}';p=ROOT/'projects'/slug
        if p.exists(): raise RuntimeError('Preserve existing project; this creation is one-time: '+slug)
        candidate=read(BASE/f'candidate-0{n}.json')
        checked([slug,'--candidate-file',f'production/research/game-lighting-history/candidate-0{n}.json','--decision','distinct','--reason',reasons[n],'--studio-evidence',evidence])
        checked([slug,'--candidate-file',f'production/research/game-lighting-history/candidate-0{n}.json','--check'])
        scenes=parse(n);count=sum(len(x['ko']) for x in scenes)
        for lang in ['ko','en']:
            script=dict(schemaVersion=1,status='reviewed-independent-explanation-input-for-tts',episode=n,
                        seriesPlan='production/research/game-lighting-history/series-plan.json',
                        durationMeasured=False,targetMinutes=20,footageDependentLinesFinalApproved=False,
                        scope='Complete independent educational narration. Any new shot-specific observation must await native pixel/source review. No final footage quota or rights approval.',
                        title=candidate['titleKo' if lang=='ko' else 'titleEn'],
                        scenes=[dict(id=x['id'],title=x['title'],lines=x[lang]) for x in scenes])
            write(p/'script'/f'narration.{lang}.json',script)
        manifest=copy.deepcopy(baseline)
        manifest.update(slug=slug,status='reviewed-tts-input-awaiting-cooperative-batch',titles=dict(ko=candidate['titleKo'],en=candidate['titleEn']))
        manifest['delivery']['directory']='output/'+slug
        manifest['delivery']['collector']='node scripts/collect-video-output.cjs '+slug
        manifest['membershipOutro']['appliedToFinal']=False
        manifest['paths']={k:v.replace('game-lighting-history-01',slug).replace('balanced-v4','balanced-v1') for k,v in manifest['paths'].items()}
        manifest['tts'].update(outputDir=f'shared/output/narration/{slug}/qwen3-1.7b-balanced-v1',filenameStem=f'{slug}-qwen3-1.7b-balanced-v1')
        manifest['productionGates']={k:False for k in baseline['productionGates']}
        manifest['productionGates'].update(currentDistinct=True,finalScriptReviewed=True)
        manifest['productionState']=dict(updatedAt=now,ownedGpuJobs=0,ownedCpuAsrJobs=0,currentParagraphPairs=count,
                                       currentVoiceApproved=False,scriptReview=f'projects/{slug}/production/script-input-review-v1.json',
                                       humanListeningApproved=False,allShotSpecificNarrationApproved=False)
        manifest['series']=dict(plan='production/research/game-lighting-history/series-plan.json',number=n,targetMinutes=20,timingMeasured=False,measuredNarrationSeconds=None)
        editing=manifest['editing']
        editing['exampleInterleaving']['planningPath']=f'projects/{slug}/planning/outline.md'
        editing['plannedActualSeconds']=None;editing['plannedExplanationSeconds']=None
        editing['openingOverview']=dict(required=True,scene='overview',reviewedBeforeTts=True,question=candidate['viewerQuestion'],
                                       outcome='Distinguish stored data, evaluated work, reuse and information limits using the worked examples',
                                       orderedSteps=[x['title'] for x in scenes[1:]],classification='explanation',languages=['ko','en'],narrationSeconds=None)
        write(p/'project.json',manifest)
        scene_list='\n'.join(f"- {x['id']}: {x['title']} ({len(x['ko'])} paragraph pairs)" for x in scenes)
        (p/'planning').mkdir(parents=True,exist_ok=True)
        (p/'planning/outline.md').write_text(f'# {candidate["titleKo"]}\n\nViewer question: {candidate["viewerQuestion"]}\n\nOriginal2s branding → narrated whole-episode overview → following complete conceptual sequence → conclusion → original10s membership. Measured duration pending; approximate20min target never licenses loops or cuts inside algorithms.\n\n{scene_list}\n\nWhite projected top/side faces, spatial occlusion and meaningful narration-timed comparisons require native animated-pixel QA. Fixed caption center960,970; source crop/cues resolve collisions. Body60:40 measured only after concept-matched game/engine demonstrations secured. No actual frame quota or rights approved yet. Existing approved reference/Nimbus preserved; no-BGM/40:60 exceptions from the separate math lecture are not copied.\n\nNarration now covers the independent algorithm explanations and general test methodology. It does not infer proprietary implementations from appearance or fabricate unobserved shots. Shot-specific additions await source inspection.\n',encoding='utf-8')
        (p/'sources').mkdir(parents=True,exist_ok=True)
        selected=[]
        for ch in chapters:
            ident=str(ch.get('id',''))
            if any(x['id'].startswith(ident) for x in scenes if x['id'] not in ['overview','conclusion']): selected.append(ch)
        write(p/'sources/research-links.json',dict(researchPack='production/research/game-lighting-history/research-pack.json',chapters=selected,finalFootageRightsApproved=False))
        (p/'sources/SOURCES.md').write_text('# Internal research and source evidence\n\nPrimary source/claim mapping: [research pack](../../../production/research/game-lighting-history/research-pack.json), [episode mapping](research-links.json). Historical publication/demo/support/shipped application remain separate. Common algorithm derivations and worked numerical values are independent educational examples; values are not game measurements. Current source verification is recorded in production/research/game-lighting-history/remaining-source-review-v1.json.\n\nPrior actual UE5 reveal native review can support its observed Lumen OFF/ON comparison only. Remaining native intervals, rights and recent-use review are pending; prepared source links are not acquisition or pixel approval. No source audio is licensed by these references. Future actual footage allocation requires sources/game-candidates.json with source, in/out, visible action, focus and diagram connection.\n',encoding='utf-8')
        write(p/'sources/game-candidates.json',dict(status='pending-native-selection-and-interval-review',seriesResearch='production/research/game-lighting-history/research-pack.json',candidates=[],selectedIntervals=[],rightsApproved=False,recentUseCheckPassed=False))
        (p/'README.md').write_text(f'# {candidate["titleKo"]}\n\nRendering history episode{n}/4. Complete current independent KO/EN narration: {len(scenes)} scenes, {count} paragraph pairs. GPU TTS is queued inside one cooperative batch for episodes2–4; only after the entire batch exits does the original research queue resume. Actual production duration, ASR, human listening, final native footage, spatial animated pixels,60:40, mixed audio/render/collection/private upload are pending. Original source coverage is distributed across the approved series, with no new-topic neural-renderer lecture.\n',encoding='utf-8')
        review=dict(schemaVersion=1,reviewedAt=now,fullScriptDirectReread=True,allKoEnTextDirectlyReviewed=True,
                    finalTtsInputWritten=True,paragraphPairs=count,scenes=len(scenes),overviewMatchesActualBody=True,
                    finalInputHashes={lang:sha(p/'script'/f'narration.{lang}.json') for lang in ['ko','en']},
                    textPairSource=f'production/research/game-lighting-history/episode-0{n}-pairs.txt',
                    sourceClaimScope='Primary engine/game sources plus independently derived algorithm examples; no exact unobserved captured action/resource IDs/performance claims.',
                    duplicateReason=reasons[n],humanListeningApproved=False,finalMixedAsrApproved=False,
                    actualNativeIntervalsApproved=False,allShotSpecificNarrationApproved=False,
                    timing='Provisional paragraph boundary estimates from the renderer are not final caption/word alignment approval.')
        write(p/'production/script-input-review-v1.json',review)
        print(json.dumps(dict(slug=slug,scenes=len(scenes),paragraphPairs=count),ensure_ascii=False),flush=True)
    # The new siblings are now full content inputs. Refresh before launching any CUDA child.
    for n in [2,3,4]:
        slug=f'game-lighting-history-0{n}'
        checked([slug,'--candidate-file',f'production/research/game-lighting-history/candidate-0{n}.json','--decision','distinct','--reason',reasons[n],'--studio-evidence',evidence])
        checked([slug,'--candidate-file',f'production/research/game-lighting-history/candidate-0{n}.json','--check'])
if __name__=='__main__': main()
