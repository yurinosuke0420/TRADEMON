import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(
    page_title="月末リザルト｜TRADEMON",
    layout="wide",
)

file_name = "record.csv"
game_state_file_name = "game_state.csv"
state_file_name = "evolution_state.csv"

st.title("月末リザルト")
st.caption("月ごとのTRADEMON結果を確認できます。")


def get_previous_month():
    today = datetime.today()
    year = today.year
    month = today.month - 1

    if month == 0:
        month = 12
        year -= 1

    return f"{year}-{month:02d}"


def find_image(monster_id):
    base_dir = "assets/cards"

    if not os.path.exists(base_dir):
        return None

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if (
                monster_id in file
                and file.lower().endswith((".png", ".jpg", ".jpeg"))
            ):
                return os.path.join(root, file)

    return None


def save_game_state(active_month, pending_result_month=None):
    data = {
        "active_month": [active_month],
        "pending_result_month": [pending_result_month],
        "保存日時": [datetime.now()],
    }

    df = pd.DataFrame(data)
    df.to_csv(game_state_file_name, index=False)

def reset_evolution_state_for_new_month(new_month):
    data = {
        "月": [new_month],
        "monster_type": [None],
        "monster_id": [None],
        "保存日時": [datetime.now()],
    }

    df = pd.DataFrame(data)

    if os.path.exists(state_file_name):
        old_df = pd.read_csv(state_file_name)
        old_df = old_df[old_df["月"] != new_month]
        df = pd.concat([old_df, df], ignore_index=True)

    df.to_csv(state_file_name, index=False)


def load_pending_month():
    if not os.path.exists(game_state_file_name):
        return None

    game_state_df = pd.read_csv(game_state_file_name)

    if len(game_state_df) == 0:
        return None

    pending_month = game_state_df.iloc[-1]["pending_result_month"]

    if pd.isna(pending_month):
        return None

    return pending_month


def get_title_and_comment(stats):
    clean_stats = {
        key: 0 if pd.isna(value) else int(value)
        for key, value in stats.items()
    }

    mvp_stat = max(clean_stats, key=clean_stats.get)
    mvp_value = clean_stats[mvp_stat]

    values = list(clean_stats.values())
    max_value = max(values)
    min_value = min(values)

    if min_value >= 150:
        title = "市場を制する者"
        comment = "総合力の高さが際立った月。"

    elif max_value - min_value <= 30 and max_value >= 50:
        title = "均衡の投資家"
        comment = "バランスの取れた投資行動ができた月。"

    else:
        title_map = {
            "攻撃力": "強気の勝負師",
            "防御力": "守りの名手",
            "知力": "分析の探求者",
            "暴走度": "大胆なる挑戦者",
        }

        comment_map = {
            "攻撃力": "積極的なトレードが光った月。",
            "防御力": "リスク管理と堅実さが光った月。",
            "知力": "振り返りと分析が充実した月。",
            "暴走度": "大胆なトレード傾向が強かった月。",
        }

        title = title_map[mvp_stat]
        comment = comment_map[mvp_stat]

    return title, mvp_stat, mvp_value, comment


if not os.path.exists(file_name):
    st.warning("まだ記録データがありません。")
    st.stop()

history = pd.read_csv(file_name)

if len(history) == 0:
    st.warning("まだ記録データがありません。")
    st.stop()

available_months = sorted(history["月"].dropna().unique(), reverse=True)

default_month = get_previous_month()

if default_month in available_months:
    default_index = available_months.index(default_month)
else:
    default_index = 0

selected_month = st.selectbox(
    "表示する月",
    available_months,
    index=default_index,
)

month_data = history[history["月"] == selected_month]

if len(month_data) == 0:
    st.info(f"{selected_month} のデータがありません。")
    st.stop()

# ----------------------------
# 月間集計
# ----------------------------

month_profit = month_data["損益%"].sum()
month_exp = month_data["日次EXP"].sum()

good_count = int(month_data["良トレード回数"].sum())
bad_count = int(month_data["無駄トレード回数"].sum())

avg_good_quality = (
    month_data["良トレードの質"].sum() / good_count
    if good_count > 0 else 0
)

avg_bad_weight = (
    month_data["無駄トレードの重さ"].sum() / bad_count
    if bad_count > 0 else 0
)

trade_quality_score = good_count - bad_count

total_attack = month_data["攻撃力"].sum()
total_defense = month_data["防御力"].sum()
total_intelligence = month_data["知力"].sum()
total_chaos = month_data["暴走度"].sum()

