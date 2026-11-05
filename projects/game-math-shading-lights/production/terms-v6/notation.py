"""Content for the English-first headings and the paired typeset equations and code.
Equations use the light/view convention of the original M21 material-sphere experiment.
The snippet is explanatory pseudocode unless an intrinsic is explicitly named."""
from dataclasses import dataclass

# Short forms keep the canonical term and its translation on one line on a phone.
TITLES = {
    1: ('Physically Based Rendering · PBR', '물리 기반 렌더링'),
    2: ('BRDF', '양방향 반사 분포 함수'),
    4: ('Light Source', '광원'),
    6: ('Hadamard Product', '성분별 곱'),
    8: ('Unit Vectors', '단위 벡터'),
    15: ('Specular Strength & Shininess', '정반사 세기와 광택 지수'),
    17: ('Blinn–Phong Reflection', '블린–퐁 반사'),
    23: ('Lambertian BRDF', '램버트 양방향 반사 분포 함수'),
    28: ('Lighting Components', '조명 성분'),
    31: ('Multiple Lights', '여러 광원의 합'),
    32: ('Local Illumination', '국소 조명'),
    33: ('Blinn–Phong Reflection', '블린–퐁 반사'),
    34: ('Light Visibility', '광원 가시성'),
    35: ('Fresnel Effect & Retroreflection', '프레넬 효과와 재귀반사'),
    39: ('Gouraud Shading', '구로 셰이딩'),
    40: ('Gouraud Shading', '구로 셰이딩'),
    47: ('Light Sources', '광원의 종류'),
    48: ('Point Light', '점 광원'),
    54: ('Irradiance', '복사조도'),
    55: ('Radiance', '복사휘도'),
    57: ('Inverse-Square Falloff', '역제곱 감쇠'),
    59: ('Spotlight Angular Falloff', '스폿 광원의 각도 감쇠'),
    61: ('Light Cookie', '광원 쿠키'),
    66: ('Projective Texture Clipping', '투영 텍스처 범위 제한'),
    67: ('Orthographic Projection', '직교 투영'),
    68: ('Light Volume', '광원 영향 영역'),
    70: ('Lightmap Atlas', '라이트맵 아틀라스'),
    72: ('Directional Irradiance', '방향별 복사조도'),
    73: ('Spherical Harmonics · SH', '구면 조화 함수'),
    74: ('Baked Lighting', '베이크 조명'),
    77: ('Environment Lighting', '환경 조명'),
    78: ('Light and Shading', '빛과 셰이딩'),
}

# Translate by complete concepts, never by generic strings such as "조도" inside another term.
TERMS = [
 ('양방향 반사 분포 함수','BRDF'),('램버트 BRDF','Lambertian BRDF'),
 ('하프웨이 벡터','Halfway Vector'),('평면 셰이딩','Flat Shading'),('플랫 셰이딩','Flat Shading'),
 ('구로 셰이딩','Gouraud Shading'),('퐁 셰이딩','Phong Shading'),
 ('퐁 반사 모델','Phong Reflection Model'),('복사휘도','Radiance'),('복사조도','Irradiance'),
 ('복사속','Radiant Flux'),('복사발산도','Radiant Exitance'),('라디오시티','Radiosity'),
 ('입체각','Solid Angle'),('라이트 프로브','Light Probe'),('라이트맵','Lightmap'),
 ('구면 조화 함수','Spherical Harmonics'),('디랙 델타','Dirac Delta'),
 ('광택 지수','Shininess Exponent'),('직교 투영','Orthographic Projection'),
 ('원근 투영','Perspective Projection'),('동차 좌표','Homogeneous Coordinates'),
]
# A first-use caption can use a short form if another canonical name is already in the same clause.
# Native educational images, unaffected paragraphs and all editorial gameplay marks remain underneath.
@dataclass(frozen=True)
class Pair:
    equation: str
    code: tuple
    notes: tuple
    onset: float = 0.0

def pair(eq, code, notes, onset=0.0):
    return Pair(eq, tuple(code.split('|')), tuple(notes.split('|')), onset)

