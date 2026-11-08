"""Package reviewed source-matched text; never mutate baseline, TTS or root revisions."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json
import review_source_revisions as r

ROOT, B = r.ROOT, r.B
OUT = B / 'narration'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def text(s): return ' '.join(s['lines'])
def write(p, obj): Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', 'utf8')

P = copy.deepcopy(r.P)
def edit(eid, sid, ko, en, reason, **more):
    old = P[eid]['changes'].get(sid, {})
    P[eid]['changes'][sid] = {**old, 'id': sid, 'ko': ko, 'en': en,
                            'reviewCorrection': reason, **more}

edit('A13', '027',
     '그래서 우리 시연에서는 한 손에 검정 원통형 손잡이를 붙였습니다. 자세를 반전했을 때 손잡이를 쥔 손과 손잡이의 위치도 함께 확인합니다.',
     'Our demonstration places a black cylindrical handle in one hand. When the pose is mirrored, check the gripping hand and the handle’s position together.',
     'Root inspected the actual Unreal prop: one black cylindrical handle, not a sword and shield. Keep the asymmetric-prop checking role.')
edit('A01', '053',
     '각자만 보면 자연스러워도 두 캐릭터를 합쳤을 때 위치나 타이밍이 어긋날 수 있죠.',
     text(r.baseline('A01','en')[52]),
     'Oatchi and rider are two characters, not two people. English was already correct and remains byte-identical.',
     team='a', observedSource='pikmin-oatchi', localRanges=[[6,14.6]],
     addedAdjacentJoin=True)
edit('A04', '030',
     '그렇게 하면 한 발의 힘은 잘 보이겠지만 연속으로 쏘는 리듬은 끊기겠죠.',
     'Each shot might look powerful, but the rhythm of continuous fire would break.',
     'The preceding counterfactual now concerns Cuphead continuous fire; replace the old punch wording without altering the anticipation/rhythm lesson.',
     team='b', evidence='../local/cup-first-level.mp4', localWindow=[0,35],
     addedAdjacentJoin=True)
edit('A14', '060',
     '동작을 이어 줄 때는 지켜야 할 자세와 연결에 필요한 시간, 그 사이를 조절하는 비율을 함께 정합니다.',
     'When connecting actions, choose the pose to preserve, the transition time, and the weights between them together.',
     'The new opening shows aim, roll and locomotion. Preserve all three summary concepts without claiming that the game exposes measured blend weights.',
     team='a', observedSource='authored-principle-summary', localRanges=[],
     addedAdjacentJoin=True)
edit('A05', '024',
     '차이가 기타를 휘두를 때도 팔과 다리가 만드는 서로 다른 방향을 나누어 보면 이 차이가 읽힙니다.',
     'In Chai’s guitar swing, separating the different directions made by his arms and legs makes the contrast readable.',
     'The observed pose includes airborne/bent legs. Remove unsupported ground-support wording; retain the asymmetric-direction comparison.')
edit('A05', '039', P['A05']['changes']['039']['ko'],
     'That is also why Chai’s opening guitar attack leaves a strong impression.',
     'Translate 눈에 남았던 as an impression, not continuous presence in the camera frame.')
edit('A08', '018', P['A08']['changes']['018']['ko'],
     'Look at Maelle holding her sword. Her face points toward the opponent, while the sword arm forms a separate, readable direction.',
     'Improve English grammar while preserving only the observed face/sword-arm directions; no claim about support feet.')

# Root's bounded source disposition: retain the developer's technical fact,
# but do not imply that the unavailable clean SIGN footage is being shown.
edit('A11', '001',
     '빠르게 나오는 공격인데, 어떤 동작은 날카롭고 어떤 동작은 미끄러지듯 느껴집니다.',
     'Both attacks are quick, but one feels sharp while the other seems to glide.',
     'Retain the original question; use the observed Dead Cells attack as the opening and the authored matched-time comparison for the contrast.',
     evidence='deadcells-motion.json', localWindow=[11,22], conditionalSource=False)
edit('A11', '003',
     '데드 셀에서 뛰고 무기를 휘두르는 캐릭터를 보세요. 몸과 다리의 윤곽이 자세마다 어떻게 바뀌는지 눈여겨보세요.',
     'Watch the Dead Cells character jump and swing a weapon. Notice how the outlines of the body and legs change from pose to pose.',
     'Replace unavailable clean SIGN footage with verified Dead Cells jump/slash shapes. Do not infer its internal interpolation method or measured timing.',
     evidence='deadcells-motion.json', localWindow=[11,22], conditionalSource=False)
edit('A11', '024',
     '길티기어 엑사드 사인의 개발 발표에서도 키 프레임 사이의 보간을 사용하지 않고 자세를 하나씩 직접 만들었다고 설명합니다. 중간을 매끈하게 채우는 대신 중요한 모양을 선택해 보여 주는 방식이죠. 우리 시연의 두 버전에서도 그 모양이 화면에 얼마나 남는지 보세요.',
     'The Guilty Gear Xrd -SIGN- development presentation explains that the team omitted interpolation between keyframes and posed them by hand. Instead of smoothly filling every gap, they selected the important shapes to show. In our two demonstration versions, watch how long those shapes remain visible.',
     'Preserve the official SIGN no-interpolation/hand-posed-keyframe technique as a cited principle, visualized by our own diagram/demo. No SIGN gameplay is claimed, copied or silently replaced with another version.',
     evidence='production/batches/animation-18-20261031/contrast-v5/narration/A11-source-disposition.json',
     localWindow=None, conditionalSource=False,
     observedSource='authored-timing-demo-plus-official-developer-document',
     primarySourceUrl='https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf',primarySourcePage=27)

def en_ids(eid, sid):
    n=int(sid)
    if eid=='A01':
        if n<=59: ids=[n]
        elif n==60: ids=[60,61]
        elif n<=79: ids=[n+1]
        elif n==80: ids=[81,82]
        elif n<=89: ids=[n+2]
        elif n==90: ids=[92,93]
        elif n==91: ids=[94,95]
        elif n<=94: ids=[n+4]
        else: ids=[99,100]
    elif eid=='A02':
        if n<=9: ids=[n]
        elif n==10: ids=[10,11]
        elif n<=33: ids=[n+1]
        elif n==34: ids=[35,36]
        elif n==35: ids=[37]
        elif n==36: ids=[38,39]
        else: ids=[n+3]
    else: ids=[n]
    return [f'{x:03}' for x in ids]

baseline_hashes={}
alignments={}
for eid in P:
    kp=ROOT/r.M[eid]['baselineKo'];ep=Path(str(kp).replace('.ko.','.en.'))
    baseline_hashes[eid]={'ko':{'path':rel(kp),'sha256':sha(kp)},'en':{'path':rel(ep),'sha256':sha(ep)}}
    mapping=[{'koId':s['id'],'enIds':en_ids(eid,s['id'])} for s in r.baseline(eid,'ko')]
    flattened=[i for x in mapping for i in x['enIds']]
    assert flattened==[s['id'] for s in r.baseline(eid,'en')],eid
    if eid in ['A01','A02']:
        alignments[eid]={'method':'Concatenate the specified existing EN rows with spaces; retain their exact wording and order. Apply replacements to semantic KO ids only after this alignment.',
                         'allOriginalEnglishRowsUsedExactlyOnce':True,'mapping':mapping}

root_revision=OUT/'revisions.json'; before_root=sha(root_revision)
episodes=[]; blocked=[]; existing=[]; inputs={}
for file in [B/'footage/passage-proposals.json',B/'footage/team-b/passage-proposals.json',B/'script-migration-plan.json',root_revision]:
    inputs[rel(file)]=sha(file)

for eid,x in sorted(P.items()):
    ko=r.baseline(eid,'ko');en={s['id']:s for s in r.baseline(eid,'en')}
    ko_by={s['id']:s for s in ko}; limits=[]; evidence_paths=[]
    for source in x['sourceProposals']:
        sp=source['episode'];lim=sp.get('limits',sp.get('limitations',[]))
        limits += [lim] if isinstance(lim,str) else (lim or [])
        if sp.get('sourceManifest'):
            path=B/'footage'/sp['sourceManifest'];assert path.exists(),path
            evidence_paths.append(path)
    changes=[]
    for sid,c in sorted(x['changes'].items()):
        idx=next(i for i,s in enumerate(ko) if s['id']==sid)
        ev=list(evidence_paths)
        if c.get('evidence'):
            raw=c['evidence'];path=ROOT/raw if raw.startswith('production/') else (B/'footage/team-b'/raw).resolve()
            assert path.exists(),path
            ev.append(path)
        # Small audit JSON supplements direct media with observations and source metadata.
        if eid=='A04' and sid in ['029','030']:
            for name in ['cup-first-level-audit.json','episode-A04-cuphead-sources.json']:
                p=B/'footage'/name
                if p.exists():ev.append(p)
        ev=list(dict.fromkeys(ev))
        evidence=[]
        for path in ev:
            item={'path':rel(path)}
            if path.suffix.lower()=='.json':
                item['sha256']=sha(path);inputs[item['path']]=item['sha256']
            evidence.append(item)
        old_en=' '.join(text(en[i]) for i in en_ids(eid,sid))
        reason=c.get('reviewCorrection',c.get('changeReason','Replace the previous commercial example with the observed approved example; preserve the same teaching role and adjacent principle.'))
        item={k:v for k,v in c.items() if k not in ['baselineSentenceId','team','existingApproved','evidence']}
        item.update({'id':sid,'ko':c['ko'],'en':c['en'],
            'baselineKoText':text(ko_by[sid]),'baselineEnIds':en_ids(eid,sid),'baselineEnText':old_en,
            'evidence':evidence[0]['path'] if evidence else inputs.keys().__iter__().__next__(),
            'evidenceFiles':evidence,'observedLocalRanges':c.get('localRanges',[c['localWindow']] if c.get('localWindow') else ([c['observedLocalRange']] if c.get('observedLocalRange') else [])),
            'changeReason':reason,'sourceVerified':not c.get('conditionalSource',False),
            'completeKoEnReadThrough':True,
            'readThroughScope':'This replacement in both languages and the preceding/following baseline passage; cumulative replacement sequence also reviewed. Text review, not playback or listening.',
            'contextIds':[ko[i]['id'] for i in [idx-1,idx+1] if 0<=i<len(ko)],
            'reuseExistingEnglishText':c['en']==old_en,
            'localReviewTextReleased':not c.get('conditionalSource',False),
            'publicationRightsAndSourceAudioClearedByThisReview':False})
        if c.get('conditionalSource'):
            item['holdReason']='Exact Xrd -SIGN- Millia source remains facecam/commentary-obscured and quarantined. Do not generate/adopt these lines until a clean source or explicit source disposition is recorded. Do not silently substitute Revelator.'
            blocked.append({'episode':eid,**item});continue
        if c.get('existingApproved'):
            item['episode']=eid;item['reuseExistingRootRevisionAndPcm']=True;existing.append(item);continue
        changes.append(item)
    episodes.append({'id':eid,'slug':r.M[eid]['slug'],'baseline':baseline_hashes[eid],
        'completeKoEnReadThrough':True,'sourceVerified':True,
        'readThroughScope':'Every replacement plus its immediate unchanged context in KO and semantically aligned EN; unchanged body principles/order retained. This is not a claim of re-listening to the complete episode.',
        'releaseStatus':'reuse-existing-root-A10' if eid=='A10' else 'source-observed-text-ready-for-local-review',
        'changes':changes,'preserveAllOtherKoIdsAndPcm':True,
        'sourceLimitations':limits,'publicationGate':'Local text verification does not close outstanding recorder/publisher/music/audio rights; retain the source ledgers and their restrictions.',
        'contextOnlyExtraIds':[c['id'] for c in changes if c.get('addedAdjacentJoin')],
        'blockedIds':[x['id'] for x in blocked if x['episode']==eid],
        'englishAlignmentRequiredBeforeApplyingChanges':eid in alignments})

result={'schemaVersion':1,'status':'source-observed-replacement-text-reviewed-explicit-source-holds',
    'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewedBy':'ai2d_finish',
    'reviewScope':'All replacement KO/EN passages, cumulative proposed sequence, and immediate unchanged neighboring passages were read by the model. Existing source observation records were reused; no new human listening, full-video viewing, TTS, render or rights clearance is claimed.',
    'preservation':'Do not rewrite the core lesson, reorder passages, or regenerate unchanged PCM. Root A10 is read-only and its two existing passages/PCM must be reused. A03 is outside this file.',
    'inputs':[{'path':p,'sha256':h} for p,h in sorted(inputs.items())],
    'summary':{'inputUniquePassages':85,'necessaryAdjacentCorrections':3,
        'newReleasedPassages':sum(len(e['changes']) for e in episodes),
        'existingRootA10PassagesToReuse':len(existing),'blockedSourcePassages':len(blocked),
        'episodeCount':len(episodes),'fullEpisodeWithNoNeededTextChange':['A16']},
    'episodes':episodes,'existingApprovedChanges':existing,'blockedChanges':blocked,
    'englishAlignment':alignments,
    'pronunciationOnlyNotes':[
        {'episode':'A08','id':'001','display':'Warrior I Pose (전사 자세 I)','koTtsAliasOnly':'전사 자세 원','doNotChangeCaptionCanonicalName':True},
        {'episode':'A13','id':'042','display':'MAXIMUM','koTtsAliasOnly':'맥시멈','doNotInferDeveloperIntentOrMirroringAlgorithm':True}],
    'specialChecks':{'A13_027_actualProp':'One-handed black cylindrical handle; no sword/shield demonstration claim.',
       'A08_pose':'Warrior I, not Warrior II; Maelle passages describe face, sword arm and coat only.',
       'A11_Millia':'Unusable SIGN footage remains quarantined. Root approved Dead Cells/Paper Mario as the two actual-game examples; developer-documented SIGN technique is retained in 024 with our diagram/demo. No active narration hold remains.',
       'A05_legSupport':'Removed ground-support claim from airborne/bent-leg pose.',
       'baselineEnglishSegmentMismatch':'A01 95KO/100EN; A02 70KO/73EN. Explicit many-to-one semantic mapping uses every old English row exactly once.'},
    'rootRevisionsSha256BeforeAndAfter':before_root}
result['sourceDisposition']={'A11':{'evidence':rel(OUT/'A11-source-disposition.json'),'actualGames':['Dead Cells','Paper Mario: The Thousand-Year Door (2024)'],'nintendoCount':1,'primaryGameCount':2,'rounding':'Approximately one third of two rounds to one; no unrelated third game is added.','unadoptedSource':'Exact Xrd -SIGN- Millia facecam/commentary footage remains quarantined; never enter the production cut list.'}}
assert result['summary']['newReleasedPassages']==86,result['summary']
assert sha(root_revision)==before_root
write(OUT/'source-verified-revisions.json',result)

lines=['# Source-verified narration replacements','',
       'Text review only. No TTS/render/platform changes. All previous useful principles, order and unchanged PCM are preserved. A10 is reused from root revisions.json.','',
       '| Episode | New released | Held | Note |','|---|---:|---:|---|']
for e in episodes:
    lines.append(f"| {e['id']} | {len(e['changes'])} | {','.join(e['blockedIds']) or '—'} | {e['releaseStatus']} |")
lines += ['', '85 input passages + 3 necessary adjacent fixes = 86 new released + 2 existing A10. No active narration holds remain; the unusable Millia source itself remains quarantined.', '',
          'English alignment is essential: A01 and A02 baseline English split several Korean sentences into multiple rows. Use englishAlignment before replacing by Korean semantic ID; no English content is dropped.', '',
          'The read-through covers every replacement and its immediate unchanged neighbors in both languages, with the replacement sequence reviewed cumulatively. It does not assert actual playback, complete audio listening, or new rights clearance.', '',
          'Source-adoption limits remain in the source ledgers. In particular Hi-Fi RUSH music/publisher scope and other unresolved publisher/audio conditions are not approved by this text review. Root may use the verified text for the authorized local-review stage while preserving those publication gates.', '',
          'Necessary adjacent corrections: A01 053 two people → two characters; A04 030 punch rhythm → continuous-shot rhythm; A14 060 preserves pose/time/weight summary without a mismatched attack-to-walk opening.', '',
          'Object corrections: A13 027 black cylindrical handle, A05 024 no ground-support inference, A08 Warrior I and no Maelle support-foot claim.', '']
lines += ['A11 source disposition: use observed Dead Cells and Paper Mario 2024 for actual-game examples. Retain the official SIGN developer technique (no interpolation between keyframes; poses authored by hand) in passage 024, paired with our own diagram/demo. The fact stays in its relevant timing section; no finished reference footage or substituted GG edition is used.', '']
(OUT/'source-verified-review.md').write_text('\n'.join(lines),'utf8')
readthrough=[]
for e in episodes:
    readthrough.append('\n'+e['id'])
    for c in e['changes']:readthrough += [c['id']+' KO '+c['ko'],c['id']+' EN '+c['en']]
(OUT/'source-verified-revisions.readthrough.txt').write_text('\n'.join(readthrough)+'\n','utf8')
print(json.dumps({'path':rel(OUT/'source-verified-revisions.json'),'sha256':sha(OUT/'source-verified-revisions.json'),'summary':result['summary'],'rootUnchanged':sha(root_revision)==before_root},ensure_ascii=False))
