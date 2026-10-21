"""
릴스 BGM 직접 합성 (저작권 걱정 없음)
- 스타일 5가지: piano(72) / lofi(84, 일렉피아노+드럼) / musicbox(88) / guitar(96) / marimba(108, 드럼)
- 코드 진행 + 아르페지오 + 패드 + 간단한 리버브, 끝 2초 페이드아웃
- 릴스마다 style 과 chords 를 바꿔서 매번 다르게 들리도록
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


def epiano(freq, dur, vel=0.2):
    """로파이 느낌 일렉 피아노: 둥근 소리 + 살짝 흔들리는 트레몰로"""
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 1.6) * (1 - np.exp(-t * 200))
    mod = np.sin(2 * np.pi * freq * 2 * t) * 1.2 * np.exp(-t * 3)          # FM 으로 종소리 같은 어택
    tone = np.sin(2 * np.pi * freq * t + mod) * (1 + 0.15 * np.sin(2 * np.pi * 4.5 * t))
    return vel * env * tone


def bell(freq, dur, vel=0.18):
    """오르골/글로켄 느낌: 높은 배음이 섞인 맑은 소리"""
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 3.5) * (1 - np.exp(-t * 500))
    tone = (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 6)
            + 0.25 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t * 10))
    return vel * env * tone


def pluck(freq, dur, vel=0.3):
    """기타 줄 뜯는 소리 (Karplus-Strong)"""
    n, p = int(SR * dur), max(2, int(SR / freq))
    rng = np.random.default_rng(int(freq))
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return vel * out


def marimba(freq, dur, vel=0.22):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 7) * (1 - np.exp(-t * 800))
    return vel * env * (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 20))


def kick(vel=0.5):
    t = np.arange(int(SR * 0.3)) / SR
    return vel * np.sin(2 * np.pi * (50 + 80 * np.exp(-t * 30)) * t) * np.exp(-t * 12)


def hat(vel=0.06):
    t = np.arange(int(SR * 0.05)) / SR
    return vel * np.random.default_rng(1).uniform(-1, 1, len(t)) * np.exp(-t * 80)


# 스타일: (BPM, 멜로디 악기, 아르페지오 순서(8분음표, -1=쉼), 옥타브, 패드 세기, 베이스 악기, 드럼)
STYLES = {
    "piano":    (72, piano,   [0, 2, 1, 3, 2, 1, 3, 2],     12, 0.05, piano,  False),
    "piano2":   (88, piano,   [0, 3, 2, 3, 1, 3, 2, 3],     12, 0.04, piano,  False),   # 조금 빠르고 통통 튀는 피아노
    "marimba":  (108, marimba, [0, 2, 3, 2, 1, 2, 3, -1],   12, 0.03, marimba, True),
    "marimba2": (96, marimba, [3, 1, 2, 0, 3, 2, 1, 2],     12, 0.04, marimba, False),  # 드럼 없는 잔잔한 마림바
    # 사용자 피드백(10/15): 아래 셋은 별로 → 안 씀
    "lofi":     (84, epiano,  [0, -1, 2, 3, -1, 1, 2, -1],  12, 0.03, epiano, True),
    "musicbox": (88, bell,    [3, 2, 1, 2, 0, 2, 1, 3],     24, 0.02, None,   False),
    "guitar":   (96, pluck,   [0, 1, 2, 3, 2, 1, 2, 3],     0,  0.02, pluck,  False),
}
USE = ["piano", "marimba", "piano2", "marimba2"]   # 릴스마다 이 순서로 돌려쓰기 + 코드 진행도 바꾸기


def _add(mix, x, start):
    s = int(SR * start)
    if s < len(mix):
        mix[s:s + len(x)] += x[: len(mix) - s]


def make(path, seconds, chords=CHORDS, style="piano"):
    bpm, inst, pattern, octave, pad_vel, bass_inst, drums = STYLES[style]
    beat = 60 / bpm
    n = int(SR * (seconds + 1))
    mix = np.zeros(n)
    bar = beat * 4
    t0, ci = 0.0, 0
    while t0 < seconds:
        chord = chords[ci % len(chords)]
        if pad_vel:
            _add(mix, pad([hz(m) for m in chord], bar + 0.6, pad_vel), t0)
        if bass_inst:
            _add(mix, bass_inst(hz(chord[0] - 12), bar, 0.18), t0)
        for k, idx in enumerate(pattern):
            if idx < 0:
                continue
            _add(mix, inst(hz(chord[idx] + octave), 1.8, 0.11 if k % 2 else 0.14), t0 + k * beat / 2)
        if drums:
            for b in range(4):
                if b % 2 == 0:
                    _add(mix, kick(), t0 + b * beat)
                _add(mix, hat(), t0 + b * beat + beat / 2)
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
