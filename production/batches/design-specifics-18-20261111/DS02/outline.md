# 버튼의 무게 | 같은 버튼인데 왜 어떤 캐릭터는 더 무겁게 느껴질까?

## 도입 · 손가락은 같고 반응은 다르다

같은 방향 버튼을 눌렀는데 한 캐릭터는 바로 출발하고, 다른 캐릭터는 몸을 움직인 뒤 속도가 붙습니다. 버튼을 놓으면 한쪽은 그 자리에서 서고, 다른 쪽은 조금 더 움직이죠. 손에 들어가는 힘은 그대로인데 두 캐릭터를 움직이는 느낌은 다릅니다. 화면이 만드는 이 차이를 출발, 정지, 다음 행동 세 순간에서 보겠습니다.

Press the same direction button and one character moves right away, while the other shifts their weight before picking up speed. Release it and one stops on the spot while the other keeps moving a little. The pressure on your finger stays the same, but controlling the two characters feels different. We can read the difference at three points: starting, stopping, and taking the next action.

실제 게임에서 출발과 감속의 차이가 보이는 동일한 카메라와 거리의 장면을 확보한 뒤 캐릭터명을 정한다. 대조된 행동은 입력값을 읽어 측정한 것처럼 표시하지 않는다.

## 속도 · 바로 움직이는가, 더 멀리 움직이는가

컨트롤러의 적응형 트리거처럼 누르는 저항 자체를 바꿀 수도 있습니다. 오늘 볼 차이는 화면에 나타납니다. 누른 뒤 얼마나 빨리 첫 움직임이 나오고, 속도가 얼마나 가파르게 붙고, 손을 뗀 뒤 얼마나 더 가는지가 한꺼번에 손맛을 만듭니다. 최고 속력이 같아도 출발과 정지가 다르면 버튼을 쓰는 리듬이 달라집니다.

An adaptive trigger can change the physical resistance under your finger. The difference here comes from the response on screen. Feel depends on how soon movement starts, how fast the character accelerates, and how far they travel after release. Two characters can have the same top speed and still call for different timing on the button.

여기서는 한 번에 한 조건만 바꿉니다. 먼저 오른쪽의 가속만 낮췄습니다. 누른 즉시 움직이기 시작하지만 같은 시간에 덜 멀리 갑니다. 다음으로 오른쪽의 감속만 낮추면 놓은 뒤에도 더 멀리 가죠. 점프의 상승과 낙하를 어떻게 잡는지도 비슷하게 조작감을 바꿉니다.

Change one condition at a time. First, the character on the right accelerates more gradually. Movement begins as soon as the button is pressed, but the character covers less ground in the same time. Then lower only the deceleration and the character moves farther after release. The way a jump rises and falls can change the feel in much the same way.

## 지연 · 움직이기 전의 시간

가속이 낮은 경우와 입력 지연은 화면에서 다르게 읽힙니다. 가속이 낮아도 작은 변화는 바로 시작합니다. 지연이 커지면 누른 시점과 첫 움직임 사이가 늘어납니다. 프레임 간격도 이 피드백을 언제 눈으로 받을지에 영향을 주죠. 누른 순간부터 첫 변화까지, 그리고 그 변화가 자라나는 구간을 따로 봐야 합니다.

Low acceleration and input latency leave different traces on screen. With low acceleration, a small change still starts right away. With more latency, the wait between the press and the first visible motion grows. Frame timing also affects when you get to see that response. Look separately at the wait before motion starts and at what the motion does after that.

자체 A/B 화면에서 입력과 첫 픽셀 변화, 속력 그래프의 기울기를 각각 붙인다. 동시에 바뀌는 값을 제한한다. 이어질 피드백 루프의 첫 연결을 표시한다.

## 피드백 · 눈과 귀로 느끼고 손으로 응답한다

손은 버튼을 누르고 게임은 그 입력을 받아 캐릭터를 움직입니다. 플레이어는 그 반응을 화면과 소리로 받아 다음 입력을 고릅니다. 버튼을 놓는 시점이 바뀌고, 다음 버튼을 누르는 간격도 바뀝니다. 화면 반응이 되돌아와 손의 행동을 바꾸는 이 순환이 조작감을 만듭니다.

Your hand presses a button, and the game turns that input into movement. You see and hear the response and use it to choose the next input. You might release earlier or wait longer before the next press. That loop from the hand through the game and back to the player shapes how the controls feel.

## 캐릭터 · 다음 행동까지의 간격

대전 게임에서는 속도만큼 다음 행동까지 남는 시간도 중요합니다. 한 캐릭터의 기술은 빠르게 끝나 다음 움직임을 선택하기 쉽습니다. 다른 캐릭터는 공격이 크게 뻗고, 그만큼 회수하는 시간 동안 상대에게 기회를 줍니다. 이 차이가 같은 버튼을 눌러도 다른 거리를 고르고 다른 타이밍에 위험을 감수하게 만듭니다.

In a fighting game, the time before your next action matters alongside speed. One character finishes a move quickly and can choose what to do next. Another makes a bigger commitment and gives the opponent an opening while recovering. That difference changes which distance and which risks you choose, even on the same button.

## 스틱 · 첫 입력이 잡히는 위치

버튼을 떠나 스틱으로 가면, 중심에서 얼마나 기울여야 입력으로 처리할지도 정해야 합니다. 중심에 아주 가까운 범위를 데드존으로 두면 스틱이 미세하게 흔들려도 캐릭터가 저절로 걷지 않습니다. 범위를 지나치게 넓히면 살짝 민 움직임도 늦게 시작하는 것처럼 느껴질 수 있습니다. 출발이 둔하게 느껴질 때는 캐릭터의 가속과 함께 입력이 언제부터 잡히는지도 확인해 보세요.

An analog stick adds another choice. How far from the center does it have to move before the game responds? A small dead zone prevents tiny movements around the center from walking the character by accident. Set it too wide and light stick movements can feel slow to register. If a character feels sluggish when starting, check when the input first registers as well as how the character accelerates.

검수 단계는 `independent footage and audio pending`. 실제 촬영에서 확인한 차이에 맞춰 예시 이름과 화면 큐를 확정한다.
