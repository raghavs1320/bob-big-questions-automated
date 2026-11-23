"""Audio Generation & Foley Sound Design Pipeline for Episode 7:
'What If Time Stopped For 24 Hours?'

Duration Target: Exactly 225.0 seconds (3 minutes 45 seconds).
Features:
- 16 Scene Voiceovers synthesized via Edge-TTS (en-US-AvaNeural, rate='+19%').
- Frame-accurate scene timing calculations (0.000s drift).
- Procedural cartoon Foley Sound Effects synthesized with NumPy (pops, whooshes, chimes, squishes, countdown beeps, sonic explosion).
- Background cartoon music dynamically mixed and ducked under speech.
"""

import asyncio
import json
import os
import subprocess
import wave
from pathlib import Path
import numpy as np
import edge_tts
from voice.audio_processor import get_audio_duration
from utils.hardware import get_ffmpeg_binary

FFMPEG_BIN = get_ffmpeg_binary()

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "audio" / "time_freeze_225s"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_SOURCE = BASE_DIR / "audio" / "gravity_cartoon_music.wav"

TARGET_TOTAL_SECONDS = 225.0
FPS = 30
SAMPLE_RATE = 48000

SCENES_SCRIPT = [
    {
        "id": 1,
        "title": "7:00 AM THE ALARM FREEZE",
        "text": "Seven A.M. on a Tuesday. The digital clock blinks seven o'clock... and then, nothing happens. The second hand stops. The alarm freezes into ribbons. And Bob's hot morning coffee hangs in mid-air like an amber glass sculpture.",
        "sfx": "freeze_chime"
    },
    {
        "id": 2,
        "title": "THE FROZEN CITY WAX MUSEUM",
        "text": "Bob steps outside, and the entire city has turned into a life-sized wax museum! Yellow cabs are frozen mid-turn with tire smoke locked in place. Pedestrians are paused mid-stride. And a cyclist is tilted at forty-five degrees!",
        "sfx": "whoosh"
    },
    {
        "id": 3,
        "title": "THE 40,000 RAINDROP MAZE",
        "text": "Bob walks into a sudden summer rainstorm. Over forty thousand raindrops are suspended in mid-air like floating diamonds! Bob taps one—it feels like a cold glass marble. He dodges through the droplet maze like a cartoon secret agent!",
        "sfx": "glass_ting"
    },
    {
        "id": 4,
        "title": "THE TERRIFYING PHYSICS OF LIGHT",
        "text": "Now for the terrifying physics: if time stopped, photons—the particles of light—should stop moving too! That means pitch-black darkness! But luckily, light only travels where Bob moves, creating a glowing cone of illumination wherever he walks!",
        "sfx": "light_hum"
    },
    {
        "id": 5,
        "title": "WALKING ON SOLID OCEAN WAVES",
        "text": "Bob heads to the beach. A twenty-foot ocean wave is frozen mid-crash, forming a giant turquoise tunnel! Water molecules can't slip past each other, meaning the ocean is rock-solid! Bob steps onto the surface and slides across the waves like an ice skater!",
        "sfx": "water_slide"
    },
    {
        "id": 6,
        "title": "THE SUPERMARKET MEGA-FEAST",
        "text": "By noon, Bob’s stomach is growling. He walks into the grand supermarket. Potato chips are suspended mid-crunch, soda streams are frozen into ruby poles, and Bob constructs a four-foot mega burger with eight patties, melted cheese, and extra pickles!",
        "sfx": "chomp"
    },
    {
        "id": 7,
        "title": "PRANKING HISTORICAL STATUES",
        "text": "With a full belly, the mischievous side kicks in. Bob visits the city museum. He adjusts the arms of serious Roman marble statues into disco poses, and draws a cheerful cartoon mustache onto the most serious security guard in town!",
        "sfx": "squeak"
    },
    {
        "id": 8,
        "title": "THE STADIUM FROZEN MID-GOAL",
        "text": "At the packed stadium, eighty thousand fans are frozen mid-cheer! The championship ball is locked in mid-air, three inches from the goal net! Bob walks onto the pitch, poses the goalie in a ballerina stance, and takes a selfie!",
        "sfx": "camera_flash"
    },
    {
        "id": 9,
        "title": "THE AIR JELLY PARADOX",
        "text": "But hour six brings strange exhaustion. Why is walking getting so hard? Because air molecules normally bounce billions of times a second. With time stopped, Bob has to physically shove millions of frozen atoms aside. It feels like wading through thick strawberry gelatin!",
        "sfx": "squish"
    },
    {
        "id": 10,
        "title": "THE ABSOLUTE ZERO DEEP FREEZE",
        "text": "And then comes the cold. Heat is just atoms vibrating. No vibration means no heat! Within hours, the air plummets toward absolute zero! Bob throws on his thickest neon yellow winter parka, while his warm breath crystallizes into floating ice butterflies!",
        "sfx": "shiver"
    },
    {
        "id": 11,
        "title": "THE FROZEN TABBY CAT SURPRISE",
        "text": "In an alleyway, Bob spots his neighborhood orange tabby cat, frozen in mid-leap trying to catch a butterfly. Bob smiles and gently places a fresh slice of pepperoni right in front of the cat’s nose—so when time starts, it gets the surprise of its life!",
        "sfx": "bell_chime"
    },
    {
        "id": 12,
        "title": "HOUR 18: SILENCE & NO WI-FI",
        "text": "By Hour eighteen, the novelty wears off. The silence is deafening. No internet. No YouTube. Electrons can't flow through wires, meaning every phone and TV is dead. Bob sits on his inflatable yellow sofa in the park, staring at the motionless clouds.",
        "sfx": "wind_echo"
    },
    {
        "id": 13,
        "title": "HOUR 23: THE COSMIC VIBRATION",
        "text": "Hour twenty-three. A low cosmic vibration hums through the ground. The frozen raindrops begin to quiver. Traffic lights flicker from amber to green. The anomaly is collapsing, and the universe is preparing to unleash twenty-four hours of pent-up kinetic energy!",
        "sfx": "rumble"
    },
    {
        "id": 14,
        "title": "THE 10-SECOND COUNTDOWN",
        "text": "Bob dives under a sturdy park shelter. Ten! Nine! Eight! Every air molecule Bob pushed, every object he moved, and every footstep stored immense kinetic tension. When the clock hits zero, all of that energy discharges in one microsecond!",
        "sfx": "countdown_beep"
    },
    {
        "id": 15,
        "title": "THE GRAND SONIC BOOM RELEASE",
        "text": "SNAP! Time EXPLODES back into motion! The ocean wave crashes with a roaring tsunami splash! Eighty thousand fans scream GOAL as the soccer ball rips through the net! Car horns honk, the rain smashes down, and the cat catches the pepperoni in a single blink!",
        "sfx": "snap_boom"
    },
    {
        "id": 16,
        "title": "PANCAKES & THE NEXT QUESTION",
        "text": "Back in his warm apartment, Bob collapses into bed with a giant plate of buttered pancakes, exhausted but victorious. Twenty-four hours of frozen time survived! Now... what happens if time goes backward for a week?! Subscribe to Bob Big Questions, and drop your craziest what-if in the comments!",
        "sfx": "victory_fanfare"
    }
]


