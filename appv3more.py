# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 16:17:15 2026

@author: samama
"""

import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Financial Shock Survival Game")

# -----------------------------
# CONSTANTS
# -----------------------------
STARTING_CAPITAL = 10000

ASSETS = [
    "Stocks",
    "Currency Market",
    "Fixed Income",
    "Private Assets",
    "Crypto",
]

ASSET_DEFINITIONS = {
    "Stocks": "Ownership shares in companies. They can offer higher returns but are more volatile.",
    "Currency Market": "Investments linked to foreign exchange markets. Exchange rates move because of interest rates, inflation and global uncertainty.",
    "Fixed Income": "Debt instruments such as government or corporate bonds that usually provide more stable returns than stocks.",
    "Private Assets": "Investments not traded on public markets such as private equity or real estate. They are less liquid but help diversification.",
    "Crypto": "Digital assets based on blockchain technology. They are highly volatile and strongly influenced by market sentiment and regulation.",
}

ROUNDS = [
    {
        "name": "Inflation Shock",
        "description": "Inflation rises sharply. Purchasing power falls and companies face higher costs.",
        "impacts": {
            "Stocks": -0.07,
            "Currency Market": -0.02,
            "Fixed Income": -0.09,
            "Private Assets": -0.04,
            "Crypto": -0.06,
        },
        "insight": "Inflation hurts assets with fixed future payments because those payments lose real value.",
    },
    {
        "name": "Geopolitical Crisis",
        "description": "A major geopolitical conflict creates uncertainty in global markets.",
        "impacts": {
            "Stocks": -0.06,
            "Currency Market": 0.03,
            "Fixed Income": 0.02,
            "Private Assets": -0.05,
            "Crypto": -0.08,
        },
        "insight": "During geopolitical crises investors usually reduce risk and move toward safer assets.",
    },
    {
        "name": "Global Banking Crisis",
        "description": "Several banks report large losses creating fear of financial instability.",
        "impacts": {
            "Stocks": -0.10,
            "Currency Market": 0.02,
            "Fixed Income": 0.06,
            "Private Assets": -0.07,
            "Crypto": -0.12,
        },
        "insight": "When banks struggle, investors worry about credit availability and economic slowdown.",
    },
    {
        "name": "Interest Rate Hike",
        "description": "Central banks sharply increase interest rates to fight inflation.",
        "impacts": {
            "Stocks": -0.05,
            "Currency Market": 0.02,
            "Fixed Income": -0.07,
            "Private Assets": -0.04,
            "Crypto": -0.09,
        },
        "insight": "Higher interest rates reduce liquidity and make risky assets less attractive.",
    },
    {
        "name": "Tech Bubble Burst",
        "description": "Technology stocks collapse after a period of excessive speculation.",
        "impacts": {
            "Stocks": -0.12,
            "Currency Market": 0.00,
            "Fixed Income": 0.03,
            "Private Assets": -0.05,
            "Crypto": -0.15,
        },
        "insight": "Speculative bubbles often hit growth assets and cryptocurrencies hardest.",
    },
    {
        "name": "Commodity Boom",
        "description": "Energy and commodity prices surge due to global supply shortages.",
        "impacts": {
            "Stocks": 0.04,
            "Currency Market": 0.01,
            "Fixed Income": -0.03,
            "Private Assets": 0.08,
            "Crypto": 0.02,
        },
        "insight": "Commodity booms can benefit real assets and companies linked to natural resources.",
    },
]

ASSET_COLORS = {
    "Stocks": "#8FB7D8",
    "Currency Market": "#E7A6C6",
    "Fixed Income": "#F2D27A",
    "Private Assets": "#C6B4E3",
    "Crypto": "#A8D8D1",
}

POSITIVE_COLOR = "#2E9B5F"
NEGATIVE_COLOR = "#D95C5C"
NEUTRAL_COLOR = "#8E8E8E"

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background-color: #faf8f6;
        border: 1px solid #eee7e1;
        padding: 12px 16px;
        border-radius: 14px;
    }

    div[data-testid="stInfo"] {
        border-radius: 14px;
    }

    div[data-testid="stSuccess"] {
        border-radius: 14px;
    }

    div[data-testid="stError"] {
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# SESSION STATE
# -----------------------------
def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = "setup"
    if "round_index" not in st.session_state:
        st.session_state.round_index = 0
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {a: 0 for a in ASSETS}
    if "events" not in st.session_state:
        st.session_state.events = []
    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.phase in ["shock", "rebalance", "final"] and len(st.session_state.events) == 0:
        st.session_state.phase = "setup"
        st.session_state.round_index = 0
        st.session_state.portfolio = {a: 0 for a in ASSETS}
        st.session_state.history = []

    if len(st.session_state.events) > 0 and st.session_state.round_index >= len(st.session_state.events):
        st.session_state.phase = "final"


init_state()

# -----------------------------
# HELPERS
# -----------------------------
def reset_game():
    st.session_state.phase = "setup"
    st.session_state.round_index = 0
    st.session_state.portfolio = {a: 0 for a in ASSETS}
    st.session_state.history = []
    st.session_state.events = []
    for a in ASSETS:
        st.session_state[f"alloc_{a}"] = 0.0
        st.session_state[f"rebal_{a}"] = 0.0


def save_history(step_label):
    snapshot = {"Step": step_label}
    for a in ASSETS:
        snapshot[a] = round(st.session_state.portfolio[a], 2)
    st.session_state.history.append(snapshot)


def format_euro(x):
    return f"€{x:,.2f}"


def build_shock_dataframe(before_portfolio, event):
    rows = []
    for a in ASSETS:
        impact = event["impacts"][a]
        after = before_portfolio[a] * (1 + impact)

        rows.append(
            {
                "Asset": a,
                "Before": round(before_portfolio[a], 2),
                "Impact": f"{impact * 100:+.0f}%",
                "After": round(after, 2),
                "Before_num": before_portfolio[a],
                "After_num": after,
            }
        )

    return pd.DataFrame(rows)


def style_shock_table(df):
    display_df = df[["Asset", "Before", "Impact", "After"]].copy()

    def impact_style_column(col):
        styles = []
        for val in col:
            if isinstance(val, str) and val.startswith("+"):
                styles.append(f"color: {POSITIVE_COLOR}; font-weight: 700;")
            elif isinstance(val, str) and val.startswith("-"):
                styles.append(f"color: {NEGATIVE_COLOR}; font-weight: 700;")
            else:
                styles.append(f"color: {NEUTRAL_COLOR}; font-weight: 700;")
        return styles

    def after_style_column(col):
        styles = []
        for i in df.index:
            if df.loc[i, "After_num"] > df.loc[i, "Before_num"]:
                styles.append(f"color: {POSITIVE_COLOR}; font-weight: 700;")
            elif df.loc[i, "After_num"] < df.loc[i, "Before_num"]:
                styles.append(f"color: {NEGATIVE_COLOR}; font-weight: 700;")
            else:
                styles.append(f"color: {NEUTRAL_COLOR}; font-weight: 700;")
        return styles

    styled = (
        display_df.style
        .apply(impact_style_column, subset=["Impact"], axis=0)
        .apply(after_style_column, subset=["After"], axis=0)
        .format({
            "Before": "€{:,.2f}",
            "After": "€{:,.2f}",
        })
    )

    return styled


def plot_allocation_donut(portfolio_dict):
    labels = []
    values = []
    colors = []

    for asset in ASSETS:
        value = portfolio_dict[asset]
        if value > 0:
            labels.append(asset)
            values.append(value)
            colors.append(ASSET_COLORS[asset])

    if not values:
        return

    fig, ax = plt.subplots(figsize=(4.5, 3.2))

    ax.pie(
        values,
        labels=labels,
        colors=colors,
        startangle=180,
        counterclock=False,
        autopct="%1.1f%%",
        pctdistance=0.9,
        labeldistance=1,
        wedgeprops={"width": 0.5, "edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 10, "color": "#3a3a3a"},
    )

    ax.axis("equal")
    plt.tight_layout()
    st.pyplot(fig, clear_figure=True)


def plot_portfolio_history():
    if len(st.session_state.history) < 2:
        return

    df_hist = pd.DataFrame(st.session_state.history)
    df_hist["Total Portfolio"] = df_hist[ASSETS].sum(axis=1)

    fig, ax = plt.subplots(figsize=(9, 4.8))

    for asset in ASSETS:
        ax.plot(
            df_hist["Step"],
            df_hist[asset],
            marker="o",
            markersize=5,
            linewidth=2.2,
            label=asset,
            color=ASSET_COLORS[asset],
        )

    ax.plot(
        df_hist["Step"],
        df_hist["Total Portfolio"],
        marker="o",
        markersize=5,
        linewidth=2.8,
        label="Total Portfolio",
        color="black",
    )

    ax.set_xlabel("Time", fontsize=10)
    ax.set_ylabel("Value (€)", fontsize=10)
    ax.set_title("Portfolio Value Over Time", fontsize=14, pad=12)
    ax.grid(True, alpha=0.20, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, fontsize=9, ncol=2)
    plt.xticks(rotation=18, ha="right")
    plt.tight_layout()

    st.pyplot(fig, clear_figure=True)


def get_stage_guidance(event, phase):
    positives = [a for a in ASSETS if event["impacts"][a] > 0]
    negatives = [a for a in ASSETS if event["impacts"][a] < 0]
    neutral = [a for a in ASSETS if event["impacts"][a] == 0]

    pos_text = ", ".join(positives) if positives else "no asset classes"
    neg_text = ", ".join(negatives) if negatives else "no asset classes"
    neu_text = ", ".join(neutral) if neutral else None

    if phase == "shock":
        text = f"""
