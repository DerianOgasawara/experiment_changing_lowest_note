"""
audio_loader.py
自作した転回形ループWAVファイルを読み込み、バイナリ形式で返すモジュール。
"""

import os
import streamlit as st
from chord_pairs import CHORD_CONFIGS

AUDIO_DIR = "audio"

# 基準音リスト（用意したキーに合わせて増減可能）
BASE_NOTES = [
    "C3", "F3", "G3"
]

NOTE_ALT_MAP = {
    "Cs3": "C#3", "Ds3": "D#3", "Fs3": "F#3", "Gs3": "G#3", "As3": "A#3"
}


def check_audio_files(active_chord_types: list[str]) -> list[str]:
    """
    有効な和音タイプについて、全基準音 × 全ペアのWAVファイルが存在するか確認する。
    """
    missing_files = []
    for chord_type in active_chord_types:
        pairs = CHORD_CONFIGS[chord_type]["pairs"]
        for base_note in BASE_NOTES:
            alt_base = NOTE_ALT_MAP.get(base_note, base_note)
            for pair in pairs:
                fname = pair["filename"]
                paths_to_check = [
                    os.path.join(AUDIO_DIR, chord_type, base_note, fname),
                    os.path.join(AUDIO_DIR, chord_type, alt_base, fname),
                    os.path.join(AUDIO_DIR, chord_type, f"{base_note}_{fname}"),
                    os.path.join(AUDIO_DIR, f"{chord_type}_{base_note}_{fname}"),
                ]
                if not any(os.path.exists(p) for p in paths_to_check):
                    missing_files.append(f"{AUDIO_DIR}/{chord_type}/{base_note}/{fname}")
    return missing_files


def load_chord_pair_audio(
    chord_type: str,
    base_note: str,
    filename: str,
    active_chord_types: list[str]
) -> bytes:
    """
    指定された和音タイプ・基準音・ファイル名のWAVデータを読み込む。
    """
    if "audio_checked" not in st.session_state:
        st.session_state.audio_checked = True
        missing = check_audio_files(active_chord_types)
        if missing:
            st.error(f"⚠️ 以下の音声ファイルが見つかりません（計 {len(missing)} 件）:")
            for m in missing[:15]:
                st.write(f"- `{m}`")
            if len(missing) > 15:
                st.write(f"  ...他 {len(missing) - 15} 件")

    alt_base = NOTE_ALT_MAP.get(base_note, base_note)

    paths_to_check = [
        os.path.join(AUDIO_DIR, chord_type, base_note, filename),        # 例: audio/major/C3/root_1st.wav
        os.path.join(AUDIO_DIR, chord_type, alt_base, filename),         # 例: audio/major/C#3/root_1st.wav
        os.path.join(AUDIO_DIR, chord_type, f"{base_note}_{filename}"),  # 例: audio/major/C3_root_1st.wav
        os.path.join(AUDIO_DIR, f"{chord_type}_{base_note}_{filename}"), # 例: audio/major_C3_root_1st.wav
    ]

    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()

    err_msg = f"音声ファイルが見つかりません: {chord_type}/{base_note}/{filename}"
    st.error(f"❌ {err_msg}")
    raise FileNotFoundError(err_msg)
