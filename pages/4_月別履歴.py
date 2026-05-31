import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="月別履歴｜TRADEMON",
    layout="wide",
)

st.title("月別履歴")
st.caption("これまでのTRADEMON育成履歴")

file_name = "record.csv"


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


def get_title(stats):
    attack = stats["攻撃力"]
    defense = stats["防御力"]
    intelligence = stats["知力"]
    chaos = stats["暴走度"]

    values = [attack, defense, intelligence, chaos]
    max_value = max(values)
    min_value = min(values)

    if min_value >= 150:
        return "市場を制する者"

    if max_value - min_value <= 30 and max_value >= 50:
        return "均衡の投資家"

    if max_value == attack:
        return "強気の勝負師"
    elif max_value == defense:
        return "守りの名手"
    elif max_value == intelligence:
        return "分析の探求者"
    else:
        return "大胆なる挑戦者"


if not os.path.exists(file_name):
    st.warning("record.csv が見つかりません。")
    st.stop()

all_history = pd.read_csv(file_name)

if len(all_history) == 0:
    st.warning("履歴データがありません。")
    st.stop()

monster_history = all_history.dropna(subset=["monster_id"])

if len(monster_history) == 0:
    st.info("まだ進化履歴がありません。")
    st.stop()

monster_history = monster_history.sort_values("保存日時")

monthly_last = monster_history.groupby("月").tail(1)
monthly_last = monthly_last.sort_values("月", ascending=False)

cols = st.columns(3)

for display_index, (_, row) in enumerate(monthly_last.iterrows()):
    col = cols[display_index % 3]

    with col:
        month = row["月"]

        month_data = all_history[all_history["月"] == month]

        month_exp = int(month_data["日次EXP"].sum())
        month_profit = round(month_data["損益%"].sum(), 1)

        stats = {
            "攻撃力": month_data["攻撃力"].sum(),
            "防御力": month_data["防御力"].sum(),
            "知力": month_data["知力"].sum(),
            "暴走度": month_data["暴走度"].sum(),
        }

        title = get_title(stats)

        st.markdown(f"## {month}")

        image_path = find_image(str(row["monster_id"]))

        if image_path and os.path.exists(image_path):
            st.image(image_path, use_container_width=True)

        st.markdown(
            f"""
            <div style="
                font-size: 22px;
                font-weight: 900;
                color: #fbbf24;
                text-align: center;
                margin-top: 8px;
                margin-bottom: 12px;
                text-shadow:
                    0 0 8px rgba(251,191,36,0.55),
                    0 0 18px rgba(251,191,36,0.35);
            ">
                《{title}》
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="line-height:1.45;">
                <div style="font-size:24px; font-weight:900; margin-bottom:8px;">
                    {row['monster_id']}
                </div>
                <div><b>進化段階：</b>{row['進化段階']}</div>
                <div><b>系統：</b>{row['monster_type']}</div>
                <div style="margin-top:10px;"><b>月間EXP：</b>{month_exp}</div>
                <div><b>月間損益：</b>{month_profit:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()