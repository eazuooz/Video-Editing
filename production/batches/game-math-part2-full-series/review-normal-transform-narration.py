"""Record only complete raw readbacks directly reviewed for this lecture."""
from pathlib import Path
import json, hashlib, sys
from datetime import datetime, timezone
R = Path(__file__).resolve().parents[3]
slug = 'game-math-normal-transform-uv'
sys.argv = [sys.argv[0], slug]
import align as a
import soundfile as sf
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m = read(R / f'projects/{slug}/project.json')
out = R / m['tts']['outputDir']
script = read(R / m['paths']['script'])
notes = {
    '02': 'All seven newly line-synthesized paragraphs directly compared in full: column-vector tangent/normal, invertible linear M and no translation, inverse transpose and commuting inverse/transpose, cancellation to dot0, orthogonal rotation and positive uniform-scale normalization, nonuniform/shear and singular zero-axis limitation, and reflection/front-face caveat with positive-scale example retained. No unrequested goodbye remains. 상세/상쇄,한사/반사,안면/앞면 and 임으로/이므로 are explicit phonetic ASR variants; every condition,zero and negation retained. Human listening pending.',
    '03': 'All seven current repaired paragraphs directly compared in full: t(1,-1),n(1,1),dot0; Mdiag2,1 produces t2,-1; wrong normal2,1 gives3; wrong unit normal still gives3/sqrt5; explicit1dividedby2=.5 and normal(.5,1) now unambiguously read with dot0; normalized(.447,.894), correct-direction-before-unit-length,2D-to3D and distinct lighting normalmatrix retained. The original reciprocal reversal is absent. 정규화에도/정규화해도,기울기에/기울기가 and 임으로/이므로 are explicit phonetic ASR variants. Every component,sign,division,dimension and negation checked against the independent math; human listening pending.',
    '01': 'Complete four-sentence overview directly compared: scaled-object question, perpendicular tangent/normal and inverse-transpose numeric example, UV correspondence/crop/rotation/flip, then repeat/clamp and interpolation-before-addressing all retained. 유브이/UV is ASR spelling; human listening pending.',
    '04': 'All six complete paragraphs compared: Megabonk rocks/building walls, stable outline while viewpoint moves, lighting versus surface markings, subsequent low rocks/desert/front-side views, unknown proprietary UV data, previous perpendicular calculation and distinct geometry/normal/image-address data retained. 기하 and 수치 예제 have phonetic ASR spelling variants; no numerical value or negation lost. Human listening pending.',
    '05': 'Current passing-wave complete five paragraphs compared after the acoustic retry: Sunset roofs/windows, outline versus detail and no vertex-count inference, brick/grid correspondence, unknown proprietary texture/address mode, and an original four-vertex plate with independent image selection retained. Initial 자 is a filler; 기하/기아,네/내 and 의/에 are explicit ASR variants. Human listening pending.',
    '06': 'All seven complete paragraphs compared: texel versus output pixel, magnification/minification contributions, declared Uhorizontal/Vdown and corner(0,0)/(1,1), explicit convention rather than API assumption,8x8 versus normalized0to1 independent of3Dpositions, planar/cylinder/sphere mapping and per-vertex storage, then interpolation with prior perspective correction retained. 정규와/정규화,보관/보간,원금/원근 and 맵핑/매핑 are explicit phonetic ASR variants; their audible pronunciation is not independently verified. All bounds and negations retained. Human listening pending.',
    '07': 'All seven complete paragraphs compared: cloth-pin analogy and four vertices, corner pairs00/10/11/01, unchanged geometry, central0.25to0.75crop, UVcorner cycling rather than rotating3Dplate,1-Uhorizontalflip preserving positions/winding, general triangle correspondence and explicit nonphysical/non-area-preserving analogy retained. 내/네 and LatinU/V/UV are readback variants. All numbers, ordered corners and negations checked. Human listening pending.',
    '08': 'All six complete paragraphs compared: red curvedwall markings, changing projected slope/scale versus image coordinates, slopedroof then container top/sidepanel direction, unknown realUV values and connection to defined original examples, full/subimage correspondence and0to1bounds, and no inference of repeataddressmode from visibly repeating marks retained. 의/에 and 기하/기아 are ASR variants; the final clause omits the redundant noun 무늬 after repeating-pattern context but retains image-internal repetition and the same result. No number, condition or negation missing. Human listening pending.',
    '09': 'All seven complete paragraphs compared: BigWalk greenroom/characters and backpanelgrid/roundmarks, projectedlines versus surfacecoordinates, continuous marks during motion, no repeataddressmode or triangleconnectivity inference, original defined UV/address example, interpolatebeforelookup and prematurevertexwrapping error retained. The propername is transcribed 아스픽워크 rather than 빅워크 and 보관/보간,위에/위의 are explicit ASR variants; correct source identity is recorded independently and audible propername remains for human listening. No numerical or algorithmic condition missing. Human listening pending.',
    '10': 'All seven complete paragraphs compared: out-of0to1UVs, repeatfloor rule,1.25-floor1=.25 and negative.75-floor(-1)=.25, truncationtowardzero differs, clampbelow0/above1 and edge continuation, alternatingmirror tiles and independentU/Vaddressmode, address versus filtering and explicitboundaryconventions retained. 이웃텍셀/이후택셀 and 이므로/임으로 are phonetic ASR variants. Every value/sign and conditional boundary checked against independent math; human listening pending.',
    '11': 'All six repaired paragraphs directly compared in full: repeated original endpoints0andexplicitnumber2 now retained at every mention;quarterU.5andthreequarterU1.5 lookup to.5, prematurevertexrepeat collapses both endpoints to0 and allinteriorUto0, lost0to2span and interpolatebeforelookup, and separateperspectivecorrection retained. 보관/보간,의/에,임으로/이므로 and LatinU/UV are explicit ASR variants. Full-scene decoder appends 다음영상에서만나요 with only.06s total and two0duration words; exact unchanged9.92s final-line WAV independently transcribed by the same CPUWhisper reviewer retains both complete approved sentences and no goodbye. This is recorded as an inferred decoder artifact with raw evidence preserved in asr-zero-duration-tail-review.json; no listening approval implied. Every endpoint/interior value,condition and algorithmic order checked; human listening pending.',
    '12': 'All six complete paragraphs compared: Sunset stair/building traversal, near/farboundaries, outline/light/pattern questions, repeatedwindows/panels without vertexcount or addressmode inference, separate index/normal/UVroles, silhouette then normalboundary then textureinspection, and a definedmesh calculation rather than guessing proprietary numbers retained. 뒤에/뒤의,맞추는/맞히는 and 의/에 are explicit ASR variants; no mathematicalvalue or negation lost. Human listening pending.',
    '13': 'All six current repaired recap paragraphs directly compared in full:4vertices*32bytes+6indices*2bytes=140; duplicate coincident vertexattributes and update faceindices for sharpnormalboundary; explicit tangentcomponents2and-1,normalcomponents.5and1 and dot0 now unambiguous; perpendicularity plus unitlength afternonuniformscale;0to2UVs interpolatebeforelookup and floornegativecoordinates; distinct index/normal/UVroles and possibleattribute separation; subsequentlight/material lesson bridge retained. 보관/보간 is an explicit ASR variant; all components,memoryvalues,bounds,signs,negations and proceduralorder retained. No prior ambiguous 이를 remains. Human listening pending.',
}
P = R / f'projects/{slug}/production'
file = P / 'narration-review-in-progress.json'
previous = read(file) if file.exists() else {'scenes': []}
rows = {s['scene']: s for s in previous['scenes']}
for s in script['scenes']:
    sid = s['id']
    rawfile = out / f'asr/{sid}.json'
    wave = out / f'chunks/{sid}-scene.wav'
    if sid not in notes or not rawfile.exists(): continue
    raw = read(rawfile)
    assert sha(wave) == raw['audio_sha256']
    samples, sr = sf.read(wave)
    expected = ' '.join(s['lines'])
    _, _, coverage = a.a.align_characters(expected, raw['words'], len(samples) / sr)
    rows[sid] = {'scene': sid, 'wavSha256': sha(wave), 'rawAsrSha256': sha(rawfile),
        'expected': expected, 'recognized': raw['text'], 'matchingCharacterCoverage': coverage,
        'agentMeaningNumberReview': 'passed', 'notes': notes[sid]}
pending = [s['id'] for s in script['scenes'] if s['id'] not in rows]
record = {'status': 'partial-direct-full-raw-readback-review', 'humanListening': 'pending',
    'reviewedAt': datetime.now(timezone.utc).isoformat(),
    'scenes': [rows[k] for k in sorted(rows)], 'pendingScenes': pending,
    'ambiguousNumberScenes': [sid for sid in ['03', '11', '13'] if sid in pending],
    'requiredOmissionRetakeScenes': [sid for sid in ['02', '03', '11', '13'] if sid in pending]}
file.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print({'directlyReviewed': sorted(rows), 'pending': pending})
