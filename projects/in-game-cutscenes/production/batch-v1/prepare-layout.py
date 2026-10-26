"""Owned D27/D28 source bank and semantic layout. No estimated audio clocks."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[4]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def bank(source,a,b,role):return {'source':source,'in':a,'out':b,'role':role}
def row(pool,kind,shares,**kw):return {'pool':pool,'mode':kind,'minActualShare':shares[0],'preferredActualShare':shares[1],'maxActualShare':shares[2],**kw}

for slug in ('in-game-cutscenes','start-with-climax'):
 P=R/'projects'/slug;L=P/'production/local/batch-v1';a=P/('sources/source-audit-v2.json' if slug=='in-game-cutscenes' else 'sources/source-audit.json');audit=load(a)
 sources=[];games=[]
 for x in audit['selectedSources']:
  gid={'Hades II':'hades2','Animal Crossing: New Horizons':'acnh','DOOM (2016)':'doom','Super Mario Galaxy 2':'galaxy2','Phoenix Wright: Ace Attorney Trilogy':'ace'}[x['game']]
  if not any(g['id']==gid for g in games):games.append({'id':gid,'title':x.get('canonicalKorean',x['game']),'genre':x['genre'],'nintendo':x.get('nintendo',False)})
  sources.append({'id':x['id'],'gameId':gid,'path':x['file'],'sha256':x['sha256'],'url':x['sourceUrl'],'role':'independent-gameplay','licenseLabel':'Published publisher video policy + recording grant; see source audit','decoded':{'width':x['nativeDimensions'][0],'height':x['nativeDimensions'][1],'fps':x['nativeFps'],'duration':x['durationSeconds']},'rightsAudit':rel(a)})
 if slug=='in-game-cutscenes':
  A='hades2-first-run';B='hades2-crossroads';C='acnh-dialogue'
  pools={
   'intro':[bank(A,119,121,'Last enemy ends and reward remains; first spoken clause'),bank(A,124,135,'Large portrait appears at the next spoken clause; same recorded encounter, small native gap editorially omitted')],
   'definition':[bank(B,50,59,'Portrait speaker changes, only the general cutscene definition')],
   'story-object':[bank(B,25,36,'Painting foregrounds a story relation')],
   'story-dialogue':[bank(B,95,123,'Hecate/Melinoe portrait dialogue; meaning and character focus'),bank(B,135,155,'Further directed Hecate exchange and the next task; independently viewed native source')],
   'gestures':[bank(C,124,140,'126s head tilt→128s both paws raised visibly above counter→129–131s paws lowered; native124–132 reviewed')],
   'breather':[bank(B,70,91,'Enemy-free voluntary walking toward the next conversation; independently viewed source70/75/80/85; avoids undecodable leading stream-copy seek')],
   'reward':[bank(A,107,119,'Combat leading to the already-previewed reward; no source interval repeated')],
   'reward-result':[bank(A,135,145,'Apollo exchange following the cleared room')],
   'dialogue-pages':[bank(C,32,56,'Completed text→next marker→new dialogue page')],
   'viewing':[bank(B,38,50,'Dora portrait and response while considering viewing pace')],
   'return-play':[bank(B,125,135,'Return from dialogue to hub and next optional exchange'),bank(B,155,160,'Manual hub movement;135–155 reserved for story focus')],
   'next-action':[bank(A,160,178,'Walk into next encounter and attack enemies')],
  }
  rows={
   '01-p01':row('intro','overview',(.25,.65,.85)),
   '01-p02':row('definition','formats',(.12,.35,.55)),
   '01-p03':row(None,'fixedVideo',(0,0,0)),
   '01-p04':row(None,'quality',(0,0,0)),
   '02-p01':row('story-object','storyFocus',(.3,.75,1)),
   '02-p02':row('story-dialogue','storyFocus',(.4,.85,1)),
   '03-p01':row('story-dialogue','storyFocus',(.65,.95,1)),
   '03-p02':row('gestures','storyFocus',(1,1,1)),
   '03-p03':row('story-dialogue','conclusion',(.3,.85,1)),
   '04-p01':row('story-dialogue','pacing',(.4,.8,1)),
   '04-p02':row('breather','pacing',(.65,.95,1)),
   '05-p01':row('reward','viewingReward',(.4,.85,1)),
   '05-p02':row(None,'viewingReward',(0,0,0)),
   '05-p03':row('reward-result','viewingReward',(.4,.9,1)),
   '06-p01':row('dialogue-pages','advance',(.5,.9,1)),
   '06-p02':row('dialogue-pages','advance',(.5,.9,1)),
   '06-p03':row(None,'advance',(0,0,0)),
   '07-p01':row(None,'playbackControls',(0,0,0)),
   '07-p02':row('viewing','advance',(1,1,1)),
   '08-p01':row(None,'skipScope',(0,0,0)),
   '08-p02':row(None,'wholeSkip',(0,0,0)),
   '08-p03':row('return-play','skipChoice',(.4,.6,.65)),
   '09-p01':row(None,'qte',(0,0,0)),
   '09-p02':row(None,'qte',(0,0,0)),
   '09-p03':row('next-action','conclusion',(.5,.9,1)),
  }
 else:
  A='doom-2016-opening';B='galaxy2-opening';C='ace-trilogy-official-first-case';D='galaxy2-first-stage'
  extra=load(P/'sources/galaxy2-extra-source-review.json');pr=load(L/'sources/first-stage-review/probe.json');v=next(x for x in pr['streams'] if x['codec_type']=='video')
  sources.append({'id':D,'gameId':'galaxy2','path':extra['file'],'sha256':extra['sha256'],'url':extra['sourceUrl'],'role':'independent-gameplay','licenseLabel':'Nintendo commentary policy + LongplayArchive transformed credited snippet grant','decoded':{'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'duration':float(pr['format']['duration'])},'rightsAudit':rel(P/'sources/galaxy2-extra-source-review.json')})
  pools={
   'intro':[bank(A,49,58,'First-room aimed shots and enemy reactions')],
   'gun':[bank(A,59,64,'Pistol view after first-room combat; not a claimed new kill')],
   'shoot':[bank(A,152,163,'Early facility aiming/firing')],
   'participation':[bank(A,230,237,'Actual manual ranged fight confirms player participation after the information-order diagram')],
   'objective':[bank(A,84,108,'Equipment acquisition and immediate facility task before full exposition')],
   'control':[bank(A,171,187,'Manual traversal, shotgun acquisition, next engagement')],
   'mario-walk':[bank(B,45,70,'Storybook manual walking/jumping toward castle')],
   'spin':[bank(B,108.5,124,'Crystal already approaches frame; first Spin109–111 and second115 match named move/result clauses; no mandatory gate claim')],
   'early-peak':[bank(B,140,148,'Early giant antagonist as a concrete opening peak, before the qualitative placement diagram')],
   'threat':[bank(B,137.4,140,'Bowser portrait aligned to named antagonist clause'),bank(B,150,178,'Peach on the giant hand aligned to the rescue-target clause; preview140–148 not repeated')],
   'companion':[bank(B,70,98,'Earlier Baby Luma encounter, explicitly recalled after threat')],
   'context':[bank(A,64,80,'Hologram context after first fight'),bank(A,108,150,'Facility security panel/communication after action')],
   'quiet':[bank(D,9,19,'Manual platform ascent'),bank(D,33,51,'Successive jumps to high route')],
   'rule-use':[bank(D,78,95,'Spin crystal and jump across blocks, a real confirmation after rule diagram')],
   'first-trial':[bank(C,57.991,60.5,'Evidence selection badge→statue→Objection'),bank(C,62.996,65.999,'Sahwit reacts; source is an edited official excerpt')],
  }
  rows={
   '01-p01':row('intro','control',(.45,.9,1)),
   '01-p02':row(None,'overview',(0,0,0)),
   '01-p03':row('early-peak','earlyPeak',(.15,.3,.5)),
   '02-p01':row('gun','control',(.2,.5,.8)),
   '02-p02':row('shoot','control',(.7,1,1)),
   '02-p03':row('objective','firstAct',(.4,.85,1)),
   '03-p01':row(None,'informationOrder',(0,0,0)),
   '03-p02':row(None,'informationOrder',(0,0,0)),
   '03-p03':row('participation','informationOrder',(.3,.5,.75)),
   '04-p01':row('control','control',(.4,.75,1)),
   '04-p02':row('control','control',(.4,.85,1)),
   '05-p01':row('mario-walk','control',(.65,1,1)),
   '05-p02':row('spin','ruleUse',(.6,.9,1)),
   '05-p03':row('threat','firstAct',(.7,1,1)),
   '05-p04':row('companion','control',(.6,.95,1)),
   '06-p01':row(None,'informationOrder',(0,0,0)),
   '06-p02':row('context','informationOrder',(.65,1,1)),
   '07-p01':row('mario-walk','quietPlay',(.5,.9,1)),
   '07-p02':row('quiet','quietPlay',(.65,1,1)),
   '08-p01':row(None,'earlyPeak',(0,0,0)),
   '08-p02':row('rule-use','ruleUse',(.25,.5,.55),diagramFirst=True),
   '09-p01':row('first-trial','firstAct',(.1,.25,.4)),
   '09-p02':row('first-trial','evidenceSelection',(.15,.3,.45),diagramFirst=True),
   '09-p03':row(None,'firstAct',(0,0,0)),
  }
 script=load(P/'script/batch-v1/narration.ko.json')
 expected={f"{s['id']}-p{i+1:02}" for s in script['scenes'] for i,_ in enumerate(s['lines'])};assert set(rows)==expected
 for s in script['scenes']:
  for i,text in enumerate(s['lines']):
   rowdata=rows[f"{s['id']}-p{i+1:02}"];rowdata['summary']=text;rowdata['title']=s['title'];rowdata['sourceEvidence']='planning/batch-v1-plan.json and source audit; actual intervals are unique, not reference media.'
 save(P/'sources/independent-footage.json',{'slug':slug,'revision':'batch-v1','sources':sources,'games':games,'sourceAudit':{'path':rel(a),'sha256':sha(a)},'sourceCountIsNotGameCount':True,'humanListening':'pending'})
 save(P/'planning/scene-layout.json',{'slug':slug,'revision':'batch-v1','status':'semantic-placement-awaiting-measured-word-clock','pools':pools,'paragraphs':rows,'noEstimatedTimings':True,'actualViewport':[0,0,1920,864],'viewportReason':'Fit original aspect above fixed caption band so source dialogue and HUD remain visible.','noAutomaticMicrocutForRatio':True})
 print(slug,'paragraphs',len(rows),'native-capacity-seconds',sum(b['out']-b['in'] for banks in pools.values() for b in banks))
