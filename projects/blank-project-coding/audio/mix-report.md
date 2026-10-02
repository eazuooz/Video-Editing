# Final-v1 audio review

The 1368.7-second mix uses the approved Qwen3-TTS 1.7B reference voice and continuous approved Nimbus restored-copy BGM. All 34 current scene WAVs are retained with SHA-256 provenance. Scene 09, 16 and 20 replacement takes were accepted after targeted ASR review; superseded takes remain separate.

Narration target is -16 LUFS, BGM target -28 LUFS, with continuous music through the two-second intro and ten-second original-member ending. The owned educational recordings contain no source audio, so no gameplay sound was invented. `production/final-v1/qa.json` measures the final AAC at **-16.07 LUFS and -2.29 dBTP**. These final encoded measurements supersede the pre-encode WAV figures in mix-settings.

Both delivered MP4s contain the same copied AAC stream as the final mix. All 34 normalized voice sections align with the mix at zero 20 ms lag; minimum envelope correlation is .98841. Raw-source to normalized voice identity was checked separately because dynamic loudness processing legitimately changes longer amplitude envelopes. See `mix-alignment-review.json` and the preserved initial diagnostic.

All 124 paragraphs received technical speech-content review. Full human listening is **pending**; ASR, waveform matching and direct visual QA are not claimed as human listening. Nimbus's official Studio listing and displayed license were directly verified, but acquisition and exact-byte matching of the original Audio Library file remain pending. The existing approved restored copy and its provenance are preserved.
