"""Record observed saved card/monetization without completing the transfer."""
from pathlib import Path
from datetime import datetime, timezone
import json

root = Path(__file__).resolve().parents[3]
target = root / 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/youtube-upload-v3.json'
record = json.loads(target.read_text('utf-8-sig'))
assert record['actualVideoId'] == '2kNMDlrwdU8'
assert record['englishMetadata']['status'] == 'published-and-full-title-description-reopened'
assert not record['uploaded'] and not record['baselineScheduleChanged']
record['monetization'] = {
    'actualReopenedStatus': '사용',
    'automaticMidrollChecked': True,
    'manualAdSlotInserted': False,
    'evidence': 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/monetization-reopened-v3.ax.txt',
}
record['coachingCard'].update({
    'reopenedVerified': True,
    'fullCanonicalUrlDirectlyRead': True,
    'timeAndTitleCallToActionTeaserReopened': True,
    'evidence': 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/coaching-card-reopened-v3.ax.txt',
})
record['detailsReopenedDuringTransfer'] = {
    'fullKoTitleDescriptionDirectlyRead': True,
    'part1CourseWikiCoachingDiscordMembershipLinksRetained': True,
    'actualPlaylist': '게임 수학(Game Math) PART 2',
    'uploadedThumbnailButtonObserved': True,
    'actualFinalThumbnailPixelsReviewed': False,
    'actualPrivacyDisplay': '대기 중',
    'transferPercentHistoricalObservation': 53,
    'remainingMinutesHistoricalObservation': 28,
}
record['updatedAt'] = datetime.now(timezone.utc).isoformat()
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'cardReopened': True, 'automaticMidrollSaved': True,
                  'uploadComplete': False, 'allSettings': False, 'baselineChanged': False}))
