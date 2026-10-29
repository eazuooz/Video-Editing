"""Update only this authorized project's checkpoint and worklist row."""
from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checkpoint = read(PROJECT / "production/checkpoint.json")
checkpoint.update({
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "stage": "original-playback-comparison-and-documentary-production",
    "completed": [
        "User start authorization on 2026-10-29; single local documentary scope",
        "REA 6.8.0 read-only inventory: 3572 embedded members, 195 readable GDScripts, engine package 4.1.1",
        "Ten independently paraphrased rule findings with byte-range/hash evidence; no decompiler used",
        "Independently authored rule core: 374 checks passed",
        "Original Blender assets: ten GLBs and editable generation source",
        "Godot 4.7.2 actual GPU stage validation and animation checks",
        "Main scene integration: 32 checks passed, deterministic demo executed",
        "OBS original-game recording saved and decoded as 1920x1080 60fps H264 with 48kHz AAC",
        "Per-process original game save isolation prepared and original save hashes recorded"
    ],
    "inProgress": ["Original gameplay observations and shot selection", "Prototype FHD capture", "Evidence-based narration and editing"],
    "pending": ["Final narration generation and speech review", "Four final local outputs", "Final audiovisual QA and selective Git delivery"],
    "evidenceLimits": [
        "374 rule checks and 32 integration checks cover our independent implementation, not full equivalence to the original game",
        "Original runtime observations must be linked to actual recorded timestamps before making runtime claims",
        "No final documentary master or human final review yet",
        "Ghidra and Tripo were not used; REA inspected shipped readable scripts rather than decompiling them"
    ]
})
write(PROJECT / "production/checkpoint.json", checkpoint)
manifest = read(PROJECT / "project.json")
manifest["rendererDecision"]["prototype"] = "Godot 4.7.2 GL Compatibility; independently authored rules, scene and original Blender GLBs"
manifest["capture"].update({"userOBSRecordingConfirmed": True, "firstOriginalRecording": "captures/recordings/buckshot-process-2026-10-29_09-15-02.mkv", "firstOriginalRecordingSeconds": 425.77, "firstOriginalRecordingVerified": "1920x1080,60/1,H264,AAC48000; decoded frame checked"})
write(PROJECT / "project.json", manifest)
worklist = read(ROOT / "shared/publishing/video-worklist.json")
for value in worklist.values():
    if not isinstance(value, list):
        continue
    for row in value:
        if isinstance(row, dict) and row.get("id") == "S-BUCKSHOT-RE":
            row.update({"productionStatus": "원작 촬영·규칙 분석·독립 프로토타입 구현 완료 범위 확인; 전체 영상 제작 중", "reviewStatus": "규칙374·통합32검사 통과; 영상 최종 검수 전", "humanApproval": "2026-10-29 응 진행해줘~로 실제 제작 승인; 완성본 시청 승인 전", "executionStatus": "한 편 로컬 제작 진행; 자동화·업로드 없음"})
write(ROOT / "shared/publishing/video-worklist.json", worklist)
md = ROOT / "docs/VIDEO_WORKLIST.md"
text = md.read_text(encoding="utf-8-sig")
start = "<!-- BUCKSHOT-RE-SETUP-20261028-START -->"
end = "<!-- BUCKSHOT-RE-SETUP-20261028-END -->"
a, b = text.index(start), text.index(end) + len(end)
block = """<!-- BUCKSHOT-RE-SETUP-20261028-START -->
## 벅샷 룰렛 리버스 엔지니어링 실험

| 영상 | 분석·구현 | 실제 촬영 | 검수 | 상태 |
|---|---|---|---|---|
| [벅샷 룰렛 분석·독립 재구현](../output/buckshot-roulette-reverse-engineering/index.html) | REA 3,572파일·195스크립트 확인; 독립 규칙·모델·애니메이션 구현 | 원작 1080p60 촬영 확인; 결과 대조·새 게임 촬영 중 | 규칙374·통합32검사 통과; 완성영상 검수 전 | 2026-10-29 사용자 착수 승인. 한 편 로컬 제작 진행 |

원작과의 완전한 동등성 검증·완성 영상·사용자 최종 시청은 아직 완료하지 않았다. 업로드·자동 다음 영상은 하지 않는다.
<!-- BUCKSHOT-RE-SETUP-20261028-END -->"""
md.write_text(text[:a] + block + text[b:], encoding="utf-8")
print("Updated selected project and S-BUCKSHOT-RE row only.")
