# Inspect and remux an approved master

This exercise uses an existing FFmpeg installation with the MP4 muxer, built-in MPEG-4 video encoder and test source. It requires no cloud service or source footage. Run it in a new working directory.

```sh
ffmpeg -hide_banner -f lavfi -i 'testsrc2=size=640x360:rate=24' \
  -t 2 -c:v mpeg4 -an -n fixture.mp4

ffprobe -v error -show_streams -show_format -of json fixture.mp4 > fixture-streams.json

ffmpeg -hide_banner -i fixture.mp4 -map 0:v:0 -c copy \
  -movflags +faststart -n delivery.mp4

ffprobe -v error -show_streams -show_format -of json delivery.mp4 > delivery-streams.json
```

The fixture and delivery copy should both report a 640×360 MPEG-4 video stream, 24 fps and two seconds of duration. Inspect a rendered frame as well as the stream report:

```sh
ffmpeg -hide_banner -ss 1 -i delivery.mp4 -frames:v 1 -update 1 -n frame.png
```

Use the same inspection step after rendering an approved HyperFrames or Remotion master. For production, choose stream mappings and container compatibility according to the delivery contract. This fixture deliberately has no audio. Include and inspect the expected audio and caption streams when the contract requires them.

[FFmpeg guide](../repositories/ffmpeg.md) · [Video workflow](../workflows/cinematic-video.md)
