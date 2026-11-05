"""KO/EN clause pairs for the paragraphs whose V6 audio read a numerical worked example."""
LESSONS = {
6:[
 ("이 구에 닿은 빛은 어떤 색으로 돌아올까요?", "What color does light take when it reflects from this sphere?"),
 ("빛의 색과 표면의 색에는 각각 빨강, 초록, 파랑 성분이 있습니다.", "Both the incoming light and the surface color have red, green and blue components."),
 ("식의 동그라미 곱은 같은 색 성분끼리 곱한다는 뜻이에요.", "The circled product multiplies matching color channels."),
 ("표면은 그대로 두고 빛의 초록 성분만 올려 볼게요.", "Keep the material fixed and raise only the green component of the light."),
 ("구에서 초록빛만 더 강해집니다. 방향을 비교하는 내적과는 다른 계산이죠.", "Only the green contribution grows. This is different from comparing directions with a dot product.")],
10:[
 ("이제 구에 닿은 빛이 어느 쪽으로 나가는지 따라가 보죠.", "Now follow the light as it leaves the sphere."),
 ("법선은 표면에 수직이고, 엘은 표면에서 광원을 향합니다.", "The normal is perpendicular to the surface. L points from the surface toward the light."),
 ("빛이 들어오는 방향은 엘과 반대예요.", "The incoming ray points opposite to L."),
 ("반사식은 법선을 기준으로 입사 방향을 뒤집어, 나가는 방향 알을 정합니다.", "Reflection mirrors the incoming direction about the normal to produce R."),
 ("그래서 셰이더의 반사 함수에는 마이너스 엘과 법선을 넣습니다.", "That is why the shader reflection function takes minus L and the surface normal.")],
12:[
 ("반짝임의 폭을 정하는 건 광택 지수입니다.", "The shininess exponent controls the width of the highlight."),
 ("반사 방향과 시선 방향이 얼마나 일치하는지를 먼저 구해요.", "First find how closely the reflection and viewing directions align."),
 ("빛과 카메라는 고정하고, 구 옆의 지수만 올려 볼게요.", "Keep the light and camera fixed and raise only the exponent beside the sphere."),
 ("정확히 일치하는 중심은 밝게 남고, 비껴난 부분부터 어두워집니다.", "The aligned center stays bright while the less aligned region darkens."),
 ("그래서 반짝이는 자리가 점점 좁아져요. 이 폭과 반짝임의 세기는 따로 조절할 수 있습니다.", "The highlight narrows. Its width and strength can be controlled separately.")],
20:[
 ("그렇다면 표면이 빛을 얼마나 정면으로 받는지 어떻게 구할까요?", "How can we tell how directly light strikes a surface?"),
 ("법선과 광원 방향을 같은 길이로 맞추고 내적을 구합니다.", "Normalize the surface normal and the direction toward the light, then take their dot product."),
 ("두 방향이 나란하면 빛을 정면으로 받고, 벌어질수록 덜 받죠.", "Aligned directions mean head-on light. As they separate, less light arrives."),
 ("그 값이 음수이면 빛이 뒷면에서 오는 거예요.", "A negative value places the light behind the surface."),
 ("이때 앞면에 더할 양은 영으로 막습니다. 이제 이 양을 표면색에 반영해 볼게요.", "Clamp the contribution to zero. Next, apply that illumination to the surface color.")],
21:[
 ("같은 색의 무광 구를 그대로 두고, 빛이 오는 방향만 옮겨 볼게요.", "Keep the matte sphere and its color fixed and move only the light direction."),
 ("식에서 재질색은 표면이 어떤 색을 돌려주는지, 광원색은 어떤 빛이 도착하는지 나타냅니다.", "Material color specifies what the surface reflects, and light color what arrives."),
 ("두 색에 앞서 구한 각도의 효과를 곱하면, 같은 표면점이 비스듬한 빛에서 어두워집니다.", "Multiplying both colors by the angular factor darkens the same surface point under grazing light."),
 ("여기서 단위 면적에 들어오는 빛을 이레디언스라고 합니다.", "Incoming power per unit surface area is irradiance.")],
30:[
 ("빛을 등진 쪽의 굴곡까지 보여주고 싶을 때는 이 응답을 바꿀 수 있습니다.", "To reveal form on the unlit side, we can change the lighting response."),
 ("하프 램버트는 법선과 광원 방향의 내적을 밝기로 바꾸는 방식을 조절해요.", "Half Lambert changes how the normal-light dot product maps to brightness."),
 ("구와 조명은 같은데, 옆면의 밝기가 더 오래 남는 걸 보세요.", "The sphere and light are the same, yet the side of the sphere stays visible for longer."),
 ("식의 제곱은 그 밝기 변화를 다시 다듬습니다.", "Squaring the remapped response shapes that transition."),
 ("다른 벽에서 돌아온 빛을 구한 게 아니라, 형태가 읽히도록 직접광의 표현을 바꾼 겁니다.", "This shapes the direct-light response to reveal form. It does not compute bounced light.")],
39:[
 ("삼각형 안쪽의 한 점은 어떤 색으로 칠할까요?", "What color should we assign to a point inside the triangle?"),
 ("구로 셰이딩은 먼저 각 꼭짓점에서 조명을 계산해 색을 정합니다.", "Gouraud shading evaluates the lighting at each vertex to obtain its color."),
 ("식에서 씨는 꼭짓점의 색, 람다는 그 색이 섞이는 비중이에요.", "Each C is a vertex color. Each lambda is the weight of that color."),
 ("점이 밝은 꼭짓점 쪽으로 옮겨 가면 그 꼭짓점의 비중이 커집니다.", "As the point moves toward the brighter vertex, that vertex carries more weight."),
 ("그렇게 꼭짓점 사이 색이 부드럽게 이어지죠. 그럼 꼭짓점에 없는 반짝임은 어떨까요?", "This produces a smooth transition. What happens if the highlight misses every vertex?")],
42:[
 ("퐁 조명 모델은 반짝임을 구하는 식이고, 퐁 셰이딩은 그 식을 픽셀에서 계산하는 방식입니다.", "The Phong reflection model gives the highlight formula. Phong shading evaluates the lighting at each pixel."),
 ("여기서 궁금한 건 같은 구라도 계산 순서를 바꾸면 반짝임이 같을까 하는 거예요.", "Would the same sphere have the same highlight if we changed the order of operations?"),
 ("왼쪽은 꼭짓점에서 밝기를 구한 뒤 그 색을 섞고, 오른쪽은 법선을 먼저 섞고 나서 밝기를 구합니다.", "On the left we blend the colors computed at the vertices. On the right we blend the normals first, then compute the brightness."),
 ("빛을 옮기면 오른쪽에는 꼭짓점 사이에도 반짝임이 맺히죠. 조명식에 거듭제곱이 들어가서 두 순서의 결과가 달라집니다.", "Move the light and a highlight can appear between vertices on the right. The nonlinear lighting response makes the order matter.")],
44:[
 ("같은 표면에 여러 조명이 비칠 때는 어떤 계산을 한 번만 해도 될까요?", "When several lights illuminate the same surface, which calculation can we do just once?"),
 ("식의 케이는 그 점의 재질색이고, 디는 각 광원이 보태는 빛입니다.", "Here k is the material color at the point, and each D is a light contribution."),
 ("같은 픽셀에서는 어떤 광원을 보더라도 재질색이 같습니다.", "At the same pixel, every light shares that material color."),
 ("그래서 빛의 기여를 먼저 합치고, 재질색을 한 번만 곱해도 색이 같아요.", "So we can sum the lights and multiply by the material color once, obtaining the same color."),
 ("이 분배법칙을 난반사와 정반사에 각각 쓰고, 환경광도 같은 재질색을 쓰면 난반사 쪽에 묶습니다.", "Apply this separately to diffuse and specular terms. Ambient can share the diffuse group when it uses the same material color.")],
53:[
 ("점 광원에서 멀어지면 같은 표면이 왜 어두워질까요?", "Why does a surface become darker as it moves away from a point light?"),
 ("광원이 내보낸 빛은 바깥으로 갈수록 더 넓은 구면을 지나갑니다.", "Light from the source crosses larger concentric spheres as it travels outward."),
 ("광원의 출력과 표면의 방향은 그대로인데, 같은 면적이 받아 가는 몫이 줄어요.", "With the same source power and surface orientation, each unit of area receives a smaller share."),
 ("구면의 넓이가 거리의 제곱에 비례하므로, 표면이 받는 양은 거리의 제곱에 반비례합니다.", "Sphere area grows with the square of distance, so the received power density falls with its inverse square.")],
58:[
 ("게임에서 빛이 닿는 범위를 직접 정하고 싶다면 경계 두 개를 씁니다.", "To author the range of a game light, choose two boundaries."),
 ("안쪽 경계까지는 밝기를 유지하고, 바깥 경계에 닿으면 빛의 기여가 사라져요.", "The light retains its full strength inside the inner boundary and vanishes at the outer boundary."),
 ("식에서 디는 광원과 표면 사이의 거리입니다.", "Here d is the distance from the light to the surface."),
 ("두 경계는 고정하고 거리만 늘리면, 그 사이에서 구의 밝기가 고르게 줄어듭니다.", "Fix both boundaries and increase only the distance. The sphere dims steadily in between."),
 ("이건 빛의 범위를 연출하기 위한 선형 감쇠입니다.", "This is linear attenuation, an artistic way to control the light's range.")],
61:[
 ("둠 쓰리에서 표면의 한 점을 비출 때는 두 종류의 무늬를 읽습니다.", "To illuminate one point in Doom 3, the renderer samples two patterns."),
 ("고보는 가로세로 어디로 빛이 나갈지를 정하고, 감쇠 맵은 깊이에 따라 얼마나 남길지를 정해요.", "The gobo determines where the light falls across the pattern. The falloff map determines how much remains with depth."),
 ("셰이더는 두 값을 곱합니다. 고보에서 어두운 곳은 깊이가 같아도 어두워요.", "The shader multiplies the samples. A dark region of the gobo stays dark even at the same depth."),
 ("그럼 표면의 위치로 두 무늬의 어디를 읽을지 어떻게 알까요?", "How does a position on the surface tell us where to sample the two patterns?")],
64:[
 ("그림의 어느 부분을 읽을지, 상자 안의 위치를 텍스처 좌표로 바꿔 보겠습니다.", "To select a part of the pattern, convert a position inside the box to texture coordinates."),
 ("엑스는 중심에서 잰 가로 위치, 에스 엑스는 상자의 전체 폭이에요.", "x is horizontal position relative to the center. s-x is the full box width."),
 ("폭을 고정한 채 점을 오른쪽으로 옮기면, 텍스처를 읽는 위치도 오른쪽으로 움직입니다.", "With the width fixed, moving the point right also moves the sampled texture coordinate right."),
 ("세로축의 부호는 여기서 그림의 아래쪽을 양의 방향으로 쓰기 때문에 뒤집어요.", "The vertical sign flips because this example uses downward-positive texture coordinates."),
 ("월드 좌표라면 먼저 광원 기준의 좌표로 바꿔야 합니다.", "First transform a world-space point into the light's coordinate system.")],
}
