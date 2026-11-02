# The Green Gallows: Audio Storybook

The ten-episode season from `FULL NEW SEASON.md`, rewritten as narrated prose and read aloud. There is one MP3 per episode, each about 18 to 35 minutes long.

| # | Episode | Clock |
| --- | --- | --- |
| 1 | The Engagement | 49 days to first snow |
| 2 | The Wake | 47 days |
| 3 | Lanterns | 42 days |
| 4 | The Hearing | 38 days |
| 5 | Lantern Night | 33 days |
| 6 | Coal | 28 days |
| 7 | The Girl Who Isn't | 21 days |
| 8 | The Wedding | 14 days |
| 9 | The Snow Confession | First snow |
| 10 | The Tithe | The last night |

- `mp3/`: the episodes, tagged with title, album and track number so a phone plays them in order.
- `text/`: the narration scripts. Line 1 is the title, and a line reading `* * *` marks a scene break.
- `render.py`: turns one script into an MP3 using [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) TTS with the `bf_emma` British voice.

## Re-rendering an episode

```bash
pip install kokoro-onnx soundfile
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
KOKORO_DIR=. python3 render.py "text/01-the-engagement.txt" "mp3/01 - The Engagement.mp3" 1
```

To change the voice, set `VOICE`, for example `VOICE=bm_george` for a male British narrator. `ffmpeg` has to be on the path.

The scripts keep the written sound effects (*Kshhh, THOOM*). `render.py` swaps them for spellings the voice can actually pronounce, so check its `SAY` table if you add new ones.
