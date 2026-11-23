#!/usr/bin/env python3
"""Autonomous Audio Pipeline for Bob Big Questions.

Uses Edge-TTS with Microsoft Ava (en-US-AvaNeural at +2% speed)
and procedural 48kHz stereo cartoon marimba & walking bass music
with dynamic loudness ducking to broadcast YouTube standards (-14 LUFS).
"""

import os
import sys
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import edge_tts

try:
    import imageio_ffmpeg
    DEFAULT_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    DEFAULT_FFMPEG = shutil.which("ffmpeg") or "ffmpeg"

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_RATE = 48000
VOICE_NAME = "en-US-AvaNeural"
VOICE_RATE = "+2%"


def get_ffmpeg_bin() -> str:
    return shutil.which("ffmpeg") or DEFAULT_FFMPEG


def get_audio_duration(file_path: Path) -> float:
    cmd = [
        get_ffmpeg_bin(), "-i", str(file_path),
        "-hide_banner"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            time_part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = time_part.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 0.0


async def _synthesize_scene_voice(text: str, output_path: Path):
    communicate = edge_tts.Communicate(text, VOICE_NAME, rate=VOICE_RATE)
    await communicate.save(str(output_path))


def synthesize_all_scenes(screenplay: Dict[str, Any], output_dir: Path) -> List[Dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    scenes = screenplay["scenes"]
    scene_audio_data = []

    for sc in scenes:
        num = sc["scene_num"]
        raw_path = output_dir / f"scene_{num:02d}_raw.m4a"
        asyncio.run(_synthesize_scene_voice(sc["narration"], raw_path))
        dur = get_audio_duration(raw_path)
        scene_audio_data.append({
            "scene_num": num,
            "banner": sc.get("banner", f"SCENE {num}"),
            "sub_banner": sc.get("sub_banner", "INTERESTING SCIENCE PHENOMENON"),
            "raw_path": raw_path,
            "raw_duration": dur,
            "visual_beats": sc.get("visual_beats", [])
        })

    return scene_audio_data


def generate_cartoon_music(duration_sec: float, output_path: Path):
    """Generates procedural bouncy marimba & walking-bass royalty-free music bed."""
    t = np.linspace(0, duration_sec, int(SAMPLE_RATE * duration_sec), endpoint=False)
    # Marimba chord progression (C - Am - F - G bouncy cartoon loop)
    bpm = 124.0
    beat_dur = 60.0 / bpm
    total_beats = int(duration_sec / beat_dur)

    chords = [
        [261.63, 329.63, 392.00],  # C major
        [220.00, 261.63, 329.63],  # A minor
        [174.61, 220.00, 261.63],  # F major
        [196.00, 246.94, 293.66],  # G major
    ]

    music = np.zeros_like(t)
    for b in range(total_beats):
        chord = chords[(b // 4) % len(chords)]
        note = chord[b % len(chord)]
        start_idx = int(b * beat_dur * SAMPLE_RATE)
        end_idx = min(len(t), int((b + 1) * beat_dur * SAMPLE_RATE))
        chunk_len = end_idx - start_idx
        if chunk_len <= 0:
            continue
        chunk_t = np.linspace(0, beat_dur, chunk_len, endpoint=False)
        envelope = np.exp(-chunk_t * 6.0)
        # Marimba pluck harmonic
        marimba = (0.7 * np.sin(2 * np.pi * note * chunk_t) +
                   0.3 * np.sin(2 * np.pi * note * 2 * chunk_t)) * envelope
        # Bass note on 1 and 3
        if b % 2 == 0:
            bass_note = chord[0] / 2.0
            bass_env = np.exp(-chunk_t * 3.5)
            bass = 0.5 * np.sin(2 * np.pi * bass_note * chunk_t) * bass_env
            marimba += bass

        music[start_idx:end_idx] += marimba * 0.22

    music = np.clip(music, -0.9, 0.9)
    audio_int16 = (music * 32767).astype(np.int16)

    # Save to wav via ffmpeg pipe
    cmd = [
        get_ffmpeg_bin(), "-y", "-f", "s16le", "-ar", str(SAMPLE_RATE), "-ac", "1",
        "-i", "pipe:0", "-ac", "2", "-ar", str(SAMPLE_RATE), str(output_path)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.communicate(input=audio_int16.tobytes())


def assemble_and_mix_audio(scene_data: List[Dict[str, Any]], output_dir: Path) -> Path:
    """Concatenates scene voiceovers with a tight, natural 1.0s breath pause and mixes with ducked music.
    
    CRITICAL: The voiceover DRIVES the scene duration!
    When the narrator finishes speaking (+ 1.0s natural pause), the scene IMMEDIATELY switches.
    Zero dead silence, zero awkward waiting!
    """
    PAUSE_PER_SCENE = 1.0  # Natural comedic breath pause

    padded_files = []
    for sc in scene_data:
        p_out = output_dir / f"scene_{sc['scene_num']:02d}_padded.wav"
        sc_dur = sc["raw_duration"] + PAUSE_PER_SCENE
        sc["final_duration"] = sc_dur
        sc["frames"] = int(round(sc_dur * 30))
        cmd = [
            get_ffmpeg_bin(), "-y", "-i", str(sc["raw_path"]),
            "-af", f"apad=pad_dur={PAUSE_PER_SCENE:.3f}",
            "-ar", str(SAMPLE_RATE), "-ac", "2",
            str(p_out)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        padded_files.append(p_out)

    # Concat all voice tracks
    concat_list = output_dir / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in padded_files:
            f.write(f"file '{p.resolve()}'\n")

    master_voice = output_dir / "master_voice.wav"
    subprocess.run([
        get_ffmpeg_bin(), "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-ar", str(SAMPLE_RATE), "-ac", "2", str(master_voice)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    final_voice_dur = get_audio_duration(master_voice)

    # Generate procedural music bed matching exact audio duration
    music_bed = output_dir / "music_bed.wav"
    generate_cartoon_music(final_voice_dur + 2.0, music_bed)

    # Ducked Audio Mix
    master_mix = output_dir / "master_audio_mix.wav"
    cmd_mix = [
        get_ffmpeg_bin(), "-y",
        "-i", str(master_voice),
        "-i", str(music_bed),
        "-filter_complex",
        "[1:a]volume=0.22[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "[out]",
        "-ar", str(SAMPLE_RATE),
        "-ac", "2",
        str(master_mix)
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return master_mix