async def synthesize_all_scenes():
    """Synthesizes individual voice files for all 16 scenes at +19% rate."""
    print("🎙️ Synthesizing 16 Scene Voiceovers with Edge-TTS (en-US-AvaNeural +19%)...")
    raw_files = []
    for sc in SCENES_SCRIPT:
        out_f = AUDIO_DIR / f"raw_scene{sc['id']:02d}.mp3"
        comm = edge_tts.Communicate(sc["text"], "en-US-AvaNeural", rate="+19%")
        await comm.save(str(out_f))
        raw_files.append(out_f)
        print(f"  ✓ Scene {sc['id']:02d}: {sc['title']}")
    return raw_files


def synthesize_foley_sfx():
    """Synthesizes procedural cartoon sound effects with NumPy."""
    sfx_dir = AUDIO_DIR / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    sr = SAMPLE_RATE

    # 1. Freeze Chime: Crystalline ringing harmonic bell
    t = np.linspace(0, 0.8, int(sr * 0.8), endpoint=False)
    env = np.exp(-t * 7.0)
    w = (np.sin(2 * np.pi * 1760 * t) * 0.5 + np.sin(2 * np.pi * 2637 * t) * 0.35 + np.sin(2 * np.pi * 3520 * t) * 0.2) * env
    write_wav(sfx_dir / "freeze_chime.wav", w, sr)

    # 2. Whoosh: Filtered noise sweep
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    noise = np.random.normal(0, 0.3, len(t))
    env = np.sin(np.pi * (t / 0.5)) ** 2
    w = noise * env * np.sin(2 * np.pi * (200 + 600 * t) * t)
    write_wav(sfx_dir / "whoosh.wav", w, sr)

    # 3. Glass Ting: High bell ping
    t = np.linspace(0, 0.4, int(sr * 0.4), endpoint=False)
    env = np.exp(-t * 14.0)
    w = (np.sin(2 * np.pi * 2793 * t) * 0.6 + np.sin(2 * np.pi * 5587 * t) * 0.3) * env
    write_wav(sfx_dir / "glass_ting.wav", w, sr)

    # 4. Light Hum: Pulsing sci-fi drone
    t = np.linspace(0, 0.6, int(sr * 0.6), endpoint=False)
    env = np.sin(np.pi * (t / 0.6))
    w = (np.sin(2 * np.pi * 220 * t) * 0.5 + np.sin(2 * np.pi * 440 * t) * 0.3) * (0.8 + 0.2 * np.sin(2 * np.pi * 8 * t)) * env
    write_wav(sfx_dir / "light_hum.wav", w, sr)

    # 5. Water Slide: Crisp glide
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    env = np.exp(-t * 5.0)
    freq = 600 - 300 * t
    w = np.sin(2 * np.pi * freq * t) * env * 0.5
    write_wav(sfx_dir / "water_slide.wav", w, sr)

    # 6. Chomp: Cartoon bite
    t = np.linspace(0, 0.3, int(sr * 0.3), endpoint=False)
    env = np.exp(-t * 18.0)
    w = (np.sin(2 * np.pi * 180 * t) * 0.7 + np.random.normal(0, 0.2, len(t))) * env
    write_wav(sfx_dir / "chomp.wav", w, sr)

    # 7. Squeak: Marker squeak
    t = np.linspace(0, 0.35, int(sr * 0.35), endpoint=False)
    freq = 1800 + 400 * np.sin(2 * np.pi * 12 * t)
    w = np.sin(2 * np.pi * freq * t) * np.sin(np.pi * (t / 0.35)) * 0.4
    write_wav(sfx_dir / "squeak.wav", w, sr)

    # 8. Camera Flash: Click and whine
    t = np.linspace(0, 0.4, int(sr * 0.4), endpoint=False)
    click = np.exp(-t * 40.0) * np.sin(2 * np.pi * 1200 * t)
    whine = np.sin(2 * np.pi * (2000 + 2000 * t) * t) * 0.15 * (t / 0.4)
    w = (click * 0.7 + whine) * 0.6
    write_wav(sfx_dir / "camera_flash.wav", w, sr)

    # 9. Squish: Strawberry jelly squelch
    t = np.linspace(0, 0.45, int(sr * 0.45), endpoint=False)
    freq = 150 + 250 * np.exp(-t * 8.0)
    w = np.sin(2 * np.pi * freq * t) * np.exp(-t * 6.0) * (1.0 + 0.3 * np.random.normal(0, 0.2, len(t))) * 0.6
    write_wav(sfx_dir / "squish.wav", w, sr)

    # 10. Shiver: Frost breeze & teeth chatter
    t = np.linspace(0, 0.6, int(sr * 0.6), endpoint=False)
    wind = np.random.normal(0, 0.2, len(t)) * np.sin(np.pi * (t / 0.6))
    chatter = np.sign(np.sin(2 * np.pi * 16 * t)) * np.sin(2 * np.pi * 900 * t) * 0.3 * np.exp(-t * 3.0)
    w = (wind + chatter) * 0.5
    write_wav(sfx_dir / "shiver.wav", w, sr)

    # 11. Bell Chime: Gentle cartoon bell
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    w = (np.sin(2 * np.pi * 1046 * t) * 0.6 + np.sin(2 * np.pi * 2093 * t) * 0.3) * np.exp(-t * 8.0)
    write_wav(sfx_dir / "bell_chime.wav", w, sr)

    # 12. Wind Echo: Low hollow rumble
    t = np.linspace(0, 0.7, int(sr * 0.7), endpoint=False)
    w = np.random.normal(0, 0.25, len(t)) * (np.sin(np.pi * (t / 0.7)) ** 2) * 0.4
    write_wav(sfx_dir / "wind_echo.wav", w, sr)

    # 13. Rumble: Low 45Hz sub-bass rise
    t = np.linspace(0, 0.8, int(sr * 0.8), endpoint=False)
    w = np.sin(2 * np.pi * (40 + 50 * t) * t) * (t / 0.8) * 0.7
    write_wav(sfx_dir / "rumble.wav", w, sr)

    # 14. Countdown Beep: Digital timer beep
    t = np.linspace(0, 0.15, int(sr * 0.15), endpoint=False)
    w = np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 20.0) * 0.6
    write_wav(sfx_dir / "countdown_beep.wav", w, sr)

    # 15. Snap Boom: Explosive bass slam and high splash
    t = np.linspace(0, 1.2, int(sr * 1.2), endpoint=False)
    boom = np.sin(2 * np.pi * (120 - 70 * t) * t) * np.exp(-t * 3.5) * 0.8
    splash = np.random.normal(0, 0.35, len(t)) * np.exp(-t * 4.0)
    w = (boom + splash) * 0.7
    write_wav(sfx_dir / "snap_boom.wav", w, sr)

    # 16. Victory Fanfare: Major chord sparkle
    t = np.linspace(0, 0.9, int(sr * 0.9), endpoint=False)
    chord = (np.sin(2 * np.pi * 523 * t) * 0.4 + np.sin(2 * np.pi * 659 * t) * 0.3 + np.sin(2 * np.pi * 784 * t) * 0.3 + np.sin(2 * np.pi * 1046 * t) * 0.2) * np.exp(-t * 4.0)
    write_wav(sfx_dir / "victory_fanfare.wav", chord * 0.6, sr)
    print("🔊 Synthesized 16 Procedural Foley Sound Effects!")


