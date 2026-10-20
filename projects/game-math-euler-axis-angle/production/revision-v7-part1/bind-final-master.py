"""Bind the once-recognized AAC to a video-clock-only remux; no inference."""
from pathlib import Path
import hashlib, importlib.util, json
import av

H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v7_final_audio_binding_common', H / 'audio-common.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)

def audio_identity(file):
    plain = hashlib.sha256(); framed = hashlib.sha256(); clocks = []
    with av.open(str(file)) as source:
        stream = next(s for s in source.streams if s.type == 'audio')
        info = dict(codec=stream.codec_context.name, sampleRate=stream.codec_context.sample_rate,
                    channels=stream.codec_context.channels, timeBase=str(stream.time_base),
                    startTime=stream.start_time, duration=stream.duration)
        for packet in source.demux(stream):
            if packet.pts is None: continue
            payload = bytes(packet); plain.update(payload)
            framed.update(len(payload).to_bytes(8, 'big')); framed.update(payload)
            clocks.append([packet.pts, packet.dts, packet.duration])
    return dict(info, packetCount=len(clocks), packetPayloadSha256=plain.hexdigest(),
                framedPacketPayloadSha256=framed.hexdigest(),
                packetClockSha256=hashlib.sha256(json.dumps(clocks, separators=(',', ':')).encode()).hexdigest(),
                firstPacket=clocks[0], lastPacket=clocks[-1])

def main():
    c.selected(); frozen = H / 'final-asr-input.json'; selected = c.read(frozen)
    asr_file = c.O / 'final-master-asr.json'; asr = c.read(asr_file)
    provenance_file = c.O / 'final-master-audio-provenance.json'; provenance = c.read(provenance_file)
    assert asr['inputSha256'] == c.sha(frozen)
    assert asr['masterSha256'] == provenance['masterSha256'] == selected['masterSha256']
    proof_file = c.O.parent / 'edit/packet-clock.json'; proof = c.read(proof_file)
    row = next(x for x in proof['outputs'] if x['kind'] == 'captioned')
    original = c.R / row['original']; current = c.R / row['file']
    assert c.sha(original) == row['originalSha256'] == asr['masterSha256']
    assert c.sha(current) == row['sha256']
    assert row['noReencoding'] and row['audioPayloadAndClockUnchanged'] and row['videoPayloadUnchanged']
    before, after = audio_identity(original), audio_identity(current)
    assert before == after, 'AAC packets or their clock changed; existing recognition cannot approve a different sound'
    assert after['codec'] == 'aac' and after['sampleRate'] == 48000 and after['channels'] == 2
    assert after['packetPayloadSha256'] == asr['aacPacketPayloadSha256'] == provenance['packetPayloadSha256']
    assert after['framedPacketPayloadSha256'] == row['audioPacketPayloadSha256']
    result = dict(schemaVersion=1, part=1, master=c.rel(current), masterSha256=c.sha(current),
        asrOriginMaster=c.rel(original), asrOriginMasterSha256=c.sha(original),
        frozenAsrInput=c.rel(frozen), frozenAsrInputSha256=c.sha(frozen),
        wholeAsr=c.rel(asr_file), wholeAsrSha256=c.sha(asr_file),
        provenance=c.rel(provenance_file), provenanceSha256=c.sha(provenance_file),
        packetClockProof=c.rel(proof_file), packetClockProofSha256=c.sha(proof_file),
        implementation=c.rel(Path(__file__)), implementationSha256=c.sha(Path(__file__)),
        audioIdentity=after, allAacPacketPayloadsAndPtsDtsDurationsIdentical=True,
        videoOnlyTimestampCorrection=True, noAudioReencoding=True, wholeRecognitionCount=1,
        recognitionReusedByExactAacIdentity=True, humanWholeListening='pending',
        note='The original successful recognition and frozen input remain unchanged. Current master is bound by identical AAC payload and complete packet clock, not by another recognition.')
    c.save(c.O / 'final-master-binding.json', result)
    print(json.dumps(dict(masterSha256=result['masterSha256'], asrOriginMasterSha256=result['asrOriginMasterSha256'], aacIdentity=True, wholeRecognitionCount=1)))

if __name__ == '__main__': main()