PAIRS = {
 5:pair(r'C=C_e+C_s+C_d+C_a','color = emit + spec|      + diffuse + ambient;','스스로 내는 빛 → 발광|반짝이는 빛과 넓게 퍼지는 빛|간접광의 근사까지 더해요.'),
 6:pair(r'\mathbf{C}=\mathbf{C}_{l}\odot\mathbf{C}_{m}','rgb = lightRGB * materialRGB;','광원 (1, 0.5, 0.2)|재질 (0.8, 0.4, 0.1)|빨강 1 × 0.8 = 0.8|초록 0.5 × 0.4 = 0.2|파랑 0.2 × 0.1 = 0.02'),
 9:pair(r'\mathbf{R}=2(\mathbf{N}\cdot\mathbf{L})\mathbf{N}-\mathbf{L}','R = reflect(-L, N);','L을 법선 위로 투영해요.|p = (N·L)N|투영한 성분을 두 배로|R = 2p − L',4.8),
 10:pair(r'\mathbf{R}=2(\mathbf{N}\cdot\mathbf{L})\mathbf{N}-\mathbf{L}','R = reflect(-L, N);','N = (0, 1, 0)|L = (0.6, 0.8, 0)|N·L = 0.8|2(N·L)N = (0, 1.6, 0)|R = (−0.6, 0.8, 0)',4),
 11:pair(r'S=\max(0,\mathbf{R}\cdot\mathbf{V})^{n}','s = pow(max(0, dot(R,V)), n);','R과 V는 단위 벡터|같은 방향에서 내적은 1|아래 값은 구의 표면점에서 계산',2),
 12:pair(r'0.8^{2}=0.64,\quad 0.8^{8}\simeq0.17','s = pow(0.8, exponent);','정렬된 방향에서는 1ⁿ = 1|지수가 커질수록 폭이 좁아져요.'),
 16:pair(r'\mathbf{H}=\frac{\mathbf{L}+\mathbf{V}}{\Vert\mathbf{L}+\mathbf{V}\Vert}','H = normalize(L + V);','L과 V의 길이는 1|서로 정반대라면 합은 0|합의 길이가 0일 때는 별도 처리',4),
 17:pair(r'S=\max(0,\mathbf{N}\cdot\mathbf{H})^{n}','s = pow(max(0, dot(N,H)), n);','하프웨이 벡터 H를 사용해요.|N과 H가 가까울수록 밝아요.|L + V = 0이면 H를 만들 수 없어요.'),
 20:pair(r'd=\max(0,\mathbf{N}\cdot\mathbf{L})','d = max(0, dot(N,L));','0° → 1|60° → 0.5|90° → 0|뒷면의 값도 0',.5),
 21:pair(r'\mathbf{C}_{d}=(\mathbf{k}_d\odot\mathbf{I})\max(0,\cos\theta)','rgb = kd * lightRGB * d;','흰빛 세기 1|재질 (0.8, 0.4, 0.2)|60° → 기여가 절반|결과 (0.4, 0.2, 0.1)'),
 22:pair(r'f_r=\frac{\rho}{\pi}','brdf = albedo / PI;','ρ는 표면이 반사하는 비율|반구의 코사인 가중 적분은 π|따라서 (ρ/π) × π = ρ',2),
 23:pair(r'\mathrm{d}L_o=L_i\,f_r\,\cos\theta\,\mathrm{d}\omega','dLo = Li * brdf * cosTheta * dOmega;','앞면에 들어오는 한 방향의 기여|입사광 × BRDF × 코사인|램버트 BRDF에 1/π가 이미 포함'),
 30:pair(r'h=\left(\frac{\mathbf{N}\cdot\mathbf{L}+1}{2}\right)^2','t = 0.5*dot(N,L) + 0.5;|h = t*t;','옆면에서 N·L = 0|램버트 값 0|Half Lambert 값 0.25'),
 31:pair(r'C=C_e+C_a+\sum_j(D_j+S_j)','color = emission + ambient;|color += sumDiffuseAndSpecular;','광원마다 D와 S를 계산해요.|발광과 환경광은 한 번만 더해요.'),
 32:pair(r'C=C_e+C_a+C_d+C_s','color = emit + ambient|      + diffuse + spec;','네 성분을 따로 조절해요.|픽셀 수와 광원 수를 함께 고려'),
 39:pair(r'C(P)=\lambda_0 C_0+\lambda_1 C_1+\lambda_2 C_2','color = w0*c0 + w1*c1 + w2*c2;','Cᵢ는 정점에서 계산한 색|λᵢ는 코드의 wi · 가중치 합은 1|삼각형 중심에서는 각각 ⅓|(0.2 + 0.4 + 0.6) / 3 = 0.4|세 정점의 최대값은 0.6'),
 41:pair(r'\mathbf{N}(P)=\frac{\sum_i\lambda_i\mathbf{N}_i}{\Vert\sum_i\lambda_i\mathbf{N}_i\Vert}','N = normalize(interpolatedN);|color = shade(N);','정점의 법선을 보간|단위 길이로 맞춘 뒤 픽셀에서 계산'),
 42:pair(r'\left(\frac{0+1}{2}\right)^2\ne\frac{0^2+1^2}{2}','a = pow((0+1)/2.0, 2);|b = (0*0 + 1*1)/2.0;','입력은 0과 1|평균을 먼저 구하면 0.25|제곱을 먼저 구하면 0.5'),
 43:pair(r'\sum_i(\mathbf{k}\odot\mathbf{D}_i)=\mathbf{k}\odot\sum_i\mathbf{D}_i','color = material * sumLight;','텍스처는 픽셀에서 읽어요.|같은 픽셀의 재질값 k는 공통'),
 44:pair(r'0.8(0.2+0.3)=0.16+0.24=0.4','color = 0.8 * (0.2 + 0.3);','광원 기여 0.2와 0.3|재질 0.8을 따로 곱해도|합친 다음 곱해도 결과는 0.4'),
 45:pair(r'C=k_d\odot D+k_s\odot S+C_e','color = kd*D + ks*S + emission;','D와 S는 보간한 조명값|두 재질색은 픽셀에서 읽어요.|환경광은 D에 포함된 약속'),
 46:pair(r'd=\mathbf{N}_{w}\cdot\mathbf{L}_{w}','d = dot(worldN, worldL);','법선과 광원 방향은 같은 공간|같은 방향의 단위 벡터 → 1|좌표 공간이 다르면 먼저 변환'),
 48:pair(r'd=\Vert Q-P\Vert,\quad\mathbf{L}=\frac{Q-P}{d}','delta = lightPos - surfacePos;|L = delta / length(delta);','P는 표면점, Q는 점 광원|d > 0일 때 단위 방향을 계산'),
 53:pair(r'E(2r)=\frac{1}{4}E(r)','E2 = E1 * 0.25;','등방성 점 광원, 정면 입사|거리가 2배 → 구면 넓이는 4배|같은 넓이에 도착하는 빛은 ¼'),
 54:pair(r'E=\frac{\mathrm{d}\Phi_{\mathrm{in}}}{\mathrm{d}A}','Eavg = incomingPower / area;','Radiant Flux (복사속) Φ · W|Irradiance (복사조도) E · W/m²|등방성 점 광원, 수직 입사|E = Φ / (4πr²)|거리 2배 → E는 ¼'),
 55:pair(r'L=\frac{\mathrm{d}^2\Phi}{\mathrm{d}A_{\perp}\,\mathrm{d}\omega}','Lavg = power / (projArea * omega);','여기서 L은 복사휘도, A⊥는 투영 면적|ω는 입체각 · 단위 sr|작은 면적과 입체각에 대한 평균|Radiance · W/(m²·sr)'),
 56:pair(r'\mathrm{d}\omega=\frac{|\cos\theta_s|\,\mathrm{d}A_s}{r^2}','dOmega = cosAbs * dA / (r*r);','작은 광원 면적 dAₛ|θₛ는 광원 법선과 시선의 각도|멀수록 광원이 차지하는 입체각 감소'),
 57:pair(r'E=\frac{I}{r^2}\quad(r>0)','E = intensity / (r*r);','정면 입사를 가정해요.|r이 0에 가까우면 값이 급증|게임에서는 상한과 범위를 정해요.'),
 58:pair(r'a=\min\!\left(1,\max\!\left(0,\frac{r_o-d}{r_o-r_i}\right)\right)','a = saturate((outer-d)/(outer-inner));','안쪽 rᵢ = 2 m, 바깥 rₒ = 6 m|d ≤ 2 → 1 · d ≥ 6 → 0|d = 4 → (6−4)/(6−2) = 0.5'),
 61:pair(r'a=G\!\left(\frac{x}{w},\frac{y}{w}\right)F(z)','a = gobo(uv) * falloff(z);','고보는 가로·세로 무늬|감쇠 맵은 깊이|0.8 × 0.5 = 0.4'),
 62:pair(r'(u,v)=\left(\frac{x}{w},\frac{y}{w}\right)','uv = lightCoord.xy / lightCoord.w;','먼저 월드 위치를 광원 좌표로|x, y만 w로 나눠요.|감쇠 맵의 z는 따로 읽어요.'),
 64:pair(r'u=\frac{x}{s_x}+\frac{1}{2},\quad v=\frac{1}{2}-\frac{y}{s_y}','u = x/width + 0.5;|v = 0.5 - y/height;','폭 4 → x = −2에서 u = 0|중심 x = 0에서 u = 0.5|x = 2에서 u = 1|v의 부호는 이 예제의 UV 약속'),
 65:pair(r'(u,v)=\left(\frac{x}{w},\frac{y}{w}\right),\quad w=z','uv = projected.xy / projected.w;','이 예제에서는 w = z|멀어질수록 단면이 커져요.'),
 72:pair(r'E=\int_{\Omega^+}L_i(\omega)\max(0,\mathbf{N}\cdot\omega)\,\mathrm{d}\omega','E += Li * max(0, dot(N,wi)) * dOmega;','Lᵢ는 입사 Radiance (복사휘도)|E는 Irradiance (복사조도)|한 색에는 여러 방향의 합만 남아요.|Radiosity (라디오시티)는 출사량'),
}