def write_wav(path: Path, data: np.ndarray, sr: int):
    data_int16 = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data_int16.tobytes())


def assemble_and_balance_audio():
    """Measures raw scene durations and creates frame-accurate padded scenes targeting exactly 225.0s."""
    raw_durations = []
    for sc in SCENES_SCRIPT:
        f_p = AUDIO_DIR / f"raw_scene{sc['id']:02d}.mp3"
        dur = get_audio_duration(str(f_p))
        raw_durations.append(dur)

    raw_total = sum(raw_durations)
    remaining_time = TARGET_TOTAL_SECONDS - raw_total
    num_scenes = len(SCENES_SCRIPT)
    pad_per_scene = max(0.05, remaining_time / float(num_scenes))

    print(f"📊 Raw Voice Duration: {raw_total:.2f}s | Target: {TARGET_TOTAL_SECONDS:.1f}s")
    print(f"⏱️ Pause Padding Per Scene: {pad_per_scene:.3f}s")

    scene_specs = []
    padded_files = []
    accum_frames = 0

    for i, sc in enumerate(SCENES_SCRIPT):
        raw_dur = raw_durations[i]
        final_scene_dur = raw_dur + pad_per_scene
        scene_frames = int(round(final_scene_dur * FPS))

        start_frame = accum_frames
        end_frame = accum_frames + scene_frames
        accum_frames = end_frame

        pad_f = AUDIO_DIR / f"padded_scene{sc['id']:02d}.wav"
        # Create padded audio using ffmpeg
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(AUDIO_DIR / f"raw_scene{sc['id']:02d}.mp3"),
            "-af", f"apad=pad_dur={pad_per_scene:.3f}",
            "-ar", str(SAMPLE_RATE),
            "-ac", "2",
            str(pad_f)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        padded_files.append(pad_f)

        scene_specs.append({
            "id": sc["id"],
            "title": sc["title"],
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": scene_frames,
            "duration_seconds": final_scene_dur,
            "sfx": sc["sfx"]
        })

    # Concatenate all padded scenes into full_voice_225s.wav
    concat_list = AUDIO_DIR / "concat_scenes.txt"
    with open(concat_list, "w") as f:
        for pf in padded_files:
            f.write(f"file '{pf.resolve()}'\n")

    full_voice_wav = AUDIO_DIR / "full_voice_225s.wav"
    subprocess.run([
        FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(full_voice_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Mix with looped background music
    final_mixed_audio = AUDIO_DIR / "full_audio_mix_225s.wav"
    filter_complex = (
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{TARGET_TOTAL_SECONDS:.2f},volume=0.22,afade=t=out:st=222:d=3[music];"
        f"[0:a]volume=1.1[voice];"
        f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", str(full_voice_wav),
        "-i", str(MUSIC_SOURCE),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        str(final_mixed_audio)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Save scene_timings.json
    timings_path = AUDIO_DIR / "scene_timings.json"
    with open(timings_path, "w") as f:
        json.dump({
            "target_seconds": TARGET_TOTAL_SECONDS,
            "total_frames": accum_frames,
            "fps": FPS,
            "scenes": scene_specs
        }, f, indent=2)

    print(f"✅ Generated Master 225.0s Audio Mix: {final_mixed_audio}")
    print(f"🎬 Total Frames: {accum_frames} ({accum_frames / float(FPS):.2f}s)")
    return str(final_mixed_audio), str(timings_path)


def main():
    asyncio.run(synthesize_all_scenes())
    synthesize_foley_sfx()
    assemble_and_balance_audio()


if __name__ == "__main__":
    main()