**What just happened:**  
This market event affected all asset classes. The main pressure was on **{neg_text}**, while **{pos_text}** held up better or increased.

**What you should look at now:**  
Check the before/after table and identify where the losses and gains are. This helps you understand how the shock changed your portfolio.
"""
        if neu_text:
            text += f"\n\n**Stable assets:** {neu_text} stayed broadly unchanged."
        return text

    if phase == "rebalance":
        text = f"""
**What happened in the market:**  
After this shock, **{neg_text}** weakened, while **{pos_text}** performed better.

**What you should do now:**  
Rebalance your portfolio so that your new allocation reflects your strategy. You can reduce exposure to weaker assets, keep diversification, or increase the weight of the assets that resisted the shock better.
"""
        if neu_text:
            text += f"\n\n**More stable assets:** {neu_text} remained mostly flat."
        return text

    return ""


# -----------------------------
# TITLE
# -----------------------------
st.title("Financial Shock Survival Game")

# -----------------------------
# SETUP
# -----------------------------
if st.session_state.phase == "setup":
    st.write("You start with **€10,000**. Allocate your capital across the asset classes.")

    with st.expander("Asset Class Definitions"):
        for a in ASSETS:
            st.write(f"**{a}** — {ASSET_DEFINITIONS[a]}")

    cols = st.columns(len(ASSETS))
    for i, asset in enumerate(ASSETS):
        with cols[i]:
            st.number_input(
                f"{asset} (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.get(f"alloc_{asset}", 0.0),
                step=1.0,
                key=f"alloc_{asset}",
            )

    total = sum(st.session_state[f"alloc_{a}"] for a in ASSETS)
    remaining = 100 - total

    st.progress(min(max(total / 100, 0), 1.0))

    if remaining > 0:
        st.info(f"Remaining allocation: {remaining:.1f}%")
    elif remaining < 0:
        st.error(f"Exceeded allocation by {abs(remaining):.1f}%")
    else:
        st.success("Allocation complete")

    if st.button("Start Game", use_container_width=True):
        if total != 100:
            st.error("Allocation must equal 100%")
        else:
            for a in ASSETS:
                pct = st.session_state[f"alloc_{a}"] / 100
                st.session_state.portfolio[a] = STARTING_CAPITAL * pct

            st.session_state.history = []
            save_history("Initial Allocation")
            st.session_state.events = random.sample(ROUNDS, 3)
            st.session_state.round_index = 0
            st.session_state.phase = "shock"
            st.rerun()

# -----------------------------
# SHOCK
# -----------------------------
elif st.session_state.phase == "shock":
    event = st.session_state.events[st.session_state.round_index]
    before = st.session_state.portfolio.copy()
    df_shock = build_shock_dataframe(before, event)

    simulated_portfolio = {
        a: before[a] * (1 + event["impacts"][a])
        for a in ASSETS
    }

    st.header(event["name"])
    st.write(event["description"])
    st.info(get_stage_guidance(event, "shock"))

    progress_value = (st.session_state.round_index + 1) / len(st.session_state.events)
    st.progress(progress_value)

    table_col, pie_col = st.columns([2, 2], gap="large")

    with table_col:
        st.subheader("Before / after shock")
        st.dataframe(
            style_shock_table(df_shock),
            use_container_width=True,
            hide_index=True,
        )

    with pie_col:
        st.subheader("After shock")
        plot_allocation_donut(simulated_portfolio)

    st.info(event["insight"])

    st.subheader("Portfolio history")
    plot_portfolio_history()

    if st.button("Apply Shock", use_container_width=True):
        for a in ASSETS:
            st.session_state.portfolio[a] *= (1 + event["impacts"][a])

        save_history(event["name"])
        st.session_state.phase = "rebalance"
        st.rerun()

# -----------------------------
# REBALANCE
# -----------------------------
elif st.session_state.phase == "rebalance":
    total = sum(st.session_state.portfolio.values())
    event = st.session_state.events[st.session_state.round_index]

    st.subheader("Rebalance Portfolio")
    st.write(f"Current value: **{format_euro(total)}**")
    st.info(get_stage_guidance(event, "rebalance"))

    progress_value = (st.session_state.round_index + 1) / len(st.session_state.events)
    st.progress(progress_value)

    cols = st.columns(len(ASSETS))
    for i, asset in enumerate(ASSETS):
        with cols[i]:
            current_weight = (st.session_state.portfolio[asset] / total) * 100 if total > 0 else 0
            st.number_input(
                asset,
                min_value=0.0,
                max_value=100.0,
                value=float(round(current_weight, 1)),
                step=1.0,
                key=f"rebal_{asset}",
            )

    total_alloc = sum(st.session_state[f"rebal_{a}"] for a in ASSETS)
    remaining = 100 - total_alloc

    if remaining > 0:
        st.info(f"Remaining allocation: {remaining:.1f}%")
    elif remaining < 0:
        st.error(f"Exceeded allocation by {abs(remaining):.1f}%")
    else:
        st.success("Allocation complete")

    label = "Finish Game" if st.session_state.round_index == 2 else "Confirm Rebalance"

    if st.button(label, use_container_width=True):
        if total_alloc != 100:
            st.error("Allocation must equal 100%")
        else:
            for a in ASSETS:
                pct = st.session_state[f"rebal_{a}"] / 100
                st.session_state.portfolio[a] = total * pct

            save_history(f"Rebalance {st.session_state.round_index + 1}")

            if st.session_state.round_index == 2:
                st.session_state.phase = "final"
            else:
                st.session_state.round_index += 1
                st.session_state.phase = "shock"

            st.rerun()

# -----------------------------
# FINAL
# -----------------------------
elif st.session_state.phase == "final":
    final_value = sum(st.session_state.portfolio.values())
    total_return = (final_value / STARTING_CAPITAL - 1) * 100

    st.header("Final Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Initial Capital", f"€{STARTING_CAPITAL:,.0f}")
    c2.metric("Final Value", f"€{final_value:,.2f}")
    c3.metric("Return", f"{total_return:+.2f}%")

    df_final = pd.DataFrame(
        {
            "Asset": ASSETS,
            "Value": [round(st.session_state.portfolio[a], 2) for a in ASSETS],
        }
    )

    st.dataframe(
        df_final.style.format({"Value": "€{:,.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Portfolio history")
    plot_portfolio_history()

    if st.button("Play Again", use_container_width=True):
        reset_game()
        st.rerun()
