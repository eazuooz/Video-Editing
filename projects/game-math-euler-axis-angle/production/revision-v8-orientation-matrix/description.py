"""Local bilingual description using the measured V8 clock; never uploads."""
from pathlib import Path
import importlib.util
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_desc_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
def stamp(seconds):
 n=int(seconds);return f'{n//3600}:{n//60%60:02}:{n%60:02}' if n>=3600 else f'{n//60:02}:{n%60:02}'
def main():
 c.authorized();t=c.read(H/'timeline.json');en=c.read(c.S/'narration.en.json');out=c.P/'publishing';out.mkdir(exist_ok=True)
 chaptersKo=['00:00 게임은 물체의 기울기를 어떻게 기억할까?'];chaptersEn=['00:00 How does a game remember an object’s tilt?']
 englishTitles=['Direction and orientation','A reference orientation','Coordinate frames and basis axes','Building and using a rotation matrix','The inverse and transpose','Which matrix do we need?','Components, dot products and direction cosines','Reading all nine entries','Transforming points and composing matrices','Storage cost','Constraints on a pure rotation','Invalid matrices and numerical drift','What a rotation matrix records']
 for s,title in zip(t['scenes'][1:],englishTitles[1:]):chaptersKo.append(stamp(s['start'])+' '+s['title']);chaptersEn.append(stamp(s['start'])+' '+title)
 references='''
자료·게임 화면 출처
3D Math Primer — Orientation and Multiple Coordinate Spaces
https://gamemath.com/book/orient.html
https://gamemath.com/book/multiplespaces.html
Modern Robotics — Rotation Matrices
https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-1-rotation-matrices-part-1-of-2/
젤다의 전설 티어스 오브 더 킹덤 독립 게임 녹화 — Royalty Free Game Clips
https://www.youtube.com/watch?v=YNQ20CKbY8U
게임 저작권: Nintendo. 녹화물 사용 허용과 게임 자체의 권리는 구분합니다.
설명 모형·도식·계산 애니메이션: 얌얌코딩 제작(Unity·Manim).
'''
 ko='''앞은 같은 곳을 보는데 날개는 기울어져 있다면, 같은 방향일까요, 같은 자세일까요?
물체에 붙은 세 축을 따라가며 자세(Orientation)가 회전행렬로 표현되는 과정을 설명합니다. 행렬의 각 숫자를 축의 성분과 내적으로 읽고, 작은 좌표 변환부터 역변환·합성·저장 비용·오차까지 차근차근 연결합니다.

범위: 게임수학 파트2의 8.1 자세부터 8.2.5 행렬 표현 정리까지.
이 영상의 약속: 왼손 좌표계, 가로로 쓴 행벡터, 물체 좌표 → 바깥 기준 좌표. 다른 자료의 열벡터 약속과는 구분해 봐 주세요.
게임 위 표식은 설명용 안내입니다. 숫자와 행렬은 직접 구현한 설명 모형의 값이며 게임 내부 데이터를 측정한 것이 아닙니다.

'''+ '\n'.join(chaptersKo)+'\n'+references
 english='''An airplane can point forward while its wings tilt. Its direction stays the same, but its orientation changes.
Follow the three axes attached to an object to see how a rotation matrix records orientation. We connect the entries to axis components and dot products, then work through coordinate changes, the inverse, composition, storage cost, and numerical error.

Scope: sections8.1–8.2.5, orientation through the summary of matrix representation.
Convention used here: a left-handed coordinate system, row vectors, and object-to-upright coordinates. A column-vector convention uses a transposed table for the same coordinate transformation.
Gameplay marks are editorial guides. Numbers and matrices come from our authored explanatory model, not measurements of the game’s internal data.

'''+ '\n'.join(chaptersEn)+'\n'+references.replace('자료·게임 화면 출처','References and gameplay credits').replace('젤다의 전설 티어스 오브 더 킹덤 독립 게임 녹화','Independent The Legend of Zelda: Tears of the Kingdom gameplay').replace('게임 저작권: Nintendo. 녹화물 사용 허용과 게임 자체의 권리는 구분합니다.','Game copyright: Nintendo. Permission for the recording does not transfer rights in the underlying game.').replace('설명 모형·도식·계산 애니메이션: 얌얌코딩 제작(Unity·Manim).','Explanatory models, diagrams and calculations: Yamyam Coding (Unity and Manim).')
 files=[]
 for lang,text in [('ko',ko),('en',english)]:
  file=out/f'revision-v8-description.{lang}.txt';file.write_text(text,encoding='utf8');files.append(dict(language=lang,file=c.rel(file),sha256=c.sha(file)))
 c.save(H/'description-manifest.json',dict(timelineSha256=c.sha(H/'timeline.json'),files=files,creditsAtBottom=True,platformMutation=False));print('Prepared exact-clock bilingual descriptions; no upload.')
if __name__=='__main__':main()
