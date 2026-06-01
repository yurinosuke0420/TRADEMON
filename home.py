import streamlit as st
import pandas as pd
from datetime import datetime, date
from zoneinfo import ZoneInfo
import os
import gspread
from google.oauth2.service_account import Credentials

from monster_master import MONSTER_MASTER

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES,
)

gc = gspread.authorize(creds)

SPREADSHEET_ID = "1oQ5PFjVQaeHAtfOoRdaUs1KUjsJmEcemrA2KX5XSUKU"
sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("records")

def read_records_from_sheet():
    values = sheet.get_all_values()

    if len(values) <= 1:
        return pd.DataFrame()

    headers = values[0]
    rows = values[1:]

    return pd.DataFrame(rows, columns=headers)


def append_record_to_sheet(record_dict):
    existing_values = sheet.get_all_values()

    if len(existing_values) == 0:
        sheet.append_row(list(record_dict.keys()))

    safe_values = []

    for value in record_dict.values():

        if pd.isna(value):
            safe_values.append("")

        elif isinstance(value, (datetime, date)):
            safe_values.append(
                value.strftime("%Y-%m-%d %H:%M:%S")
            )

        else:
            safe_values.append(value)

    sheet.append_row(safe_values)

st.set_page_config(
    page_title="TRADEMON",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #020617;
        --panel: #0f172a;
        --panel-2: #111827;
        --line: #334155;
        --text: #f8fafc;
        --muted: #94a3b8;
        --gold: #fbbf24;
        --gold-2: #f59e0b;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(124, 58, 237, 0.18), transparent 32%),
            radial-gradient(circle at top right, rgba(251, 191, 36, 0.10), transparent 28%),
            var(--bg);
        color: var(--text);
    }

    .block-container {
        padding-top: 24px;
        padding-bottom: 40px;
        max-width: 1180px;
    }

    .main-title {
        font-size: 52px;
        font-weight: 1000;
        margin-bottom: 2px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: linear-gradient(180deg, #fde68a 0%, #fbbf24 45%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 22px rgba(251,191,36,0.18);
    }

    .title-sub {
        font-size: 14px;
        letter-spacing: 0.28em;
        color: #94a3b8;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .sub-title {
        color: var(--muted);
        margin-bottom: 20px;
        font-size: 15px;
    }

    .panel-title {
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 10px;
    }

    .evolution-badge {
        display: inline-block;
        background: rgba(251, 191, 36, 0.16);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.40);
        border-radius: 999px;
        padding: 7px 14px;
        font-size: 16px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .exp-note {
        color: #fbbf24;
        font-size: 18px;
        font-weight: 900;
        margin-top: 8px;
        margin-bottom: 2px;
    }

    .exp-sub-note {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 4px;
    }

    .compact-slider-label {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 800;
        margin-bottom: 6px;
        margin-top: 2px;
    }



    .monster-name {
        font-size: 36px;
        font-weight: 950;
        margin-top: 4px;
        margin-bottom: 4px;
        line-height: 1.05;
        letter-spacing: 0.02em;
    }

    .monster-sub {
        color: var(--muted);
        font-size: 14px;
        margin-bottom: 12px;
    }


    .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-top: 12px;
    }

    .info-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 16px;
        padding: 10px;
        text-align: center;
    }

    .info-label {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 4px;
    }

    .info-value {
        font-size: 20px;
        font-weight: 900;
        color: #f8fafc;
    }

    .input-row {
        padding: 3px 0 5px 0;
        border-bottom: 1px solid rgba(148, 163, 184, 0.10);
    }

    .input-row-last {
        padding: 3px 0 0px 0;
    }

    .row-title {
        font-size: 15px;
        font-weight: 850;
        color: #f1f5f9;
        margin-bottom: 0px;
        letter-spacing: 0.01em;
    }


    .stepper-value {
        text-align: center;
        font-size: 22px;
        line-height: 32px;
        font-weight: 900;
        color: #f8fafc;
    }

    .metric-strip {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 14px;
        padding: 6px;
        text-align: center;
    }

    .metric-label {
        color: var(--muted);
        font-size: 11px;
        margin-bottom: 2px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 17px;
        font-weight: 900;
    }

    .save-button-note {
        color: var(--muted);
        font-size: 12px;
        text-align: center;
        margin-top: -4px;
        margin-bottom: 8px;
    }

    div.stButton > button {
        border-radius: 14px;
        font-weight: 800;
        min-height: 36px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        background: rgba(15, 23, 42, 0.9);
        color: #f8fafc;
    }

    div.stButton > button:hover {
        border-color: var(--gold);
        color: var(--gold);
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--gold), var(--gold-2));
        color: #111827;
        border: none;
        min-height: 48px;
        font-size: 16px;
        box-shadow: 0 10px 24px rgba(245, 158, 11, 0.24);
    }

    div.stButton > button[kind="primary"]:hover {
        color: #111827;
        filter: brightness(1.05);
    }

    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stDateInput"] input {
        background-color: rgba(2, 6, 23, 0.88);
        color: #f8fafc;
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.26);
    }

    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background-color: var(--gold) !important;
    }

    div[data-testid="stSlider"] [role="slider"] {
        background-color: var(--gold) !important;
        border: 3px solid #fff !important;
        width: 18px !important;
        height: 18px !important;
        box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.25);
    }

    div[data-testid="stSlider"] {
        padding-top: 4px !important;
        padding-bottom: 0px !important;
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 62px !important;
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title-sub">MONSTER STOCK EVOLUTION</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">TRADEMON</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">今日のトレードを記録して、今月のモンスターを育てよう</div>', unsafe_allow_html=True)

file_name = "record.csv"
state_file_name = "evolution_state.csv"
dex_file_name = "monster_dex.csv"
game_state_file_name = "game_state.csv"

stages = ["闇タマゴ", "タマゴ", "幼体", "成長期", "成熟期", "完全体", "究極体"]

CHAMPION_BRANCHES = {
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
    "AQUARION": "AQUARION-M", "SEIREA": "SEIREA-M", "VALDION": "GAIABASTION",
    "LEAFFORT": "LEAFORDION", "IRONFORT": "GORGONGALD", "GAIAROCK": "ORIHALGAIA",
    "BALGULEO": "LEOGKAISER", "VOLTIGA": "VOLKRONOS", "NELGROM": "NEBISREX",
    "NANPINKING": "MELANTIA", "FUKUMILORD": "POYAMEROS", "INAGOPRINCE": "RIKACLEAR",
}


def get_target_stage_index(month_exp):
    if month_exp < 0:
        return 0
    elif month_exp < 30:
        return 1
    elif month_exp < 80:
        return 2
    elif month_exp < 150:
        return 3
    elif month_exp < 220:
        return 4
    elif month_exp < 300:
        return 5
    else:
        return 6


def get_next_target(stage_name):
    targets = {
        "闇タマゴ": 0,
        "タマゴ": 30,
        "幼体": 80,
        "成長期": 150,
        "成熟期": 220,
        "完全体": 300,
        "究極体": None,
    }
    return targets[stage_name]


def load_evolution_state(month):
    if not os.path.exists(state_file_name):
        return None

    state_df = pd.read_csv(state_file_name)
    month_state = state_df[state_df["月"] == month]

    if len(month_state) == 0:
        return None

    latest_state = month_state.iloc[-1]
    return {
        "monster_type": latest_state["monster_type"],
        "monster_id": latest_state["monster_id"],
    }


def save_evolution_state(month, monster_type, monster_id):
    data = {
        "月": [month],
        "monster_type": [monster_type],
        "monster_id": [monster_id],
        "保存日時": [datetime.now(ZoneInfo("Asia/Tokyo"))],
    }

    df = pd.DataFrame(data)

    if os.path.exists(state_file_name):
        old_df = pd.read_csv(state_file_name)
        old_df = old_df[old_df["月"] != month]
        df = pd.concat([old_df, df], ignore_index=True)

    df.to_csv(state_file_name, index=False)


def clear_evolution_state(month):
    if not os.path.exists(state_file_name):
        return

    state_df = pd.read_csv(state_file_name)
    state_df = state_df[state_df["月"] != month]
    state_df.to_csv(state_file_name, index=False)

def load_game_state():
    if not os.path.exists(game_state_file_name):
        return {
            "active_month": datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m"),
            "pending_result_month": None,
        }

    state_df = pd.read_csv(game_state_file_name)

    if len(state_df) == 0:
        return {
            "active_month": datetime.now(ZoneInfo("Asia/Tokyo")).date().strftime("%Y-%m"),
            "pending_result_month": None,
        }

    latest_state = state_df.iloc[-1]

    pending_result_month = latest_state.get("pending_result_month", None)

    if pd.isna(pending_result_month):
        pending_result_month = None

    return {
        "active_month": latest_state["active_month"],
        "pending_result_month": pending_result_month,
    }


def save_game_state(active_month, pending_result_month=None):
    data = {
        "active_month": [active_month],
        "pending_result_month": [pending_result_month],
        "保存日時": [datetime.now(ZoneInfo("Asia/Tokyo"))],
    }

    df = pd.DataFrame(data)
    df.to_csv(game_state_file_name, index=False)


def register_monster_to_dex(month, evolution, monster_type, monster_id):
    if monster_id is None:
        return

    if evolution not in ["成長期", "成熟期", "完全体", "究極体"]:
        return

    new_data = {
        "初登録日時": [datetime.now(ZoneInfo("Asia/Tokyo"))],
        "初登録月": [month],
        "進化段階": [evolution],
        "monster_type": [monster_type],
        "monster_id": [monster_id],
    }

    new_df = pd.DataFrame(new_data)

    if os.path.exists(dex_file_name):
        old_df = pd.read_csv(dex_file_name)

        already_registered = (
            (old_df["monster_id"] == monster_id)
            & (old_df["進化段階"] == evolution)
        ).any()

        if already_registered:
            return

        new_df = pd.concat([old_df, new_df], ignore_index=True)

    new_df.to_csv(dex_file_name, index=False)

def get_dominant_type(attack, defense, intelligence, chaos):
    stats = {
        "Attacker": attack,
        "Gardian": defense,
        "Sage": intelligence,
        "Chaos": chaos,
    }
    return max(stats, key=stats.get)


def determine_rookie_monster(attack, defense, intelligence, chaos):
    stats = {
        "Attack": attack,
        "Defense": defense,
        "Intelligence": intelligence,
        "Chaos": chaos,
    }

    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_stats[0][0]
    secondary = sorted_stats[1][0]

    if primary == "Attack":
        if secondary == "Defense":
            return "GARGANOS"
        else:
            return "DRAL"

    elif primary == "Defense":
        if secondary == "Intelligence":
            return "GARUSHELL"
        else:
            return "RAGNITE"

    elif primary == "Intelligence":
        if secondary == "Attack":
            return "SEIJAS"
        else:
            return "FAIRIS"

    elif primary == "Chaos":
        if secondary == "Intelligence":
            return "MELORIM"
        else:
            return "REIGAL"

    return None


def calculate_limited_evolution(month_data, save_state=True):
    month_data = month_data.sort_values("日付")

    month_exp = 0
    current_stage_index = 1
    current_type = None
    current_monster_id = None

    current_month = month_data.iloc[0]["月"]
    saved_state = load_evolution_state(current_month)

    if saved_state is not None:
        current_type = saved_state["monster_type"]
        current_monster_id = saved_state["monster_id"]

    total_attack = 0
    total_defense = 0
    total_intelligence = 0
    total_chaos = 0

    for _, row in month_data.iterrows():
        month_exp += int(row["日次EXP"])

        total_attack += int(row["攻撃力"])
        total_defense += int(row["防御力"])
        total_intelligence += int(row["知力"])
        total_chaos += int(row["暴走度"])

        target_stage_index = get_target_stage_index(month_exp)

        if target_stage_index > current_stage_index:
            current_stage_index += 1
            new_stage = stages[current_stage_index]

            if (
                new_stage == "成長期"
                and current_type is None
                and current_monster_id is None
            ):
                current_type = get_dominant_type(
                    total_attack,
                    total_defense,
                    total_intelligence,
                    total_chaos,
                )

                current_monster_id = determine_rookie_monster(
                    total_attack,
                    total_defense,
                    total_intelligence,
                    total_chaos,
                )

                if save_state:
                    save_evolution_state(row["月"], current_type, current_monster_id)

            elif new_stage == "成熟期":
                stats = {
                    "Attack": total_attack,
                    "Defense": total_defense,
                    "Intelligence": total_intelligence,
                    "Chaos": total_chaos,
                }

                if current_monster_id in CHAMPION_BRANCHES:
                    branch_table = CHAMPION_BRANCHES[current_monster_id]
                    available_stats = {
                        stat_name: stats[stat_name]
                        for stat_name in branch_table.keys()
                    }
                    selected_stat = max(available_stats, key=available_stats.get)
                    current_monster_id = branch_table[selected_stat]

            elif new_stage == "完全体":
                if current_monster_id in ULTIMATE_EVOLUTION:
                    current_monster_id = ULTIMATE_EVOLUTION[current_monster_id]

            elif new_stage == "究極体":
                if current_monster_id in MEGA_EVOLUTION:
                    current_monster_id = MEGA_EVOLUTION[current_monster_id]

        elif target_stage_index < current_stage_index:
            current_stage_index -= 1

            if current_stage_index < 3:
                current_type = None
                current_monster_id = None

                if save_state:
                    clear_evolution_state(row["月"])

    total_stats = {
        "攻撃力": total_attack,
        "防御力": total_defense,
        "知力": total_intelligence,
        "暴走度": total_chaos,
    }

    return month_exp, stages[current_stage_index], current_type, current_monster_id, total_stats


def find_monster_image(evolution, monster_type, monster_id):
    if evolution == "闇タマゴ":
        return MONSTER_MASTER["dark_egg"]["image"]
    elif evolution == "タマゴ":
        return MONSTER_MASTER["egg"]["image"]
    elif evolution == "幼体":
        return MONSTER_MASTER["unil"]["image"]

    stage_map = {
        "成長期": "Rookie",
        "成熟期": "Champion",
        "完全体": "Ultimate",
        "究極体": "Mega",
    }

    folder_stage = stage_map.get(evolution)

    if not monster_type or not folder_stage:
        return None

    base_path = f"assets/cards/{monster_type}/{folder_stage}"

    if not os.path.exists(base_path):
        return None

    files = os.listdir(base_path)
    target_files = [f for f in files if monster_id and monster_id in f]

    if len(target_files) > 0:
        return os.path.join(base_path, target_files[0])

    return None


# ------------------------------------------------------------
# 事前に今月のモンスター情報を計算
# ------------------------------------------------------------

history = read_records_from_sheet()

game_state = load_game_state()
today_month = datetime.now(ZoneInfo("Asia/Tokyo")).date().strftime("%Y-%m")

current_month = game_state["active_month"]

if not os.path.exists(game_state_file_name):
    save_game_state(
        active_month=today_month,
        pending_result_month=None,
    )
    game_state = load_game_state()

# ----------------------------
# 月跨ぎ検知
# ----------------------------

active_month = game_state["active_month"]

if active_month != today_month:

    save_game_state(
        active_month=active_month,
        pending_result_month=active_month,
    )

    game_state = load_game_state()

pending_result_month = game_state["pending_result_month"]

if pending_result_month:

    st.warning(
        f"""
月末リザルトが未確認です。

対象月：
{pending_result_month}

月末リザルトを確認後、
「次の月へ進む」を実行してください。
"""
    )

home_locked = pending_result_month is not None

if home_locked:
    st.stop()

if len(history) > 0:
    month_data = history[history["月"] == current_month]
else:
    month_data = pd.DataFrame()

if len(month_data) > 0:
    month_exp, evolution, monster_type, monster_id, total_stats = calculate_limited_evolution(month_data)
else:
    month_exp = 0
    evolution = "タマゴ"
    monster_type = None
    monster_id = None
    total_stats = {"攻撃力": 0, "防御力": 0, "知力": 0, "暴走度": 0}

if pd.isna(monster_type):
    monster_type = None

if pd.isna(monster_id):
    monster_id = None

image_path = find_monster_image(evolution, monster_type, monster_id)
next_target = get_next_target(evolution)


# ------------------------------------------------------------
# 左：モンスター / 右：入力
# ------------------------------------------------------------

if "good_trades" not in st.session_state:
    st.session_state.good_trades = 0
if "bad_trades" not in st.session_state:
    st.session_state.bad_trades = 0

left_col, right_col = st.columns([1.02, 0.98], gap="large")

with left_col:
    # container removed to avoid empty decorative boxes
    st.markdown('<div class="panel-title">✨ 今月のモンスター</div>', unsafe_allow_html=True)

    if image_path and os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.error("モンスター画像が見つかりません")

    if evolution == "タマゴ":
        display_name = "タマゴ"

    elif evolution == "幼体":
        display_name = "ユニル"

    elif monster_id:
        display_name = monster_id

    else:
        display_name = "未誕生"

    display_type = monster_type if monster_type else "未確定"

    if evolution in ["闇タマゴ", "タマゴ", "幼体"]:
        badge_text = evolution
    else:
        display_type = monster_type if monster_type else "未確定"
        badge_text = f"{evolution} / {display_type}"

    st.markdown(
        f'<div class="evolution-badge">{badge_text}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="monster-name">{display_name}</div>', unsafe_allow_html=True)

    st.markdown(f"**月間EXP：** {month_exp}")

    if next_target is not None and next_target > 0:
        progress = max(0, min(month_exp / next_target, 1.0))
        st.progress(progress)
        remaining_exp = max(0, next_target - month_exp)
        st.markdown(f'<div class="exp-note">次の進化まであと {remaining_exp} EXP</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="exp-sub-note">進化目安：{next_target} EXP　｜　1回の記録につき最大1段階</div>', unsafe_allow_html=True)
    elif evolution == "究極体":
        st.success("究極体に到達！今月の最高進化です！")
    else:
        st.warning("EXPがマイナスです。闇タマゴ状態です。")

    st.markdown(
        f"""
        <div class="info-grid">
            <div class="info-card"><div class="info-label">攻撃力</div><div class="info-value">⚔️ {total_stats['攻撃力']}</div></div>
            <div class="info-card"><div class="info-label">防御力</div><div class="info-value">🛡️ {total_stats['防御力']}</div></div>
            <div class="info-card"><div class="info-label">知力</div><div class="info-value">🧠 {total_stats['知力']}</div></div>
            <div class="info-card"><div class="info-label">暴走度</div><div class="info-value">🔥 {total_stats['暴走度']}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    # container removed to avoid empty decorative boxes
    st.markdown('<div class="panel-title">📅 今日の記録</div>', unsafe_allow_html=True)

    record_date = st.date_input("記録する日付", value=datetime.now(ZoneInfo("Asia/Tokyo")).date(), label_visibility="collapsed")

    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    st.markdown('<div class="row-title">損益（％）</div>', unsafe_allow_html=True)
    profit_percent = st.number_input(
        "今日の損益（%）",
        value=0.0,
        step=0.1,
        format="%.1f",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    st.markdown('<div class="row-title">良トレード</div>', unsafe_allow_html=True)
    good_left, good_right = st.columns([1, 1.5], gap="large")

    with good_left:
        st.caption("回数")
        minus_col, value_col, plus_col = st.columns([1, 1, 1])

        with minus_col:
            if st.button("−", key="good_minus", use_container_width=True):
                        st.session_state.good_trades = max(0, st.session_state.good_trades - 1)

        with value_col:
            st.markdown(
                f"<div class='stepper-value'>{st.session_state.good_trades}</div>",
                unsafe_allow_html=True,
            )

        with plus_col:
            if st.button("＋", key="good_plus", use_container_width=True):
                        st.session_state.good_trades += 1

    with good_right:
        st.markdown('<div class="compact-slider-label">良トレードの質</div>', unsafe_allow_html=True)
        good_quality = st.slider("良トレードの質（0〜5）", 0, 5, 0, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    st.markdown('<div class="row-title">無駄トレード</div>', unsafe_allow_html=True)
    bad_left, bad_right = st.columns([1, 1.5], gap="large")

    with bad_left:
        st.caption("回数")
        minus_col, value_col, plus_col = st.columns([1, 1, 1])

        with minus_col:
            if st.button("−", key="bad_minus", use_container_width=True):
                        st.session_state.bad_trades = max(0, st.session_state.bad_trades - 1)

        with value_col:
            st.markdown(
                f"<div class='stepper-value'>{st.session_state.bad_trades}</div>",
                unsafe_allow_html=True,
            )

        with plus_col:
            if st.button("＋", key="bad_plus", use_container_width=True):
                        st.session_state.bad_trades += 1

    with bad_right:
        st.markdown('<div class="compact-slider-label">無駄トレードの重さ</div>', unsafe_allow_html=True)
        bad_weight = st.slider("無駄トレードの重さ（0〜5）", 0, 5, 0, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-row-last">', unsafe_allow_html=True)
    st.markdown('<div class="row-title">振り返り</div>', unsafe_allow_html=True)
    memo = st.text_area("今日の振り返り", height=62, label_visibility="collapsed")
    st.caption(f"文字数：{len(memo)} / 200目安　｜　知力目安：{min(50, len(memo) // 4)}")
    st.markdown('</div>', unsafe_allow_html=True)

    good_trades = st.session_state.good_trades
    bad_trades = st.session_state.bad_trades

    profit_exp = int(profit_percent * 10)
    good_trade_exp = good_trades * 5 + good_quality * 3
    bad_trade_penalty = bad_trades * -5 + bad_weight * -3

    if len(memo) >= 100:
        memo_exp = 10
    elif len(memo) > 0:
        memo_exp = 3
    else:
        memo_exp = 0

    daily_exp = profit_exp + good_trade_exp + bad_trade_penalty + memo_exp

    attack = good_trades * 10 + good_quality * 5
    defense = max(0, 10 + good_quality * 4 + memo_exp - bad_trades * 8 - bad_weight * 3)
    intelligence = min(50, len(memo) // 4)
    chaos = bad_trades * 10 + bad_weight * 5

    st.markdown("#### 今日の結果")

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f"<div class='metric-strip'><div class='metric-label'>攻撃力</div><div class='metric-value'>⚔️ {attack}</div></div>", unsafe_allow_html=True)
    with r2:
        st.markdown(f"<div class='metric-strip'><div class='metric-label'>防御力</div><div class='metric-value'>🛡️ {defense}</div></div>", unsafe_allow_html=True)
    with r3:
        st.markdown(f"<div class='metric-strip'><div class='metric-label'>知力</div><div class='metric-value'>🧠 {intelligence}</div></div>", unsafe_allow_html=True)
    with r4:
        st.markdown(f"<div class='metric-strip'><div class='metric-label'>暴走度</div><div class='metric-value'>🔥 {chaos}</div></div>", unsafe_allow_html=True)

    with st.expander("EXP内訳を見る"):
        e1, e2 = st.columns(2)
        e1.write(f"損益EXP：{profit_exp}")
        e1.write(f"良トレードEXP：{good_trade_exp}")
        e2.write(f"無駄トレードペナルティ：{bad_trade_penalty}")
        e2.write(f"振り返りEXP：{memo_exp}")

    st.markdown(f"**今日の獲得EXP：{daily_exp}**")

    if chaos >= 30:
        st.error("モンスターが暴走している！")
    elif daily_exp >= 30:
        st.success("会心の一日！モンスターが大きく成長した！")
    elif daily_exp > 0:
        st.info("モンスターは順調に育っている")
    else:
        st.warning("今日は苦しい一日。明日立て直そう")

    st.markdown('<div class="save-button-note">入力内容を確認してから保存してください</div>', unsafe_allow_html=True)
    save_button = st.button("🔥 今日の記録を保存", type="primary", use_container_width=True)


# ------------------------------------------------------------
# 保存処理
# ------------------------------------------------------------

if save_button:
    record_month = record_date.strftime("%Y-%m")

    old_history = read_records_from_sheet()

    if len(old_history) > 0:
        old_month_data = old_history[old_history["月"] == record_month]
    else:
        old_month_data = pd.DataFrame()

    if len(old_month_data) > 0:
        before_exp, before_evolution, before_type, before_monster_id, before_stats = calculate_limited_evolution(
            old_month_data,
            save_state=False,
        )
    else:
        before_exp = 0
        before_evolution = "タマゴ"
        before_type = None
        before_monster_id = None

    data = {
        "保存日時": [datetime.now(ZoneInfo("Asia/Tokyo"))],
        "日付": [record_date.strftime("%Y-%m-%d")],
        "月": [record_month],
        "損益%": [profit_percent],
        "良トレード回数": [good_trades],
        "良トレードの質": [good_quality],
        "無駄トレード回数": [bad_trades],
        "無駄トレードの重さ": [bad_weight],
        "メモ": [memo],
        "損益EXP": [profit_exp],
        "良トレードEXP": [good_trade_exp],
        "無駄トレードペナルティ": [bad_trade_penalty],
        "振り返りEXP": [memo_exp],
        "日次EXP": [daily_exp],
        "攻撃力": [attack],
        "防御力": [defense],
        "知力": [intelligence],
        "暴走度": [chaos],

        # 月末リザルト用
        "monster_id": [None],
        "進化段階": [None],
        "monster_type": [None],
    }

    df = pd.DataFrame(data)

    if len(old_history) > 0:
        new_history = pd.concat([old_history, df], ignore_index=True)
    else:
        new_history = df

    new_month_data = new_history[new_history["月"] == record_month]

    after_exp, after_evolution, after_type, after_monster_id, after_stats = calculate_limited_evolution(
        new_month_data,
        save_state=True,
    )
    new_history.loc[new_history.index[-1], "monster_id"] = after_monster_id
    new_history.loc[new_history.index[-1], "進化段階"] = after_evolution
    new_history.loc[new_history.index[-1], "monster_type"] = after_type

    latest_record_dict = new_history.iloc[-1].to_dict()
    append_record_to_sheet(latest_record_dict)

    register_monster_to_dex(
        record_month,
        after_evolution,
        after_type,
        after_monster_id,
    )

    before_stage_index = stages.index(before_evolution)
    after_stage_index = stages.index(after_evolution)

    evolved = (
        after_stage_index > before_stage_index
        or after_monster_id != before_monster_id
    )

    if evolved:
        st.balloons()

        st.success("🌟 進化発生！")

        st.markdown(
            f"""
            <div style="
                margin-top: 12px;
                padding: 18px;
                border-radius: 18px;
                border: 1px solid rgba(251, 191, 36, 0.55);
                background: linear-gradient(135deg, rgba(251,191,36,0.18), rgba(124,58,237,0.18));
                text-align: center;
            ">
                <div style="font-size: 18px; color: #fbbf24; font-weight: 900;">EVOLUTION</div>
                <div style="font-size: 26px; color: #f8fafc; font-weight: 950; margin-top: 8px;">
                    {before_evolution} → {after_evolution}
                </div>
                <div style="font-size: 18px; color: #e2e8f0; font-weight: 800; margin-top: 6px;">
                    {before_monster_id or "タマゴ"} → {after_monster_id or "タマゴ"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("記録を保存しました！")

    st.info("画面を更新すると、左側のモンスター表示も最新状態になります。")

# ------------------------------------------------------------
# 履歴エリア
# ------------------------------------------------------------

st.divider()

history = read_records_from_sheet()

if len(history) > 0:

    hist_left, hist_right = st.columns([1, 1.55], gap="large")

    with hist_left:
        st.header("月次履歴")
        monthly_rows = []

        for month in sorted(history["月"].unique()):
            data = history[history["月"] == month]
            m_exp, m_evolution, m_type, m_monster_id, m_total_stats = calculate_limited_evolution(data, save_state=False)

            monthly_rows.append({
                "月": month,
                "損益%": data["損益%"].sum(),
                "日次EXP合計": data["日次EXP"].sum(),
                "制限後EXP": m_exp,
                "最終進化": m_evolution,
                "良トレード回数": data["良トレード回数"].sum(),
                "無駄トレード回数": data["無駄トレード回数"].sum(),
                "振り返りEXP": data["振り返りEXP"].sum(),
            })

        monthly_summary = pd.DataFrame(monthly_rows)
        st.dataframe(monthly_summary, use_container_width=True)

    with hist_right:
        st.header("日次記録")
        st.dataframe(history, use_container_width=True)

        st.header("記録の修正")
        if len(history) > 0:
            latest_record = history.iloc[-1]
            st.write(f"最後に保存した記録：{latest_record['日付']} / 損益%：{latest_record['損益%']} / 日次EXP：{latest_record['日次EXP']}")

            st.caption("※Google Sheets保存化に伴い、削除機能は一時停止中です。")
else:
    st.info("まだ記録がありません。今日の記録を保存すると、モンスター育成が始まります。")
