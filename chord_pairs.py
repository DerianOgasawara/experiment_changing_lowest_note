"""
chord_pairs.py
和音の最低音変化（転回形ペア）の定義モジュール。
今後、短三和音や四和音へ拡張する際は CHORD_CONFIGS に設定を追加するだけで対応可能。
"""

from typing import Dict, List

# 実験対象の和音タイプと、比較する転回形ペアの定義
CHORD_CONFIGS: Dict[str, Dict] = {
    "major": {
        "name": "長三和音 (Major Triad)",
        "pairs": [
            {
                "id": "A_root_1st",
                "label": "基本形 ↔ 第1転回形",
                "bass_interval": "長3度",
                "semitones": 4,
                "filename": "root_1st.wav",
            },
            {
                "id": "B_root_2nd",
                "label": "基本形 ↔ 第2転回形",
                "bass_interval": "完全5度",
                "semitones": 7,
                "filename": "root_2nd.wav",
            },
            {
                "id": "C_1st_2nd",
                "label": "第1転回形 ↔ 第2転回形",
                "bass_interval": "短3度",
                "semitones": 3,
                "filename": "1st_2nd.wav",
            },
        ],
    },
    
    # --- 拡張例（音声ファイルを用意したらコメントを外して使用可能） ---
     "minor": {
         "name": "短三和音 (Minor Triad)",
         "pairs": [
             {"id": "A_root_1st", "label": "基本形 ↔ 第1転回形", "bass_interval": "短3度", "semitones": 3, "filename": "root_1st.wav"},
             {"id": "B_root_2nd", "label": "基本形 ↔ 第2転回形", "bass_interval": "完全5度", "semitones": 7, "filename": "root_2nd.wav"},
             {"id": "C_1st_2nd",  "label": "第1転回形 ↔ 第2転回形", "bass_interval": "長3度", "semitones": 4, "filename": "1st_2nd.wav"},
         ],
     },
}


def get_pairs_by_chord_type(chord_type: str) -> List[Dict]:
    """指定された和音タイプのペア定義リストを返す"""
    if chord_type not in CHORD_CONFIGS:
        raise ValueError(f"未定義の和音タイプです: {chord_type}")
    return CHORD_CONFIGS[chord_type]["pairs"]