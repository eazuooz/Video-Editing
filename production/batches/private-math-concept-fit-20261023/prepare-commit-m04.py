from common import *
paths=[]
folders=[B]
for slug in ['game-math-euler-axis-angle','game-math-quaternion-foundations-v3']:
 P=R/'projects'/slug;folders +=[P/'production/concept-fit-v2',P/'script/concept-fit-v2',P/'publishing/revisions/concept-fit-v2']
for folder in folders:
 paths +=[rel(x) for x in folder.rglob('*') if x.is_file() and x.suffix in ['.py','.json','.md','.txt','.srt'] and '__pycache__' not in x.parts and not x.name.endswith('-commit.json')]
shared=['shared/publishing/video-worklist.json','docs/GAME_MATH_PRIVATE_POLISH.md','projects/game-math-euler-axis-angle/project.json']
paths+=shared
save(B/'m04-complete-commit.json',dict(paths=sorted(set(paths)),sharedPaths=shared,message='Polish Euler lecture with matched object actions and prepare quaternion revision'))
print(len(set(paths)),'owned paths')
