"""Preserve prepared v1/v2 history and add meaningful final-paragraph guide motion."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas'; folder=MC/'src/projects/player-customization'
src=folder/'observation-guide-explanation-v2.tsx'; dest=folder/'observation-guide-explanation-v3.tsx'
assert not dest.exists(), 'Preserve prepared follow-up; do not regenerate.'
code=src.read_text('utf-8')
replacements={
 "world.add(actor(()=>-660+500*u(0),-170,30,P.blue))":"world.add(actor(()=>-660+500*u(0)+190*u(3),-170,30,P.blue))",
 "[-390,-100].forEach(x=>world.add(target(x,-170,0)));world.add(actor(-500,170,30,P.green));":"[-390,-100].forEach(x=>world.add(target(x,-170,0)));world.add(actor(-500,170,30,P.green));world.add(s.path(()=>[[-100,-170,35],[155,-170,35]],P.blue,()=>u(3)));",
 "world.add(label('시작',-550,-165,P.blue));world.add(label('공간',0,-120));world.add(label('대상',520,-110,P.green));":"world.add(label('시작',-550,-165,P.blue));world.add(label('공간',0,-120));world.add(label('대상',520,-110,P.green));\n  world.add(<Node opacity={()=>u(3)}>{token(()=>-425+890*u(3),-75,150,P.green,'●')}{s.path(()=>[[-420,-75,151],[470,-75,151]],P.green,()=>u(3))}</Node>);",
 "world.add(s.box(545,145,30,65,65,200,'#c5ccd3'));world.add(label('높이 차이',-420,-190,P.blue));world.add(label('아래의 대상',440,-140,P.green));":"world.add(s.box(545,145,30,65,65,200,'#c5ccd3'));world.add(label('높이 차이',-420,-190,P.blue));world.add(label('아래의 대상',440,-140,P.green));\n  world.add(<Node opacity={()=>u(3)}>{token(-410,40,()=>55+250*u(3),P.green,'●')}{s.path(()=>[[-410,40,65],[-410,40,310]],P.green,()=>u(3))}</Node>);",
 "const x=()=>-430+560*u(1),y=()=>-100+170*u(1);":"const x=()=>-430+560*u(1)+120*u(3),y=()=>-100+170*u(1)-130*u(3);",
 "world.add(label('다른 위치에서 겨냥',-400,-230,P.blue));world.add(label('대상 배치',470,-205,P.green));":"world.add(label('다른 위치에서 겨냥',-400,-230,P.blue));world.add(label('대상 배치',470,-205,P.green));\n  world.add(<Node opacity={()=>u(3)}>{actor(()=>-570+260*u(3),()=>180-360*u(3),30,P.green)}{s.path(()=>[[-570,180,45],[-310,-180,45]],P.green,()=>u(3))}</Node>);",
 "world.add(label('목적',-540,-170,P.blue));world.add(label('행동으로 후보 구분',45,-145));world.add(label('목적에 맞는 시험',605,-110,P.green));":"world.add(label('목적',-540,-170,P.blue));world.add(label('행동으로 후보 구분',45,-145));world.add(label('목적에 맞는 시험',605,-110,P.green));\n  world.add(<Node opacity={()=>u(3)}>{token(()=>90+465*u(3),100,140,P.green,'●')}{s.path(()=>[[630,205,45],[40,205,45]],P.green,()=>u(3),[15,10])}</Node>);",
 "world.add(actor(-330,80,()=>30+60*u(1),P.green));world.add(s.path(()=>[[-620,-90,90],[-330,80,90]],P.green,()=>u(1)));":"world.add(actor(-330,80,()=>30+60*u(0),P.green));world.add(s.path(()=>[[-620,-90,90],[-330,80,90]],P.green,()=>u(0)));",
 "world.add(actor(205,140,30,P.blue));world.add(target(625,-100,2));world.add(token(()=>260+325*u(2),()=>115-185*u(2),125,P.blue,'▲'));":"world.add(actor(205,140,30,P.blue));world.add(target(625,-100,1));world.add(token(()=>260+325*u(1),()=>115-185*u(1),125,P.blue,'▲'));",
 "world.add(token(705,0,()=>30+95*u(3),P.green,'✓'));":"world.add(token(705,0,()=>30+95*u(3),P.green,'✓'));world.add(s.path(()=>[[645,0,70],[500,0,70]],P.green,()=>u(3)));"
}
for a,b in replacements.items():
    assert code.count(a)==1,a
    code=code.replace(a,b)
dest.write_text(code,'utf-8')
for p in sorted((folder/'observation-guide-scenes-v1').glob('*.tsx')):
    text=p.read_text('utf-8');assert "../observation-guide-explanation-v2" in text
    p.write_text(text.replace('../observation-guide-explanation-v2','../observation-guide-explanation-v3'),'utf-8')
config=MC/'tsconfig.player-customization.guides-v1.json'
d=json.loads(config.read_text('utf-8'));assert any('observation-guide-explanation-v2.tsx' in x for x in d['include'])
d['include']=[x.replace('observation-guide-explanation-v2.tsx','observation-guide-explanation-v3.tsx') for x in d['include']]
config.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
cmd=['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','node_modules/typescript/bin/tsc','--noEmit','--project',config.name]
r=subprocess.run(cmd,cwd=MC,capture_output=True,text=True)
record=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),status='prepared-final-paragraph-motion-awaiting-measured-render',
    historicalHelperV1Preserved=True,historicalHelperV2Preserved=True,helper=dest.relative_to(ROOT).as_posix(),helperSha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
    originalGuideKoEnUnchanged=True,actualTtsNotRestarted=True,actualGuideVoiceTimingMeasured=False,
    changes=['09 extends the actor/path at the final comparison instead of a frozen path.',
        '10 carries a new spatial marker from origin through the target connection during the preview instruction.',
        '11 moves a height marker vertically to explain the position relation during the final observation instruction.',
        '12 moves the center/ring relative to the nearby targets during the final test instruction.',
        '13 keeps the target arrangement fixed and moves a green comparison actor between two caster positions.',
        '14 takes the chosen candidate to the test and draws a return path toward the choice.',
        '15 aligns support recovery to the support paragraph and projectile motion to the attack paragraph; its final return path is retained.',
        '16 moves a confirmation marker toward the preview actor.'],
    command=cmd,typecheckExitCode=r.returncode,typecheckStdout=r.stdout,typecheckStderr=r.stderr,
    scope='Own guide wrapper/helper imports and own prepared white-fix project only; not a full workspace pass.',
    actualGuideDepthPixelsApproved=False,finalPairPixelsApproved=False,bodyRatioApproved=False)
(BASE/'observation-guides-final-paragraph-motion-prepared-v3.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(helper=record['helper'],typecheckExitCode=r.returncode,actualRenderApproved=False),ensure_ascii=False))
assert r.returncode==0,r.stdout+r.stderr
