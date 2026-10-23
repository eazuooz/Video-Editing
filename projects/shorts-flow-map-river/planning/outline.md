# 게임 속 강물은 어떻게 바위를 피해 흐를까?

## 1. Flowing river around stationary rock; reveal texture-based effect

이 물결, 바위를 피해 돌아가죠. 물을 전부 시뮬레이션한 걸까요? 이 장면은 물결 그림을 움직여 만든 겁니다.

## 2. Uniform scrolling crosses obstacle; switch to authored field arrows

그냥 한쪽으로 밀면, 무늬가 바위도 그대로 통과합니다. 그래서 위치마다 움직일 방향을 화살표로 따로 정해 두죠.

## 3. Show sampled RG texture, decode signed vector; neutral→right worked example

이 방향 지도가 플로 맵입니다. 우리 지도는 빨강에 가로, 초록에 세로 방향을 담아요. 두 값이 절반이면 정지, 빨강만 최대로 올리면 오른쪽입니다.

## 4. Same map drives water shader around rock; arrows track same map samples

셰이더는 이 값을 읽고, 물결 그림을 가져올 위치를 조금씩 옮깁니다. 바위 주변의 화살표를 휘게 그렸으니, 무늬도 갈라져 돌아가는 거죠.

## 5. One stretching phase versus two staggered reset phases

그런데 계속 늘리면 무늬가 찌그러집니다. 그래서 짧게 움직이고 되감되, 엇갈린 두 무늬를 번갈아 섞어서 되감는 순간을 감춰요.

## 6. Move rock without changing map, then update map; visible correction

바위를 옮겨도 새 길이 저절로 생기진 않아요. 방향 지도도 바꿔 줘야 합니다. 물의 모든 움직임 대신, 보이는 흐름을 설계한 겁니다.
