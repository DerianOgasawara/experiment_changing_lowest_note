"""
experiment.py
和音の最低音変化による類似度（変化の大きさ）評価実験モジュール（一対比較法・ループ再生対応）
"""

import random
import itertools
import json
import streamlit as st

from chord_pairs import CHORD_CONFIGS, get_pairs_by_chord_type
from audio_loader import load_chord_pair_audio, get_current_trial_base_note

# ==============================================================================
# 実験設定
# ==============================================================================
# 今回の実験で使用する和音タイプ（chord_pairs.py のキーを指定）
ACTIVE_CHORD_TYPES = ["major", "minor"]

# 全ペア組み合わせ（三和音なら3通り）を何周繰り返すか（例: 4周 × 3通り = 12試行）
REPEATS_PER_PAIR = 1
# ==============================================================================


def init_session_state():
    """セッション状態の初期化"""
    if "exp_started" not in st.session_state:
        st.session_state.exp_started = False
    if "trials" not in st.session_state:
        st.session_state.trials = []
    if "current_trial_idx" not in st.session_state:
        st.session_state.current_trial_idx = 0
    if "results" not in st.session_state:
        st.session_state.results = []
    if "exp_finished" not in st.session_state:
        st.session_state.exp_finished = False


def generate_trial_list() -> list[dict]:
    """
    各和音タイプの全ペア組み合わせを生成し、左右の提示順をカウンターバランスしてシャッフルする。
    """
    raw_trials = []

    for chord_type in ACTIVE_CHORD_TYPES:
        pairs = get_pairs_by_chord_type(chord_type)
        # 3つのペア (A, B, C) から2つを選ぶ全組み合わせ (A vs B, B vs C, C vs A)
        combinations = list(itertools.combinations(pairs, 2))

        for rep in range(REPEATS_PER_PAIR):
            for item_1, item_2 in combinations:
                # 偶数周と奇数周で左右の配置を反転させて順序効果を完全に相殺
                if (rep % 2 == 0) == random.choice([True, False]):
                    left_item, right_item = item_1, item_2
                else:
                    left_item, right_item = item_2, item_1

                raw_trials.append({
                    "chord_type": chord_type,
                    "chord_name": CHORD_CONFIGS[chord_type]["name"],
                    "left": left_item,
                    "right": right_item,
                })

    # 全体の試行順をランダムにシャッフル
    random.shuffle(raw_trials)

    # 試行番号を付与
    for idx, trial in enumerate(raw_trials):
        trial["trial_id"] = idx + 1

    return raw_trials


def run() -> dict:
    """
    app.py から呼び出されるメイン関数。
    実験完了時に {"status": "completed", "results_json": ...} を返す。
    """
    init_session_state()
    st.subheader("和音の響きの変化に関する聴取実験")

    # ---------------------------------------------------------
    # 1. 実験案内画面（未開始時）
    # ---------------------------------------------------------
    if not st.session_state.exp_started and not st.session_state.exp_finished:
        st.markdown("""
        **【実験手順】**
        1. 画面に表示される **「パターン 1」** と **「パターン 2」** の再生ボタンを押すと、2つの和音が交互にループ再生されます。
        2. 両方を十分に聴き比べ、**2つの和音の「響きの変化（違いの大きさ）」をより強く感じる方** を選んでください。
        3. 一方の音声を止めたい場合は、一時停止ボタンを押してからもう一方を再生してください。
        """)

        preview_trials = generate_trial_list()
        st.info(f"全 **{len(preview_trials)}** 試行の比較タスクを実施します。ヘッドホンまたはイヤホンの着用を推奨します。")

        if st.button("実験を開始する", type="primary"):
            st.session_state.trials = preview_trials
            st.session_state.current_trial_idx = 0
            st.session_state.results = []
            st.session_state.trial_base_notes = {}
            st.session_state.exp_started = True
            st.session_state.exp_finished = False
            st.rerun()

        return {"status": "not_started"}

    # ---------------------------------------------------------
    # 2. 実験タスク画面（進行中）
    # ---------------------------------------------------------
    if st.session_state.exp_started and not st.session_state.exp_finished:
        trials = st.session_state.trials
        idx = st.session_state.current_trial_idx
        total = len(trials)
        current = trials[idx]

        st.progress(idx / total)
        st.caption(f"試行進捗: {idx + 1} / {total}")

        st.markdown("##### 2つのループ音声を聴き比べてください")

        col_1, col_2 = st.columns(2)

        with col_1:
            st.markdown("### 🎵 パターン 1")
            audio_1 = load_chord_pair_audio(
                current["chord_type"],
                current["left"]["filename"],
                ACTIVE_CHORD_TYPES
            )
            # loop=True によりブラウザ上でシームレスにループ再生
            st.audio(audio_1, format="audio/wav", loop=True)

        with col_2:
            st.markdown("### 🎵 パターン 2")
            audio_2 = load_chord_pair_audio(
                current["chord_type"],
                current["right"]["filename"],
                ACTIVE_CHORD_TYPES
            )
            st.audio(audio_2, format="audio/wav", loop=True)

        st.write("---")
        st.write("**どちらの方が、繰り返される2つの和音の「響きの変化（違いの大きさ）」をより強く感じますか？**")

        selected_side = None

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🎵 パターン 1 の方が変化が大きい", key=f"btn_1_{idx}", use_container_width=True):
                selected_side = "left"
        with btn_col2:
            if st.button("🎵 パターン 2 の方が変化が大きい", key=f"btn_2_{idx}", use_container_width=True):
                selected_side = "right"

        # 回答後の記録と次の試行への遷移
        if selected_side is not None:
            left_item = current["left"]
            right_item = current["right"]

            if selected_side == "left":
                winner = left_item
                loser = right_item
            else:
                winner = right_item
                loser = left_item

            pair_ids = sorted([left_item["id"], right_item["id"]])

            st.session_state.results.append({
                "trial_no": idx + 1,
                "chord_type": current["chord_type"],
                "base_note": get_current_trial_base_note(),
                "pattern_1_id": left_item["id"],
                "pattern_2_id": right_item["id"],
                "selected_pattern": "1" if selected_side == "left" else "2",
                "winner_id": winner["id"],                 # ヒストグラム集計用（変化が大きいと選ばれたペアID）
                "winner_label": winner["label"],           # 例: "基本形 ↔ 第2転回形"
                "winner_interval": winner["bass_interval"],# 例: "完全5度"
                "winner_semitones": winner["semitones"],   # 例: 7
                "loser_id": loser["id"],
                "loser_semitones": loser["semitones"],
                "comparison_key": f"{pair_ids[0]}_vs_{pair_ids[1]}"
            })

            if idx + 1 < total:
                st.session_state.current_trial_idx += 1
            else:
                st.session_state.exp_started = False
                st.session_state.exp_finished = True
            st.rerun()

        return {"status": "in_progress"}

    # ---------------------------------------------------------
    # 3. 実験完了画面
    # ---------------------------------------------------------
    if st.session_state.exp_finished:
        st.success("🎉 全ての比較試行が完了しました！画面下の「回答を送信する」ボタンを押してください。")

        payload = {
            "active_chord_types": ACTIVE_CHORD_TYPES,
            "total_trials": len(st.session_state.results),
            "trials": st.session_state.results
        }

        return {
            "status": "completed",
            "results_json": json.dumps(payload, ensure_ascii=False)
        }


# 単体テスト用 (`streamlit run experiment.py` で動作確認可能)
if __name__ == "__main__":
    st.set_page_config(page_title="和音類似度比較実験", layout="wide")
    run()
