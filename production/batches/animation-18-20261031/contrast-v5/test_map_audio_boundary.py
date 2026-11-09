"""Real A13 virtual EDL regression; no media encoding or shared plan writes."""
import assemble_explanations as a

def rejects(fn):
    try:fn()
    except AssertionError:return True
    raise AssertionError('An actual protected-region overlap was allowed')

def main():
    manifest=a.read(a.INTEGRATION);ep=next(x for x in manifest['episodes']if x['id']=='A13')
    maps=a.protected_map_audio(ep);m=next(x for x in maps if x['kind']=='map')
    planfile=a.H/'local/final-audio/A13/audio-plan.json';plan=a.read(planfile)
    g=next(x for x in plan['groups']if x['id']=='A13-speech-009')
    assert(g['startSample'],g['baselineStartFrame'],g['deltaFrames'])==(4162864,5204,25)
    assert g['placements'][0]['offsetSample']==2880 and g['placements'][0]['take']['fullTakeRetained']and g['placements'][0]['take']['speed']==1
    assert g['newSamples']==g['endSample']-g['startSample']+g['deltaFrames']*800
    a.protect_map_pcm(g,maps)
    rejects(lambda:a.protect_map_pcm({**g,'startSample':m['endSample']-1},maps))
    picture={'id':g['id']+'-picture','kind':'retimed-authored-explanation','startFrame':g['baselineStartFrame'],
        'endFrame':g['baselineEndFrame'],'newFrames':g['extensionRequirement']['requiredPictureFrames'],'picture':'virtual-test-fixture-only',
        'sourceVerified':True,'testFixtureOnly':True}
    a.picture_override('A13',picture,[],ep['preservedRelationRegions'])
    rejects(lambda:a.picture_override('A13',{**picture,'startFrame':5203},[],ep['preservedRelationRegions']))
    base=next(x for x in a.read(a.BASE)['records']if x['id']=='A13');total=base['frames']
    video=a.core.picture_edl(total,'unchanged-real-baseline',[],[picture])
    audio,samples=a.audio_edl(total*800,[{**g,'kind':'replace-complete-mix'}],'unchanged-real-baseline-pcm')
    assert video[0]['outputEndFrame']==5204 and audio[0]['outputEndSample']==4162864
    assert video[0]['sourceStartFrame']==0 and audio[0]['sourceStartSample']==0
    assert samples==video[-1]['outputEndFrame']*800==(total+25)*800
    assert g['startSample']-picture['startFrame']*800==-336
    all_ranges=[]
    for e in manifest['episodes']:
        ranges=a.protected_map_audio(e);all_ranges.append({'id':e['id'],'ranges':ranges})
        for q in ranges:
            rejects(lambda q=q,ranges=ranges:a.protect_map_pcm({'startSample':q['endSample']-1,'endSample':q['endSample']+1},ranges))
    receipt={'passed':True,'scope':'Real current A13 virtual edit plan and all17 protected map/repair ranges; no encode or listening',
        'audioPlanSha256':a.sha(planfile),'map':m,'groupId':g['id'],'groupMixSha256':g['sourceSha256'],
        'audioStartSample':g['startSample'],'pictureStartFrame':g['baselineStartFrame'],'pictureAudioOffsetSamples':-336,
        'deltaFramesAppliedOnce':25,'fullTakeUncut1x':True,'prefixPaddingSamples':2880,'allMapPcmAndPicturePreserved':True,
        'oneSampleAudioOverlapRejected':True,'oneFramePictureOverlapRejected':True,'bodyRepairGuardsRetained':True,
        'all17RangeProofs':all_ranges,'totalSamplesMatchFrames':True,'renderStarted':False,'humanListening':False}
    a.save(a.L/'map-audio-boundary-test.json',receipt)
    print('PASS: A13 audio4162864 / picture5204, -336sample offset, +25frames once; map and repair guards retained')

if __name__=='__main__':main()
