"""Record only scenes whose entire raw readback was directly compared.

Unreviewed scenes and ambiguous numerical readings stay pending.
"""
from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];slug='game-math-mesh-uv'
sys.argv=[sys.argv[0],slug]
import align as a
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(R/f'projects/{slug}/project.json');out=R/m['tts']['outputDir'];script=read(R/m['paths']['script'])
notes={
 '01':'Complete four-sentence overview compared with raw readback:3Dshape/light information, roofs/rocks,indexed memory,face/vertex normals,complete accumulation,sharp edges,triangulation bias and defined-mesh verification retained.3차원/삼차원 and 메쉬/메시 are readback spellings; no numerical claims changed.',
 '02':'All five paragraphs compared: real roof traversal,outline versus panel lines,other roof/vents,no hidden edge or vertex-count inference,and original defined-mesh example retained. Extra 자 filler and 게임 표면의/표면에,기아/기하 are explicitly visible readback spelling differences. No calculated number or negation is lost; human listening remains pending.',
 '03':'Complete six paragraphs compared:CSGunion/intersection/difference,bored volume example,metaballs/implicit-volume context,open triangle surfaces,valid triangulation and vertex/edge/face relationships retained. 기아/기하 and 이전장에서 spacing are readback spelling differences, not independently verified listening.',
 '04':'Complete changed-wave raw readback directly compared:defined vertices0,1,2,3 (four total),triangles012/023,duplicated0/2,32-byte vertex and2-byte index,6×32=192 versus4×32+6×2=128+12=140,and separate local32+6×2=44 all retained. The revised paragraph explicitly reads six two-byte indices,total twelve,with no eleven-byte ambiguity. Raw 0,1,2,3,4개 is the vertex-label list followed by its four-count,not five positions. 산순/단순 is a phonetic ASR variant. All attributes and scope distinctions remain. Human listening pending.',
 '05':'All seven paragraphs compared:attribute identity,declared clockwise/APIfrontface rule,012→120same direction versus021opposite,shared edge02,implicit adjacency,winged-edge alternatives,boundary1face/nonmanifoldmore-than2,compatible render batches and editor/GPU distinction retained. 배치/매치 is a phonetic readback difference. Every index,comparison and negation checked against the independent math audit.',
 '06':'All seven full paragraphs compared with the raw readback:green grid and curved wall/cylinder,outline versus surface marks,unknown proprietary topology,defined indices0and2,unchanged surface/changed normal and transition to face/vertex normals retained. 위의/위에 and 뒤의/뒤에 are particle differences; no calculated index or negation is missing. Human listening pending.',
 '07':'All six full paragraphs compared:faceted rocks/cacti,unchanged outline while camera moves,unknown hidden normals,materials/shadows affecting brightness,positions versus lighting input,and the original hexagonal-prism comparison retained. 맞히는/맞추는 and 기둥에/기둥의 are readback variants. No proprietary numerical normal claim is inferred.',
 '08':'All six paragraphs directly compared:cross product/front-face/unit length,nonunique sharp-corner face normal,smooth-surface shading normals,unchanged prism positions/indices,unit normal-light cosine and normalization,and separate culling/shading diagnostics retained. Raw 공면/곡면,정교화/정규화 and 쉐이딩/셰이딩 are explicit phonetic spelling differences; agent readback review does not verify their audible pronunciation and human listening remains pending.',
 '09':'All seven paragraphs directly compared:Gouraud interpolates vertex lighting,per-pixel shading interpolates then normalizes directions;blend(0.5,0.5),length~0.707 and unit components~0.707 all correct;Phong shading versus reflection-model distinction and unchanged silhouette retained. 보관/보간,정교화/정규화 are explicit phonetic ASR variants. Raw 2단계 corresponds to the script 이 단계를 거칩니다,which references the just-demonstrated normalization and is not a new two-step numerical assertion. Human listening pending.',
 '10':'All three full paragraphs compared:red deck,curved railing/sloped panel,geometry versus smooth lighting,and collect connected faces then split required boundaries all retained. No numerical claim or negation changed.',
 '11':'All seven paragraphs directly compared:yellow walls/round opening,changing brightness and shadow versus actual opening,character traversal revealing thickness,unknown hidden vertex count/algorithm,full accumulation,constant versus continuous normals,and hard-edge separation all retained. Only word spacing changed.',
 '12':'All seven paragraphs directly compared:zero accumulators,cross of two edges,degenerate near-zero rejection,unit face added to each of three triangle indices,(1,1,1)/sqrt3 with each component~0.577,normalize after all faces,zero/opposing/isolated policies,and equal-face-vote caveats retained. 퇴와/퇴화,정교화/정규화 and 새/세 are explicit phonetic ASR variants; the three-index meaning and all numeric values were checked against the independent audit. Human listening pending.',
 '13':'Complete current replacement readback directly compared with all seven paragraphs:three faces at a corner,smoothing brightness without changing the cube silhouette,hard-edge separation,eight unique positions versus six faces times four records per face=24 total records,distinct top-facing normal in the top-face record and side-facing normal in the side-face record,matching indices,UV seam attributes,opposing-normal zero and front/back policy,unchanged coordinates and separately preserved editor connectivity all retained. The revised two complete directional sentences are both present. No unrequested farewell or subtitle-credit phrase appears in this current raw readback. 그래서 connective omitted and 꼭지점/꼭짓점,입/잎 are explicit ASR differences; no condition or calculated value lost. Human listening pending.',
 '14':'All six full paragraphs directly compared:two top triangles versus two side faces,(1,2,1) and normalized(0.408,0.816,0.408),unchanged quad with different diagonal,90degrees split still90,angle weighting and alternative area policy,and hard-edge splitting before smooth averaging retained. 정교화/정규화 and 꼭지점/꼭짓점 are explicit phonetic readback variants. All signs,components,vote counts and degrees independently checked.',
 '15':'All seven full paragraphs directly compared:yellow opening,outline retained despite smooth brightness,unknown proprietary record count,separate top/side directions versus smooth neighbors,no unconditional minimization or averaging,and the next episode transformed-tangent dot-product exercise retained. 앞에/앞의 and 공면/곡면 are explicit phonetic/particle ASR differences; human audible pronunciation remains unverified.',
 '16':'All five full paragraphs directly compared:four32-byte vertices plus six2-byte indices=140,whole versus local scope,complete attribute identity,initialization→valid face→three-vertex accumulation→final normalization,zero/degenerate guards,hard edges/weights/unchanged silhouette,and inverse-transpose/UV next episode retained. 유효하면/유효한 면,새/세,퇴하면/퇴화 면 and 둥그러지는/둥글어지는 are explicit phonetic ASR variants. Counts4,32,6,2,140 and all negations verified; human listening pending.'
}
P=R/f'projects/{slug}/production';file=P/'narration-review-in-progress.json'
previous=read(file) if file.exists() else {'scenes':[]}
rows={s['scene']:s for s in previous['scenes']}
for s in script['scenes']:
 sid=s['id'];rawfile=out/f'asr/{sid}.json';wave=out/f'chunks/{sid}-scene.wav'
 if sid not in notes or not rawfile.exists():continue
 raw=read(rawfile);assert sha(wave)==raw['audio_sha256']
 import soundfile as sf
 audio,rate=sf.read(wave);expected=' '.join(s['lines'])
 _,_,coverage=a.a.align_characters(expected,raw['words'],len(audio)/rate)
 rows[sid]={'scene':sid,'wavSha256':sha(wave),'rawAsrSha256':sha(rawfile),'expected':expected,'recognized':raw['text'],'matchingCharacterCoverage':coverage,'agentMeaningNumberReview':'passed','notes':notes[sid]}
pending=[s['id'] for s in script['scenes'] if s['id'] not in rows]
record={'status':'partial-direct-full-raw-readback-review','humanListening':'pending','reviewedAt':datetime.now(timezone.utc).isoformat(),'scenes':[rows[k] for k in sorted(rows)],'pendingScenes':pending,'ambiguousNumberScenes':[],'requiredOmissionRetakeScenes':[sid for sid in ['13'] if sid in pending]}
file.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print({'directlyReviewed':sorted(rows),'pending':pending,'numericRetakePending':[]})
