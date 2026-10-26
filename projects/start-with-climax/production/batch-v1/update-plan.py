"""Bind the frozen script to inspected source evidence. No media jobs."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[4]
PROJECT=ROOT/'projects/start-with-climax'
H=PROJECT/'production/batch-v1'
PLAN=PROJECT/'planning/batch-v1-plan.json'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

audit_path=PROJECT/'sources/source-audit.json'
audit=load(audit_path)
script=load(PROJECT/'script/batch-v1/narration.ko.json')
review=load(H/'script-review.json')
review.update({
    'status':'script-frozen-source-checked-ready-for-root-voice',
    'sourceAudit':{'path':rel(audit_path),'sha256':sha(audit_path)},
    'directPixelScope':{
        'DOOM':'Source boards covering32–191s directly read. Recording agent separately verified16 fine frames48–63s. No whole listening claim.',
        'Galaxy2':'All30 ten-second bins0–300s and26 one-second Spin bins100–126s directly read. Spin at109–111s and114–116s breaks crystals; no mandatory gate claim.',
        'Ace':'All14 first-case fine panels52.986–65.999s directly read. Later-case footage and DS composites rejected.'},
    'terminologyCorrection':'Official Nintendo Korean Baby Luma = 베이비치코 and Spin = 스핀, corrected before TTS.',
    'sourceCrossCheckCorrections':[
        {'paragraph':'02-p02','change':'Door or next-route unlocking replaced with visible threat reduction.','reason':'Recorded first-room enemy reactions are shown; door traversal is not in the selected event.'},
        {'paragraph':'02-p03','change':'Literal first scene changed to opening.','reason':'Short fixed opening words precede manual combat.'},
        {'paragraph':'05-p02','change':'Mandatory blocked route and opening gate removed; Spin breaking the crystal retained.','reason':'Fine pixels show crystal destruction; no claim that jumping past it was impossible.'},
        {'paragraph':'05-p04','change':'Baby Luma is described as already met along the way.','reason':'Avoid moving the encounter to after Bowser by narration order.'}]})
save(H/'script-review.json',review)

plan=load(PLAN)
plan['status']='script-frozen-ready-for-root-ElevenLabs-voice'
plan['scriptReview']={'path':rel(H/'script-review.json'),'sha256':sha(H/'script-review.json'),
    'scriptInputs':review['scriptInputs'],'paragraphs':review['paragraphs'],
    'clauseUnits':review['clauseUnits'],'spokenChars':review['spokenChars'],
    'voiceOwner':'root','actualSourceAudioListening':'pending; metadata and stills are not listening'}
plan['sourceAudit']={'path':rel(audit_path),'sha256':sha(audit_path)}
plan['selectedGames']=audit['selectedSources']
plan['nintendoExampleCount']=audit['nintendoExampleCount']
plan['previousEpisodeComparison']={
    'episode':'D27','basis':'Current selected batch source audit; D25 through D30 order',
    'games':[{'game':'Hades II','genre':'isometric action roguelike','status':'independent FHD direct review and Supergiant policy checked'},
             {'game':'Animal Crossing: New Horizons','genre':'life simulation'}],
    'comparison':'D28 uses FPS,3D platforming,and courtroom adventure. D27 uses isometric action roguelike and life simulation; this is a genre/interaction change serving the actual lesson, not a title-only shooter replacement.'}
plan['terminology']=[
    {'ko':'둠','en':'DOOM(2016)','meaning':'First-person shooter; recorded2016 version, not1993.','display':'DOOM(2016)','tts':'둠'},
    {'ko':'슈퍼 마리오 갤럭시 2','en':'Super Mario Galaxy2','meaning':'3D platform game; inspected Wii NTSC recording.','tts':'슈퍼 마리오 갤럭시 투','primary':'https://www.nintendo.com/kr/switch/bpdla/index.html'},
    {'ko':'베이비치코','en':'Baby Luma','meaning':'Little star-shaped companion met before Bowser.','primary':'https://www.nintendo.com/kr/switch/bpdla/index.html'},
    {'ko':'스핀','en':'Spin','meaning':'Body rotation using the companion power; breaks the depicted crystal.','primary':'https://www.nintendo.com/kr/switch/bn84a/index.html'},
    {'ko':'역전재판123나루호도셀렉션','en':'Phoenix Wright: Ace Attorney Trilogy','meaning':'Modern HD collection. Selected evidence and reaction belong to the first case. The trial is early, not literally the first video frame.','primary':'https://www.ace-attorney.com/trilogy/us/'}]
links=[
    ('01','02','Small climax is a first experience of appeal','DOOM first room demonstrates that promise'),
    ('02','03','Immediate task understood before full history','Reorder information around experienced action'),
    ('03','04','Acting can create a question','Hand over controls to permit participation'),
    ('04','05','Action plus visible threat motivates play','Mario route actions lead to giant Bowser'),
    ('05','06','Actions and events establish understanding','Later background answers active questions'),
    ('06','07','Information attached to a direct task','Quiet beginnings can also offer a task'),
    ('07','08','Small actions make a calm world familiar','Place a small peak early or shorten the opening'),
    ('08','09','Teach a rule needed by the next action','First trial begins defining evidence judgments')]
plan['chapterBoundaryLinks']=[{'from':a,'to':b,'previousResult':x,'inheritedNeed':y,
    'headingFreeFullRead':True,'realizedJoinReview':'pending actual voice and final playback'} for a,b,x,y in links]
roles={
 '01':('doom-2016-opening','Opening actual-game promise','First-room shooting after branding; no reference lesson film.'),
 '02':('doom-2016-opening','FFVII-equivalent urgent task before complete history','Early pistol combat. No claim of zero exposition or control on the first literal frame.'),
 '03':(None,'Chronological causes versus information order','Authored MC relationship timeline; no measured retention data.'),
 '04':('doom-2016-opening','Manual action and visible consequence','Movement, aiming and firing; editorial target guides, no invented internal values.'),
 '05':('galaxy2-opening','Kid Icarus-equivalent early control, antagonist reveal, prerequisite learning','Storybook traversal, Baby Luma, Spin crystal, giant Bowser. Not a one-minute claim or immediate final boss fight.'),
 '06':('doom-2016-opening','Return to first game: information after action','Security status, hologram and communication follow the first-room fight.'),
 '07':('galaxy2-opening','Quiet beginning still provides control','Separate Mario traversal windows; no repeated idle footage.'),
 '08':(None,'Early peak, or short lead-in when structure resists','Qualitative curve plus needed-rule and immediate-use relationship.'),
 '09':('ace-trilogy-official-first-case','Original first-trial role retained in HD edition','Official actual UI57.991–59.993 and reaction62.996–65.999. Not a continuous unassisted attempt; promotional text excluded from actual bank.')}
for row in plan['sourceToScriptToScreen']:
    scene=row['plannedScene'];sid,role,screen=roles[scene]
    row.update({'productionSource':sid,
        'productionGame':next((x['game'] for x in audit['selectedSources'] if x['id']==sid),None),
        'sourceStatus':'FHD and recording rights reviewed' if sid else 'self-authored concept diagram',
        'adoptedRole':role,'plannedScreen':screen,
        'paragraphIds':[f'{scene}-p{i+1:02}' for s in script['scenes'] if s['id']==scene for i,_ in enumerate(s['lines'])]})
plan['learningBeats']=[{'scene':x['plannedScene'],'referencePoint':x['id'],
    'target':x['centralPoint'],'speech':'Canonical KO and paired clauses; measured voice pending',
    'visual':x['plannedScreen'],'speechVisualOverlap':True,'hold':0,
    'holdReason':'No observation silence; narrate target, action, result over the visible event.'}
    for x in plan['sourceToScriptToScreen']]
plan['rendering']={'tool':'Motion Canvas',
    'sourcePrefix':'motion-canvas/src/projects/start-with-climax/batch-v1',
    'reason':'Information order, qualitative story curves and evidence selection are2D relationships. World actions remain independent gameplay; no duplicate engine simulation.',
    'implementationKind':'conceptual illustration plus inspected independent screenshots',
    'packing':'Only explanation cuts on a packed timeline; source offsets in edit-plan preserve continuous audio clock.',
    'capture':[1920,1080,60],'captionProtectedRect':[150,892,1784,1060],
    'fixedCaptions':{'center':[960,970],'size':48,'maxLines':2},
    'encoded1080And375Review':'pending'}
plan['tts'].update({'status':'script ready; root generation pending','spokenChars':review['spokenChars'],
    'actualListening':'pending','aliases':'direct string map',
    'canonicalChecks':'Baby Luma and Spin official Korean names checked before TTS'})
plan['currentUncertainty']=[
    'Measured voice times, moving annotations, and source-audio listening remain pending.',
    'All selected cues/cuts still need encoded1080/375 review.',
    'Capcom standalone trailer actual-gameplay excerpt is interpreted under its published game-footage commentary policy; no broader promotional-asset license claimed.']
plan['omissions'].append({'content':'Unused source game names and Kid Icarus exact timing',
    'reason':'Verified equivalents preserve example function and order without claiming identical controls or seconds.'})
save(PLAN,plan)
print('Frozen script evidence and source-to-screen plan saved.')
