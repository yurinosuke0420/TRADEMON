import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="進化ツリー｜TRADEMON",
    layout="wide",
)

dex_file_name = "monster_dex.csv"

st.title("進化ツリー")
st.caption("モンスターの進化ルートと攻略ヒント")

ROOKIE_BRANCHES = {
    "DRAL": {"Defense": "GRANDRAKE", "Intelligence": "ABYSS_SERPENT", "Chaos": "SKYVERN"},
    "GARGANOS": {"Defense": "INFERNOS", "Intelligence": "IRONZAUR", "Chaos": "BERSAGON"},
    "FAIRIS": {"Defense": "LUMIFEA", "Attack": "MYSTIA", "Chaos": "VERLINA"},
    "SEIJAS": {"Defense": "ARKEIN", "Attack": "NOXIS", "Chaos": "LOGWELL"},
    "RAGNITE": {"Attack": "SILVARD", "Intelligence": "CELESTIA", "Chaos": "VALGAS"},
    "GARUSHELL": {"Attack": "LEAFELD", "Intelligence": "IRONSHELL", "Chaos": "ALMAZIO"},
    "REIGAL": {"Attack": "LEOGALG", "Defense": "VOLGALD", "Intelligence": "NEVALK"},
    "MELORIM": {"Attack": "RURUMESOM", "Defense": "SUYASLIN", "Intelligence": "POLTURN"},
}

ULTIMATE_EVOLUTION = {
    "GRANDRAKE": "ZAGROS", "ABYSS_SERPENT": "LEVIATAN", "SKYVERN": "VALZEON",
    "INFERNOS": "BLAZEREX", "IRONZAUR": "FORTZAUR", "BERSAGON": "RAGEGRAUL",
    "LUMIFEA": "LUMINARIA", "MYSTIA": "MISTINA", "VERLINA": "VERIS",
    "ARKEIN": "ARCANUS", "NOXIS": "NACTIS", "LOGWELL": "LOGION",
    "SILVARD": "SEIREA", "CELESTIA": "AQUARION", "VALGAS": "VALDION",
    "LEAFELD": "LEAFFORT", "IRONSHELL": "IRONFORT", "ALMAZIO": "GAIAROCK",
    "LEOGALG": "BALGULEO", "VOLGALD": "VOLTIGA", "NEVALK": "NELGROM",
    "RURUMESOM": "NANPINKING", "SUYASLIN": "FUKUMILORD", "POLTURN": "INAGOPRINCE",
}

MEGA_EVOLUTION = {
    "ZAGROS": "GAIARD", "LEVIATAN": "OCEANUS", "VALZEON": "ASTRAL",
    "BLAZEREX": "IGNIX", "FORTZAUR": "METALGALD", "RAGEGRAUL": "DEMONIRAL",
    "LUMINARIA": "ASTREA", "MISTINA": "AQUERIS", "VERIS": "SYLPHIA",
    "ARCANUS": "ENFERDIAS", "NACTIS": "ECLIPSION", "LOGION": "ZEULION",
    "SEIREA": "SEIREA-M", "AQUARION": "AQUARION-M", "VALDION": "GAIABASTION",
    "LEAFFORT": "LEAFORDION", "IRONFORT": "GORGONGALD", "GAIAROCK": "ORIHALGAIA",
    "BALGULEO": "LEOGKAISER", "VOLTIGA": "VOLKRONOS", "NELGROM": "NEBISREX",
    "NANPINKING": "MELANTIA", "FUKUMILORD": "POYAMEROS", "INAGOPRINCE": "RIKACLEAR",
}

CONDITION_TEXT = {
    "Attack": "攻撃力が高い",
    "Defense": "防御力が高い",
    "Intelligence": "知力が高い",
    "Chaos": "暴走度が高い",
}

HINT_TEXT = {
    "Attack": "良トレード回数と良トレードの質で上がります。",
    "Defense": "良トレードの質・振り返りEXPで上がり、無駄トレードで下がります。",
    "Intelligence": "振り返りメモの文字数で上がります。",
    "Chaos": "無駄トレード回数と無駄トレードの重さで上がります。",
}


def load_obtained_ids():
    if not os.path.exists(dex_file_name):
        return set()

    dex = pd.read_csv(dex_file_name)
    return set(dex["monster_id"].dropna().astype(str))


def find_image(monster_id):
    base_dir = "assets/cards"

    if not os.path.exists(base_dir):
        return None

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if monster_id in file and file.lower().endswith((".png", ".jpg", ".jpeg")):
                return os.path.join(root, file)

    return None


def is_obtained(monster_id, obtained_ids):
    return monster_id in obtained_ids


def shown_name(monster_id, obtained_ids):
    return monster_id if is_obtained(monster_id, obtained_ids) else "？？？"


def show_card(monster_id, stage, obtained_ids, height=230):
    obtained = is_obtained(monster_id, obtained_ids)
    image_path = find_image(monster_id)

    if obtained and image_path and os.path.exists(image_path):
        st.image(image_path, use_container_width=True, caption="クリックで拡大")
    else:
        st.markdown(
            f"""
            <div style="
                height:{height}px;
                border-radius:18px;
                background:linear-gradient(135deg,#020617,#111827);
                border:1px solid rgba(148,163,184,0.25);
                display:flex;
                align-items:center;
                justify-content:center;
                color:#f8fafc;
                font-size:42px;
                font-weight:1000;
            ">
                ？？？
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(f"**{shown_name(monster_id, obtained_ids)}**")
    st.caption(stage)


obtained_ids = load_obtained_ids()

st.metric("発見済み", f"{len(obtained_ids)} 体")
st.divider()

for rookie_id, branch_table in ROOKIE_BRANCHES.items():
    title = shown_name(rookie_id, obtained_ids)

    with st.expander(f"{title}ルート", expanded=is_obtained(rookie_id, obtained_ids)):

        top_left, top_right = st.columns([1, 2.2])

        with top_left:
            show_card(rookie_id, "成長期", obtained_ids, height=230)

        with top_right:
            st.markdown("#### 分岐条件")
            st.caption("成熟期への分岐は、成長期に進化した後の累計ステータスで決まります。")
            for condition in branch_table.keys():
                st.markdown(f"- **{CONDITION_TEXT[condition]}**：{HINT_TEXT[condition]}")

        st.markdown("---")

        for condition, champion_id in branch_table.items():
            ultimate_id = ULTIMATE_EVOLUTION.get(champion_id)
            mega_id = MEGA_EVOLUTION.get(ultimate_id)

            st.markdown(f"### {CONDITION_TEXT[condition]} ルート")

            c1, arrow1, c2, arrow2, c3 = st.columns([1.2, 0.18, 1.2, 0.18, 1.2])

            with c1:
                show_card(champion_id, "成熟期", obtained_ids)

            with arrow1:
                st.markdown(
                    "<div style='text-align:center; font-size:34px; margin-top:105px;'>→</div>",
                    unsafe_allow_html=True,
                )

            with c2:
                if ultimate_id:
                    show_card(ultimate_id, "完全体", obtained_ids)

            with arrow2:
                st.markdown(
                    "<div style='text-align:center; font-size:34px; margin-top:105px;'>→</div>",
                    unsafe_allow_html=True,
                )

            with c3:
                if mega_id:
                    show_card(mega_id, "究極体", obtained_ids)

            st.markdown("---")