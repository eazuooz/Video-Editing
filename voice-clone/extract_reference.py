"""Extract a clean mono WAV reference clip from a video, using PyAV.

Usage:
  python extract_reference.py "D:\\OneDrive\\비디오\\Video Project 24.mp4" \
      ..\\shared\\voice-reference\\reference.wav --start 15 --duration 20
"""

from __future__ import annotations

import argparse
from pathlib import Path

import av


def extract(source: Path, destination: Path, start: float, duration: float) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    end = start + duration

    with av.open(source) as input_container:
        audio_stream = input_container.streams.audio[0]
        resampler = av.audio.resampler.AudioResampler(
            format="s16", layout="mono", rate=24_000
        )

        with av.open(destination, mode="w", format="wav") as output_container:
            output_stream = output_container.add_stream("pcm_s16le", rate=24_000)
            output_stream.layout = "mono"

            for frame in input_container.decode(audio_stream):
                frame_start = float(frame.time or 0)
                if frame_start + float(frame.samples / frame.sample_rate) < start:
                    continue
                if frame_start >= end:
                    break

                for resampled_frame in resampler.resample(frame):
                    for packet in output_stream.encode(resampled_frame):
                        output_container.mux(packet)

            for packet in output_stream.encode(None):
                output_container.mux(packet)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--start", type=float, default=15)
    parser.add_argument("--duration", type=float, default=20)
    args = parser.parse_args()

    extract(args.source, args.destination, args.start, args.duration)
    print(f"Created {args.destination}")


if __name__ == "__main__":
    main()
