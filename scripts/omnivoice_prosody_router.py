"""Normalize speech and route explicit user energy preferences to local OmniVoice."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

PROSODY = {
    "yukino": {"speeds": [0.92, 0.88, 0.89, 0.90], "pauses": [380, 520, 480, 420],
        "voice": "female, soft composed gentle voice, soothing intimate Mommy ASMR warmth, calm breathing pace"},
    "shizuka": {"speeds": [0.94, 0.90, 0.91, 0.93], "pauses": [340, 450, 430, 360],
        "voice": "female, mature warm contralto, calm motherly teacher voice, clear articulation, reassuring mentor cadence"},
    "shikaku": {"speeds": [0.94, 0.91, 0.92, 0.95], "pauses": [350, 440, 420, 310],
        "voice": "male, deep calm fatherly baritone, relaxed strategic commander tone, steady grounded pace"},
    "kiki-chii": {"speeds": [1.00, 0.93, 0.94, 0.97], "pauses": [260, 380, 370, 290],
        "voice": "female, bright expressive warm voice, enthusiastic creative director tone, lively natural cadence"},
    "val": {"speeds": [0.97, 0.93, 0.94, 0.97], "pauses": [300, 390, 380, 290],
        "voice": "female, clear composed analytical voice, precise academic articulation, calm steady rhythm"},
}
ENGINE_VOICES = {
    "yukino": "female, young adult, low pitch, whisper",
    "shizuka": "female, middle-aged, low pitch",
    "shikaku": "male, middle-aged, very low pitch",
    "kiki-chii": "female, young adult, high pitch",
    "val": "female, young adult, moderate pitch",
}
STATES = ("normal", "calm", "tired", "incident")

def normalize(text, role):
    replacement = " Detail kode sudah tertulis di layar. " if role == "shikaku" else " Rincian teknis sudah tertulis di layar. "
    fence = chr(96) * 3
    text = re.sub("(?s)" + fence + ".*?" + fence, replacement, text)
    text = re.sub(r"https?://\S+", " tautan sumber ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*(?:#{1,6}|[-*>])\s*", "", text)
    text = re.sub(r"[*_\x60~]+", "", text)
    for pattern, spoken in ((r"\bMSSHI\b", "M S S H I"), (r"\bMuZA\b", "Muza"),
            (r"\bS1\b", "Strata Satu"), (r"\bS2\b", "Strata Dua"), (r"\bS3\b", "Strata Tiga"),
            (r"\bRp0\b", "nol rupiah"), (r"\bUMKM\b", "U M K M")):
        text = re.sub(pattern, spoken, text)
    return re.sub(r"\s+", " ", text).strip()

def parameters(role, state):
    row = PROSODY[role]
    index = STATES.index(state)
    return {"speed": row["speeds"][index], "pause_ms": row["pauses"][index],
            "voice": "instruct:" + ENGINE_VOICES[role], "persona_style": row["voice"], "state": state}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--role", choices=PROSODY, required=True)
    parser.add_argument("--state", choices=STATES)
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--format", choices=("wav", "mp3", "ogg", "flac"), default="wav")
    parser.add_argument("--describe", action="store_true")
    args = parser.parse_args(argv)
    state = args.state
    if state is None:
        preference = args.home / "msshi-private/integrations/voice-state" / (args.role + ".json")
        state = "normal"
        if preference.is_file():
            value = json.loads(preference.read_text(encoding="utf-8")).get("state", "normal")
            state = value if value in STATES else "normal"
    selected = parameters(args.role, state)
    if args.describe:
        print(json.dumps(selected))
        return 0
    runtime = args.home / "msshi-private/omnivoice-runtime"
    model = runtime / "model"
    if not (model / "model.safetensors").is_file():
        raise FileNotFoundError("Install the verified OmniVoice model first.")
    text = normalize(args.text_file.read_text(encoding="utf-8-sig"), args.role)
    if not text:
        raise ValueError("No spoken text remains after normalization.")
    if len(text) > 1500:
        raise ValueError("Use speech chunks below 1500 characters on this local CPU runtime.")
    os.environ.update(HF_HOME=str(runtime / "hf-cache"), HF_HUB_OFFLINE="1",
                      HF_HUB_DISABLE_XET="1", TRANSFORMERS_OFFLINE="1",
                      OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", NUMBA_NUM_THREADS="2")
    os.environ["OMNIVOICE_MODEL"] = str(model)
    os.environ["OMNIVOICE_DEVICE"] = "cpu"
    os.environ["OMNIVOICE_DTYPE"] = "float32"
    os.environ["OMNIVOICE_NUM_STEP"] = "16"
    os.environ["OMNIVOICE_LOAD_ASR"] = "false"
    os.environ["OMNIVOICE_LANGUAGE"] = "Indonesian"
    os.environ["OMNIVOICE_VOICE"] = selected["voice"]
    ffmpeg = args.home / "tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe"
    if ffmpeg.is_file():
        os.environ["FFMPEG_BINARY"] = str(ffmpeg)
        os.environ["PATH"] = str(ffmpeg.parent) + os.pathsep + os.environ.get("PATH", "")
    import torch
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    from hermes_omnivoice.provider import OmniVoiceTTSProvider
    args.output.parent.mkdir(parents=True, exist_ok=True)
    print("OmniVoice loading local model for this speech request.", flush=True)
    provider = OmniVoiceTTSProvider()
    produced = provider.synthesize(text, str(args.output), voice=selected["voice"],
                                  model=str(model), speed=selected["speed"], format=args.format)
    print(json.dumps({"output": produced, "role": args.role, "prosody": selected,
                      "unload": "process exit", "at": datetime.now(timezone.utc).isoformat()}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
