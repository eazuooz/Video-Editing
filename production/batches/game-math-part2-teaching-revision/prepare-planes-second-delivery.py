"""Prepare records for the observed second private upload and scoped Git delivery."""
from pathlib import Path
B=Path(__file__).parent
s=(B/'record-planes-first-platform.py').read_text(encoding='utf8')
s=s.replace('first plane lecture','second plane lecture').replace('game-math-plane-distances-v2','game-math-triangle-addresses-v2')
s=s.replace('Rzrt47-u4G0','wbZcFGzJMRg').replace('64ff63e99f6e004eada6d6726fefbf618c4796f17102cc640544fae2b13bd181','d10eb21fbf4afcf124adb5f0d7995168af508f04fd070a6702db4728eceb45cf')
s=s.replace('11:51:55','14:11:55').replace('12:01:55','14:21:55').replace('midrollEnabled=False','midrollEnabled=True')
s=s.replace('actual midroll checkbox unchecked','actual midroll checkbox checked')
start=s.index("item['status']=")
end=s.index("q['updatedAt']",start)
s=s[:start]+'''item['status']='both-private-episodes-reviewed; second-selective-git-and-schedule-transition-pending'
item['revision'].update(flowReviewPassed=True,annotationMotionReviewPassed=True,narrationComplete=True,
 renderComplete=True,localOutputsCollected=True,localPixelReviewComplete=True,wholeNativePlaybackComplete=True,
 firstEpisodePrivateUploadComplete=True,firstEpisodeFullPublishingSettingsComplete=True,
 secondEpisodePrivateUploadComplete=True,secondEpisodeFullPublishingSettingsComplete=True,
 privateUploadComplete=True,fullPublishingSettingsComplete=True,videoIds=['Rzrt47-u4G0','wbZcFGzJMRg'])
q['execution']['stage']='Both plane lectures actual reviewed private uploads and full available settings complete; second selective Git and schedule transition pending; polygon additive preparation active'
'''+s[end:]
s=s.replace('Recorded actual first plane','Recorded actual second plane')
(B/'record-planes-second-platform.py').write_text(s,encoding='utf8')
s=(B/'deliver-planes-first-git.py').read_text(encoding='utf8')
s=s.replace('planes-first','planes-second').replace('game-math-plane-distances-v2','game-math-triangle-addresses-v2')
s=s.replace('plane distance lecture','triangle address lecture').replace("['Rzrt47-u4G0']","['wbZcFGzJMRg']")
s=s.replace('firstEpisodeGitDelivered','secondEpisodeGitDelivered').replace('firstEpisodeGitCommit','secondEpisodeGitCommit').replace('firstEpisodeRemoteVerifiedSha','secondEpisodeRemoteVerifiedSha')
(B/'deliver-planes-second-git.py').write_text(s,encoding='utf8')
print('Prepared actual second plane platform-record and isolated Git helpers.')
