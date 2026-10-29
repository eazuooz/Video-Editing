"""Prepare the user-requested workflow-first revision; preserve the v3 body."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,q):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

NEW={
('01',1):(
'기존 게임의 동작 원리를 분석해서, 새로운 외형의 게임을 빠르게 만들 수 있을까요? 왼쪽은 벅샷 룰렛, 오른쪽은 이번에 만든 프로토타입입니다. 오늘은 REA라는 분석 도구와 AI 에이전트, 3D 제작 도구를 연결해 이런 기반 프로토타입을 만드는 과정을 보여드리겠습니다.',
'Can we analyze how an existing game works and quickly build a game with a new look? Buckshot Roulette is on the left; our prototype is on the right. Today, we will connect the REA analysis tool, an AI agent, and 3D production tools to build this kind of foundation for a new game.'),
('01',2):(
'전체 흐름부터 보겠습니다. 출발점은 기존 게임의 실행 파일과 데이터입니다. 한쪽에서는 코드를 분석해 규칙을 찾고, 다른 쪽에서는 모델과 애니메이션이 어떻게 구성되어 있는지 살펴봅니다. 이 분석을 바탕으로 AI 에이전트가 새 코드를 작성하고, 새로운 외형을 준비합니다. 마지막으로 게임 엔진에 합쳐 직접 조작할 수 있는 프로토타입을 만듭니다.',
'Let us start with the whole workflow. It begins with an existing game’s executable and data. One branch examines code to identify rules; another examines how models and animations are organized. Using that analysis, an AI agent writes new code and prepares a new visual design. Finally, we bring them together in a game engine to make a playable prototype.'),
('02',1):(
'여기서 REA부터 알아보죠. 이름은 Reverse Engineer Anything. 기존 프로그램의 파일과 코드 구조를 조사하는 작업을 AI 에이전트가 수행하도록 연결해 주는 분석 도구입니다. AI 에이전트는 목표에 맞춰 도구를 호출하고, 결과를 읽으며 다음 작업을 이어가는 인공지능입니다. 에이전트가 어떤 파일이 들어 있는지 요청하면 REA가 목록을 반환하고, 그 결과를 읽은 에이전트가 필요한 파일을 다시 살펴보는 식입니다. 이렇게 얻은 근거를 다음 분석과 구현에 사용하는 거예요.',
'First, what is REA? Its name is Reverse Engineer Anything. It is an analysis tool that lets an AI agent investigate a program’s files and code structure. An AI agent calls tools toward a goal, reads their results, and continues with the next task. For example, the agent requests a file inventory, REA returns the list, and the agent uses it to inspect the relevant files. The resulting evidence guides the next analysis and implementation steps.'),
('02',2):(
'REA는 명령줄 프로그램으로 직접 사용할 수도 있고, MCP로 AI 에이전트에 연결할 수도 있습니다. MCP는 AI가 외부 도구를 사용하도록 연결하는 표준 규격입니다. 기계어 분석이 필요하면 Ghidra를 사용하고, 모델과 애니메이션은 게임 엔진에 맞는 리소스 도구로 살펴봅니다. 새 외형을 만들 때는 Tripo MCP로 3D 생성 도구를 연결하거나, Blender를 다룰 수 있죠. 완성한 규칙과 외형은 Unity, Unreal, Godot 같은 게임 엔진에 합칩니다. 이제 이번 실험에서 실제로 사용한 경로를 따라가 보겠습니다.',
'REA can be used directly from a command line or connected to an AI agent through MCP. MCP is a standard for connecting AI to external tools. When machine-code analysis is needed, Ghidra can help; models and animations are examined with resource tools appropriate to the engine. For a new visual design, an agent can use Tripo MCP to connect to 3D generation tools, or work with Blender. The rules and visuals then come together in an engine such as Unity, Unreal, or Godot. Now let us follow the route we actually used in this experiment.'),
('08',1):(
'이제 처음의 흐름을 다시 보겠습니다. REA로 게임의 구조를 찾고, 읽을 수 있는 코드에서 핵심 규칙을 분리했습니다. 그 규칙으로 새 코드를 작성하고, Blender에서 만든 외형을 Godot 엔진에 연결해 직접 플레이할 수 있는 프로토타입을 만들었죠. 이렇게 기존 게임을 작동 원리를 확인하는 출발점으로 삼으면, 처음부터 추측하던 부분을 줄이고 내 아이디어를 시험하는 단계로 더 빠르게 넘어갈 수 있습니다. 이번 결과물은 그 제작 흐름을 직접 시험한 기반 프로토타입입니다.',
'Let us return to the workflow. REA helped us locate the game’s structure, and readable code let us identify its core rules. We wrote new code for those rules, connected our Blender-made visuals in Godot, and produced a playable prototype. Using an existing game as a starting point for understanding behavior reduces what we have to guess and helps us reach the stage of testing our own ideas sooner. This prototype is our practical test of that production workflow.')
}
ALIASES={'Reverse Engineer Anything':'리버스 엔지니어 애니씽','Tripo MCP':'트리포 엠씨피','Ghidra':'기드라','Blender':'블렌더','Unreal':'언리얼','Unity':'유니티','Godot':'고도','REA':'알이에이','MCP':'엠씨피','AI':'인공지능','3D':'쓰리디'}
def spoken(text):
    for source,target in ALIASES.items():text=text.replace(source,target)
    return text.replace("인공지능가", "인공지능이")
def main():
    ko=read(P/'script/narration.ko.json');en=read(P/'script/narration.en.json')
    baseline=P/'production/local/revision-v3-inputs';baseline.mkdir(parents=True,exist_ok=True)
    for rel in ['script/narration.ko.json','script/narration.en.json','production/timeline.json','production/caption-alignment-final.json']:
        target=baseline/Path(rel).name
        if not target.exists():target.write_bytes((P/rel).read_bytes())
    outputs={};mapping=[]
    titles={'01':'분석에서 플레이 가능한 기반 프로토타입까지','02':'REA의 역할과 전체 도구 연결','08':'같은 제작 흐름으로 아이디어를 시험하기'}
    for lang,base in [('ko',ko),('en',en)]:
        result=copy.deepcopy(base);result.update(status='user-selected-workflow-first-v4',revision='v4',actualDurationSeconds=None)
        result.pop('draftSha256',None);result['draftSource']='planning/revision-v4-workflow.json'
        for scene in result['scenes']:
            sid=scene['id'];old_scene=next(x for x in base['scenes'] if x['id']==sid)
            if sid in titles:scene['title']=titles[sid]
            if sid in ['01','02','08']:
                records=[NEW[key] for key in NEW if key[0]==sid]
                display=[r[0 if lang=='ko' else 1] for r in records]
                lines=[spoken(x) for x in display] if lang=='ko' else display.copy()
                if sid=='02':
                    lines+=old_scene['lines'];display+=old_scene.get('displayLines',old_scene['lines'])
                scene['lines']=lines;scene['displayLines']=display
            if lang=='ko':
                for number,line in enumerate(scene['lines'],1):
                    item={'scene':sid,'paragraph':number}
                    if (sid,number) in NEW:item.update(mode='synthesize',reason='User requested REA explanation and workflow-first thesis')
                    else:item.update(mode='reuse',baselineScene=sid,baselineParagraph=number-2 if sid=='02' else number)
                    mapping.append(item)
        outputs[lang]=result;save(P/f'script/revision-v4/narration.{lang}.json',result)
    revision={'schemaVersion':1,'revision':'v4','authorizedAt':datetime.now(timezone.utc).isoformat(),
        'userRequest':'REA에 대한 설명이 빠졌어. 처음에 이 구조로 리버스 엔지니어링해서 게임의 기반 프로토타입을 빠르게 만드는 것을 소개하는 영상이다.',
        'thesis':'Use reverse-engineering evidence and AI-connected creation tools to reach a playable base prototype quickly.',
        'revisionScope':'New result-led opening, full toolchain overview, REA/agent/MCP explanation, workflow-focused conclusion. Preserve the useful observed-rule/implementation body and exact reused PCM.',
        'scripts':{'ko':'script/revision-v4/narration.ko.json','en':'script/revision-v4/narration.en.json'},
        'baseline':{'captionedSha256':'75dd9914af58ab4ac28f4489a76c197ccb6a84f4038837acb487cf01fbd213ec','audio':'production/local/audio-v1/narration.wav','timing':'production/local/audio-v1/narration.timing.json','timeline':'production/local/revision-v3-inputs/timeline.json'},
        'audioReuseMapping':mapping,'newParagraphs':5,'reusedParagraphs':14,
        'actualRoute':['REA6.8.0 CLI','readableGDScript rule analysis','AI independently authored rules and tests','BlenderPython originalmodels','Godot4.7.2 playableprototype'],
        'genericOptionalTools':['Ghidra for relevant native analysis','engine-specific resource inspection','TripoMCP for new3Dassets','Unity/Unreal/Godot as implementation destinations'],
        'accuracy':['REA is Reverse Engineer Anything, a tool/workflow layer used by an AI agent, not the model itself','Ghidra and Tripo were not executed in this experiment','No measured wall-clock speedup or automatic complete-game clone claim','Resource structure inspection is distinct from reusing original assets'],
        'visualPlan':['Actualoriginal/prototype split comparison at opening','Progressivefullworkflowmap','AIagent request→REAtool→evidence response illustration','Optionalgenerictools vs actualroute distinguished by text and line style','Existingbodyevidence reused','Closingreturns toactualroute andplayablegoal'],
        'sources':'planning/rea-explainer-v4.json','platformMutationAuthorized':False,'humanFinalApproval':False}
    save(P/'planning/revision-v4-workflow.json',revision)
    manifest=read(P/'project.json');manifest.update(status='revision-v4-production',publishReady=False)
    manifest['revision']={'id':'v4','reason':revision['userRequest'],'baselineReview':'User requested workflow/REA correction; no final approval'}
    manifest['titleKo']='기존 게임을 분석해 새 게임의 기반을 만든다면? — REA와 AI 프로토타입';manifest['titles']['ko']=manifest['titleKo']
    save(P/'project.json',manifest)
    cp=read(P/'production/checkpoint.json');cp.update(stage='revision-v4-script-and-reuse-preparation',updatedAt=revision['authorizedAt'],inProgress=['Workflow-firstv4/REA explanation and five new TTS paragraphs'],pending=['Render and inspect selected v4 locally; keep v3 retained','User final local review'],humanFinalReview=False)
    cp['revisionPlan']='planning/revision-v4-workflow.json';save(P/'production/checkpoint.json',cp)
    control=read(ROOT/'shared/publishing/video-production-control.json');control['scopedSetupAuthorizations'][P.name].update(status='revision-v4-production',revisionUserEvidence=revision['userRequest'],humanReview=False);save(ROOT/'shared/publishing/video-production-control.json',control)
    work=read(ROOT/'shared/publishing/video-worklist.json');row=next(r for r in work['rows'] if r.get('id')=='S-BUCKSHOT-RE');row.update(productionComplete=False,productionStatus='v4: REA·전체 제작 흐름 도입 보강 중',reviewStatus='v3 수정 요청 반영 중; v4 검수 전',executionStatus='선택 수정본 로컬 제작 중');save(ROOT/'shared/publishing/video-worklist.json',work)
    print(json.dumps({'paragraphs':len(mapping),'synthesize':5,'reuse':14,'oldOutputsPreserved':True}))
if __name__=='__main__':main()
