"""
잔잔한 피아노 BGM 직접 합성 (저작권 걱정 없음)
- 72 BPM, Fmaj7 → Em7 → Dm7 → Cmaj7 반복
- 부드러운 패드 + 피아노 느낌 아르페지오 + 간단한 리버브, 끝 2초 페이드아웃
"""
import wave

import numpy as np

SR = 44100
BPM = 72
BEAT = 60 / BPM
CHORDS = [  # MIDI 노트
    [53, 57, 60, 64],   # Fmaj7
    [52, 55, 59, 62],   # Em7
    [50, 53, 57, 60],   # Dm7
    [48, 52, 55, 59],   # Cmaj7
]


def hz(n):
    return 440 * 2 ** ((n - 69) / 12)


def piano(freq, dur, vel=0.25):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 2.8) * (1 - np.exp(-t * 300))
    tone = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) * np.exp(-t * 4)
            + 0.12 * np.sin(6 * np.pi * freq * t) * np.exp(-t * 6))
    return vel * env * tone


def pad(freqs, dur, vel=0.05):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8).clip(0)
    s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 1.003 * t) for f in freqs)
    return vel * env * s


def reverb(x):
    y = x.copy()
    for delay, gain in [(0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2), (0.173, 0.15), (0.29, 0.1)]:
        d = int(SR * delay)
        y[d:] += gain * x[:-d]
    return y


def make(path, seconds, chords=CHORDS):
    n = int(SR * (seconds + 1))
    mix = np.zeros(n)
    bar = BEAT * 4
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]          # 8분음표 아르페지오 순서
    t0, ci = 0.0, 0
    while t0 < seconds:
        chord = chords[ci % len(chords)]
        p = pad([hz(m) for m in chord], bar + 0.6)
        s = int(SR * t0)
        mix[s:s + len(p)] += p[: n - s]
        bass = piano(hz(chord[0] - 12), bar, 0.18)
        mix[s:s + len(bass)] += bass[: n - s]
        for k, idx in enumerate(pattern):
            nt = t0 + k * BEAT / 2
            note = chord[idx] + 12
            pn = piano(hz(note), 1.8, 0.11 if k % 2 else 0.14)
            s2 = int(SR * nt)
            if s2 < n:
                mix[s2:s2 + len(pn)] += pn[: n - s2]
        t0 += bar
        ci += 1
    mix = reverb(mix)[: int(SR * seconds)]
    fade = int(SR * 2)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix[: int(SR * 0.3)] *= np.linspace(0, 1, int(SR * 0.3))
    mix = mix / np.abs(mix).max() * 0.6
    data = (np.repeat(mix[:, None], 2, axis=1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
