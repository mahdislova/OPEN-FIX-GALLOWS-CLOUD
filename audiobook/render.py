#!/usr/bin/env python3
"""Render one episode text file to a tagged MP3 with Kokoro TTS.

Usage: python3 render.py <episode.txt> <out.mp3> <track-number>
Env:   KOKORO_DIR  folder holding kokoro-v1.0.onnx and voices-v1.0.bin
       VOICE       Kokoro voice (default bf_emma)

Text format: line 1 is the episode title. Blank lines separate paragraphs.
A line containing only "* * *" is a scene break (longer pause).
"""
import os, re, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

src, out, track = sys.argv[1], sys.argv[2], sys.argv[3]
kdir = os.environ.get("KOKORO_DIR", ".")
voice = os.environ.get("VOICE", "bf_emma")
import onnxruntime as ort
opts = ort.SessionOptions()
opts.intra_op_num_threads = int(os.environ.get("THREADS", "0"))
sess = ort.InferenceSession(os.path.join(kdir, "kokoro-v1.0.onnx"), opts, providers=["CPUExecutionProvider"])
k = Kokoro.from_session(sess, os.path.join(kdir, "voices-v1.0.bin"))

raw = open(src, encoding="utf-8").read().strip()
title, body = raw.split("\n", 1)
blocks = re.split(r"\n\s*\n", body.strip())

SR = 24000
def silence(sec): return np.zeros(int(SR * sec), dtype=np.float32)

# The phonemizer spells vowel-less sound words out letter by letter ("K-S-H-H-H").
# The scripts keep the written onomatopoeia; these are the sayable stand-ins.
SAY = [
    (r"\b[Kk]shhh\b", "Shoosh"), (r"\bKSSHHH\b", "KRASH"),
    (r"\b(FZZZT|FZZT|Fzzt)\b", "Fizzt"), (r"\bFff\b", "Fooh"),
    (r"\bFwhumph\b", "Whoomph"), (r"\bFwip\b", "Whip"), (r"\bfssst\b", "Fisst"),
    (r"\bHhhhhhhhh\b", "Haaah"), (r"\bHssss\b", "Hiss"),
    (r"\b[Hh]hhh?\b", "Hah"), (r"\bKKK\b", "KRICK"),
    (r"\b(Krrrrrk|krrrrrrk)\b", "Kraaak"), (r"\b(Krrrk|Krrk|Krk)\b", "Krick"),
    (r"\bRrrrip\b", "Riiip"), (r"\bSkrr[kt]\b", "Skritch"),
    (r"\b[Tt]k\b", "tick"), (r"\bEeeeiiii\b", "Eeeeee"),
    (r"\b[Tt]hup-thup\b", "Ba-dum"),
]

def speak(text):
    text = re.sub(r"\s+", " ", text).strip()
    for pat, rep in SAY: text = re.sub(pat, rep, text)
    # Split on sentence ends so no chunk overruns the model's phoneme window.
    parts = re.split(r"(?<=[.!?…])\s+(?=[\"'‘“A-Z])", text)
    chunks, cur = [], ""
    for p in parts:
        if len(cur) + len(p) < 380: cur = (cur + " " + p).strip()
        else:
            if cur: chunks.append(cur)
            cur = p
    if cur: chunks.append(cur)
    audio = []
    for c in chunks:
        s, _ = k.create(c, voice=voice, speed=0.97, lang="en-gb")
        audio += [s.astype(np.float32), silence(0.12)]
    return np.concatenate(audio) if audio else silence(0.1)

pieces = [silence(0.6), speak("The Green Gallows."), silence(0.7), speak(title), silence(1.6)]
for b in blocks:
    if b.strip() == "* * *":
        pieces.append(silence(1.4)); continue
    pieces += [speak(b), silence(0.55)]
pieces.append(silence(2.0))
wav = np.concatenate(pieces)

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
    sf.write(tmp.name, wav, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1",
        "-codec:a", "libmp3lame", "-b:a", "64k",
        "-metadata", f"title={title}", "-metadata", "album=The Green Gallows: Audio Storybook",
        "-metadata", "artist=The Green Gallows", "-metadata", f"track={track}/10",
        "-metadata", "genre=Audiobook", out], check=True)
    os.unlink(tmp.name)
print(f"{out}: {len(wav)/SR/60:.1f} min")
