# silencecut

Cut the silences out of a talking-head video. It finds speech with FFmpeg's `silencedetect`, writes an edit decision list (EDL), renders the cut with a short audio fade at every join so there are no clicks, and then checks its own render.

It stands in for the first editing pass of **Video Use**: removing dead air from raw footage. It is our own code. Video Use plans cuts from a word-level transcript; silencecut uses loudness only, so it needs no transcription service, no API key and sends nothing anywhere.

## Usage

```sh
python silencecut.py input.mp4 --noise -35dB --min-silence 0.4 --pad 0.08 --out out/cut.mp4
python silencecut.py input.mp4 --edl-only --out out/cut.mp4      # write the EDL and stop
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--noise` | -35dB | Level below which audio counts as silence. |
| `--min-silence` | 0.4 | Shortest silence to remove, in seconds. Shorter pauses stay. |
| `--pad` | 0.08 | Seconds of audio kept on each side of every cut, so word starts and ends are not clipped. |
| `--fade` | 0.03 | Audio fade in and out at each segment edge (half-sine shape). 0 turns fades off. |
| `--min-speech` | 0.05 | Drop sounds shorter than this, such as a single tap. |
| `--crf` | 20 | H.264 quality. |
| `--out` | out/cut.mp4 | Output video. |

It writes three files: the video, `<name>.edl.json` and `<name>.report.json`. Exit code 0 means rendered and self-check passed, 1 means the self-check failed, 2 means an error.

### How it works

1. `silencedetect` on the first audio stream gives the silent stretches. Everything else is speech.
2. Each speech segment is widened by `--pad`, then snapped outward to whole video frames, then merged with neighbours it now touches. Snapping to frames is what keeps sound and picture in sync: video is cut with `trim=start_frame/end_frame` and audio with `atrim=start_sample/end_sample` at exactly the same instants.
3. One FFmpeg pass trims all segments, fades each audio segment in and out, and joins them with the `concat` filter. Output is H.264 `yuv420p` and AAC. The filter graph goes through a file so long EDLs do not hit command-line limits.
4. Self-check: the decoded video frame count and the audio duration must equal the EDL sum within one frame. The decoded audio is scanned at every join: the largest sample-to-sample jump within 2 ms of the join must not exceed both 3 times the largest jump 40 to 80 ms away and 0.002 (about -54 dBFS). A jump bigger than that is a click.

### EDL format

```json
{ "version": 1, "source": "input.mp4", "fps": "30", "sampleRate": 48000,
  "params": { "noiseDb": -35, "minSilence": 0.4, "pad": 0.08, "fade": 0.03, "minSpeech": 0.05 },
  "silences": [ { "start": 0.0, "end": 1.0 } ],
  "segments": [ { "index": 0, "in": 0.9, "out": 2.6, "duration": 1.7, "inFrame": 27, "outFrame": 78, "outputStart": 0.0 } ],
  "totalDuration": 5.1 }
```

`in` and `out` are source times in seconds. `outputStart` is where the segment lands in the cut.

## Requirements

Python 3.10 or newer with numpy, and `ffmpeg` and `ffprobe` on `PATH`.

## What it does not do, compared with Video Use

- No transcript. It cannot remove filler words, false starts or retakes, and it cannot cut by meaning. It only removes quiet stretches.
- A loud room or music bed can hide pauses from it. Tune `--noise` per recording.
- Assumes a constant frame rate and a video and audio stream that both start at time 0.
- No overlays, captions, color work or B-roll. Single input file only.
- The join check looks for steps in the waveform. It does not judge whether a cut sounds natural.
- Audio-only input works, with a 10 ms grid in place of video frames. It was not part of the test.

## Test

```sh
python test.py
```

The test synthesizes a 10 s fixture: a `testsrc2` picture at 30 fps and 48 kHz audio with three 440 Hz tone bursts (1.5 s, 1.0 s, 2.0 s) separated by 1.5 s gaps. The gaps are not digital silence. A quiet 103.7 Hz hum at -40 dBFS runs under everything, so a cut without a fade lands on a live waveform and steps. A white square in the corner is lit exactly while a tone plays, so sync can be measured.

| Check | Result (26 Nov 2026, FFmpeg 7.1, Python 3.14) |
| --- | --- |
| `segments`: three speech segments found | pass: 0.9-2.6, 3.9-5.1, 6.4-8.6 s |
| `duration`: output equals tones plus pads (4.98 s) within frame snapping, and equals the EDL sum | pass: 5.100 s EDL, 5.100 s video, 5.100 s audio (snapping added 4 frames) |
| `selfCheck`: the tool's own check passed | pass |
| `clickFree`: independent decode, peak jump at each join below 0.002 | pass: 0.000004 and 0.000003 (the hum's own jump is 0.000136) |
| `avSync`: each on/off edge of the white square matches the tone edge | pass: 0 frames off at all 6 edges |
| `controlClicks`: the same cuts with `--fade 0` must fail the self-check | pass: exit 1, a 0.011 jump at the first join was caught |

The control's second join stepped only 0.0017, below the 0.002 floor, so it was not flagged. That step is about -55 dBFS. The fixture and control files are deleted after the test; `out/` keeps the cut, its EDL and reports (about 290 KB).