stats = {
    "攻撃力": total_attack,
    "防御力": total_defense,
    "知力": total_intelligence,
    "暴走度": total_chaos,
}

monthly_title, mvp_stat, mvp_value, title_comment = get_title_and_comment(stats)

st.success(f"{selected_month} のTRADEMON結果")

# ----------------------------
# 最終進化モンスター
# ----------------------------

monster_rows = month_data.dropna(subset=["monster_id"])

if len(monster_rows) > 0:
    final_row = monster_rows.iloc[-1]

    final_monster_id = final_row["monster_id"]
    final_stage = final_row["進化段階"]
    final_type = final_row["monster_type"]

    image_path = find_image(final_monster_id)

    st.markdown("## 🏆 最終進化")

    left, right = st.columns([1, 1.5])

    with left:
        if image_path and os.path.exists(image_path):
            st.image(image_path, use_container_width=True)

    with right:
        st.markdown(f"### {final_monster_id}")
        st.markdown(f"**進化段階：** {final_stage}")
        st.markdown(f"**系統：** {final_type}")

        st.markdown("---")

        st.markdown(
            f"""
            <div style="
                font-size: 34px;
                font-weight: 1000;
                color: #fbbf24;
                text-shadow:
                    0 0 8px rgba(251,191,36,0.55),
                    0 0 18px rgba(251,191,36,0.35);
                margin-top: 36px;
                margin-bottom: 12px;
            ">
                《 {monthly_title} 》
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"**強み：** {mvp_stat}（{int(mvp_value)}）")
        st.caption(title_comment)

    st.divider()

# ----------------------------
# 前月比EXP
# ----------------------------

previous_months = [
    m for m in available_months
    if m < selected_month
]

if len(previous_months) > 0:
    prev_month = sorted(previous_months, reverse=True)[0]
    prev_month_data = history[history["月"] == prev_month]
    prev_month_exp = prev_month_data["日次EXP"].sum()
    exp_delta = int(month_exp - prev_month_exp)
else:
    exp_delta = None

# ----------------------------
# 月間指標
# ----------------------------

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "月間EXP",
        int(month_exp),
        delta=f"前月比 {exp_delta:+}" if exp_delta is not None else None,
    )

with c2:
    st.metric("月間損益", f"{month_profit:.1f}%")

with c3:
    st.metric("品質スコア", f"{trade_quality_score:+}")

st.divider()

# ----------------------------
# 良トレ / 無駄トレ
# ----------------------------

left, right = st.columns(2)

with left:
    st.subheader("良トレード")

    st.markdown(
        f"""
**回数：** {good_count}回  
**平均質：** {avg_good_quality:.1f} / 5
"""
    )

with right:
    st.subheader("無駄トレード")

    st.markdown(
        f"""
**回数：** {bad_count}回  
**平均重さ：** {avg_bad_weight:.1f} / 5
"""
    )

# ----------------------------
# 次の月へ
# ----------------------------

st.divider()

st.markdown("## 次の月へ")

pending_month = load_pending_month()

if pending_month == selected_month:

    if st.button(
        "次の月へ進む",
        use_container_width=True,
    ):

        today_month = date.today().strftime("%Y-%m")

        save_game_state(
            active_month=today_month,
            pending_result_month=None,
        )

        reset_evolution_state_for_new_month(today_month)

        st.balloons()

        st.markdown(
            """
            <div style="
                margin-top: 18px;
                padding: 22px;
                border-radius: 20px;
                border: 1px solid rgba(251, 191, 36, 0.55);
                background: linear-gradient(135deg, rgba(251,191,36,0.18), rgba(59,130,246,0.14));
                text-align: center;
            ">
                <div style="
                    font-size: 18px;
                    color: #fbbf24;
                    font-weight: 900;
                    letter-spacing: 0.16em;
                ">
                    NEW SEASON
                </div>
                <div style="
                    font-size: 30px;
                    color: #f8fafc;
                    font-weight: 1000;
                    margin-top: 8px;
                ">
                    新たなタマゴが誕生した！
                </div>
                <div style="
                    font-size: 15px;
                    color: #cbd5e1;
                    margin-top: 8px;
                ">
                    新しい月のTRADEMON育成が始まります。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info("Homeに戻ると、新しいタマゴから育成を開始できます。")

else:

    st.info("月末処理対象の月ではありません。")