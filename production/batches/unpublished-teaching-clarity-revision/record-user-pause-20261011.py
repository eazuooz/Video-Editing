import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
now = datetime.now(timezone(timedelta(hours=9))).isoformat()
request = '새로만들어진 영상 업로드됬으면 기존영상은 삭제해줘 유튜브에서 그리고 새로만들어진거 예약날짜 기존꺼랑 맞춰주고 작업은 일단 멈춰줘 토큰없거든 다음주에 차면 다시 진행할게'
pause = {
    'schemaVersion': 1, 'recordedAt': now, 'status': 'paused-by-user',
    'userEvidence': request, 'automationId': '24', 'automationStatus': 'PAUSED',
    'resumeRequiresUserInstruction': True, 'automaticNextWeekResume': False,
    'newProductionAllowed': False,
    'remainingAuthorizedAction': 'Verify completed replacement uploads, match previous schedules and delete only their corresponding obsolete YouTube IDs.',
    'localMediaAndCheckpointsPreserved': True, 'foreignResearchModified': False,
    'activeOwnedTtsAsrRenderWorkersObserved': 0,
    'orientation': {
        'ttsSession54946ActualExitCode': 0,
        'researchResumeVerification': 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1/research-handoff-verification-v2.json',
        'resumedResearchQueuePid': 84232,
        'annotationV2ActualExitCode': 0,
        'structuralV1ActualExitCode': 0,
        'pending': ['whole6-current-PCM-ASR', '22-independent-context-review', 'structural-scene12-and18-layout-repair', 'measured-final-edit-and-all-delivery-gates'],
        'replacementActualId': None,
    },
}
path = ROOT / 'production/USER_VIDEO_WORK_PAUSE.json'
path.write_text(json.dumps(pause, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
qpath = ROOT / 'production/batches/unpublished-teaching-clarity-revision/queue.json'
q = json.loads(qpath.read_text(encoding='utf-8-sig'))
q['mode'] = 'paused'
q['userPause'] = {'recordedAt': now, 'record': str(path.relative_to(ROOT)).replace('\\', '/'), 'resumeRequiresUserInstruction': True}
q['updatedAt'] = now
qpath.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
cpath = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1/latest-checkpoint.json'
c = json.loads(cpath.read_text(encoding='utf-8-sig'))
c['userPause'] = q['userPause']
c['paused'] = True
cpath.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'paused', 'record': str(path), 'productionStarted': False}, ensure_ascii=False))
