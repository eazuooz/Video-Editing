"""Adopt only the four individually inspected, mathematically verified native studies."""
from prepare import HERE, WORK, read, save

NOTES = {
 'A03': 'Original Spear Attack 02 and run clips. The four simultaneous phase poses and weapon swing remain; no hand-made joint motion was found in the source audit.',
 'A09': 'Original ComboHands joint rotations remain identical on every frame. Hand scale is the explicitly taught variable; the ball/volume demonstrations are geometric diagrams.',
 'A13': 'Original walk and flashlight clips. Reviewed foot progression, reflected hands and held prop, plus the synchronized observer view. Retain the native performance and explicit mathematical reflection.',
 'A16': 'Original Spear Attack 04 joint rotations on every frame. Reviewed swing, overhead view and active interval; only the documented collision/display parameters vary.',
}


def main():
    for ep, note in NOTES.items():
        audit = read(WORK / ep / 'native-source-audit.json')
        samples = read(WORK / ep / 'retained-native-sampling/samples.json')
        assert audit['sourceMotionVerified'] and samples['samples']
        assert audit['pictures']['captioned.mp4']['sha256'] == samples['sourceSha256']
        save(WORK / ep / 'native-picture-review.json', {
            'episode': ep, 'visualReviewPassed': True, 'pictures': audit['pictures'],
            'nativeMotionSourceVerified': True, 'reviewScope': 'Every-frame source-pose checks plus encoded temporal contact-sheet inspection; no human final viewing claimed.',
            'decision': note, 'sourceAudit': str(WORK / ep / 'native-source-audit.json'),
            'encodedSamples': str(WORK / ep / 'retained-native-sampling/samples.json'),
            'humanReviewed': False})
    print('Retained native bodies adopted:', ', '.join(NOTES))


if __name__ == '__main__':
    main()
