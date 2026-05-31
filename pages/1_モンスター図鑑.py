import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="モンスター図鑑｜TRADEMON",
    layout="wide",
)

dex_file_name = "monster_dex.csv"

st.markdown("# 📖 モンスター図鑑")
st.caption("これまでに出会ったTRADEMONたち")

FULL_DEX = {
    "成長期": [
        "DRAL", "GARGANOS", "FAIRIS", "SEIJAS",
        "RAGNITE", "GARUSHELL", "REIGAL", "MELORIM"
    ],

    "成熟期": [
        "GRANDRAKE", "ABYSS_SERPENT", "SKYVERN",
        "INFERNOS", "IRONZAUR", "BERSAGON",
        "LUMIFEA", "MYSTIA", "VERLINA",
        "ARKEIN", "NOXIS", "LOGWELL",
        "SILVARD", "CELESTIA", "VALGAS",
        "LEAFELD", "IRONSHELL", "ALMAZIO",
        "LEOGALG", "VOLGALD", "NEVALK",
        "RURUMESOM", "SUYASLIN", "POLTURN"
    ],

    "完全体": [
        "ZAGROS", "LEVIATAN", "VALZEON",
        "BLAZEREX", "FORTZAUR", "RAGEGRAUL",
        "LUMINARIA", "MISTINA", "VERIS",
        "ARCANUS", "NACTIS", "LOGION",
        "SEIREA", "AQUARION", "VALDION",
        "LEAFFORT", "IRONFORT", "GAIAROCK",
        "BALGULEO", "VOLTIGA", "NELGROM",
        "NANPINKING", "FUKUMILORD", "INAGOPRINCE"
    ],

    "究極体": [
        "GAIARD", "OCEANUS", "ASTRAL",
        "IGNIX", "METALGALD", "DEMONIRAL",
        "ASTREA", "AQUERIS", "SYLPHIA",
        "ENFERDIAS", "ECLIPSION", "ZEULION",
        "SEIREA-M", "AQUARION-M", "GAIABASTION",
        "LEAFORDION", "GORGONGALD", "ORIHALGAIA",
        "LEOGKAISER", "VOLKRONOS", "NEBISREX",
        "MELANTIA", "POYAMEROS", "RIKACLEAR"
    ]
}


def find_image_by_monster_id(monster_id):
    base_dir = "assets/cards"

    if not os.path.exists(base_dir):
        return None

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if monster_id in file and file.lower().endswith((".png", ".jpg", ".jpeg")):
                return os.path.join(root, file)

    return None


if os.path.exists(dex_file_name):
    dex = pd.read_csv(dex_file_name)
    obtained_ids = set(dex["monster_id"].dropna().astype(str))
else:
    obtained_ids = set()

total_count = sum(len(v) for v in FULL_DEX.values())
obtained_count = sum(
    monster_id in obtained_ids
    for monsters in FULL_DEX.values()
    for monster_id in monsters
)

st.metric("収集率", f"{obtained_count} / {total_count} 体")
st.caption("取得済みカードはクリックで拡大できます。")

st.divider()

tab_rookie, tab_champion, tab_ultimate, tab_mega = st.tabs(
    ["成長期", "成熟期", "完全体", "究極体"]
)

tab_map = {
    "成長期": tab_rookie,
    "成熟期": tab_champion,
    "完全体": tab_ultimate,
    "究極体": tab_mega,
}

for stage, tab in tab_map.items():

    with tab:
        cols = st.columns(3)

        for i, monster_id in enumerate(FULL_DEX[stage]):

            col = cols[i % 3]
            obtained = monster_id in obtained_ids
            image_path = find_image_by_monster_id(monster_id)

            with col:
                if obtained:

                    if image_path and os.path.exists(image_path):
                        st.image(
                            image_path,
                            use_container_width=True,
                            caption="クリックで拡大",
                        )
                    else:
                        st.warning("画像なし")

                    st.markdown(f"**{monster_id}**")
                    st.caption("登録済み")

                else:
                    st.markdown(
                        """
                        <div style="
                            height: 360px;
                            border-radius: 18px;
                            background: linear-gradient(135deg, #020617, #111827);
                            border: 1px solid rgba(148, 163, 184, 0.25);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: #f8fafc;
                            font-size: 42px;
                            font-weight: 1000;
                        ">
                            ？？？
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown("**？？？**")
                    st.caption("未登録")