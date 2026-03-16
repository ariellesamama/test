import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

STARTING_CAPITAL = 10000

ASSETS = [
    "Stocks",
    "Currency Market",
    "Fixed Income / Credit",
    "Private Assets",
    "Crypto",
]

ASSET_DEFINITIONS = {
    "Stocks": "Ownership shares in companies. They can offer higher returns but are more volatile.",
    "Currency Market": "Investments linked to foreign exchange markets. Exchange rates move because of interest rates, inflation and global uncertainty.",
    "Fixed Income / Credit": "Debt instruments such as government or corporate bonds that usually provide more stable returns than stocks.",
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
            "Fixed Income / Credit": -0.09,
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
            "Fixed Income / Credit": 0.02,
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
            "Fixed Income / Credit": 0.06,
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
            "Fixed Income / Credit": -0.07,
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
            "Fixed Income / Credit": 0.03,
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
            "Fixed Income / Credit": -0.03,
            "Private Assets": 0.08,
            "Crypto": 0.02,
        },
        "insight": "Commodity booms can benefit real assets and companies linked to natural resources.",
    },
]

## FCTS

#creating the session state's variables
def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = "setup"
    if "round_index" not in st.session_state:
        st.session_state.round_index = 0
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {a: 0 for a in ASSETS}
    if "events" not in st.session_state:
        st.session_state.events = []

    # Safety check: if the app reloads while no events are stored,
    # send the user back to setup instead of crashing.
    if st.session_state.phase in ["shock", "rebalance", "final"] and len(st.session_state.events) == 0:
        st.session_state.phase = "setup"
        st.session_state.round_index = 0
        st.session_state.portfolio = {a: 0 for a in ASSETS}
        st.session_state.history = []

    # Safety check: if round_index goes out of range, go to final screen.
    if len(st.session_state.events) > 0 and st.session_state.round_index >= len(st.session_state.events):
        st.session_state.phase = "final"

init_state()

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

def plot_portfolio_history():
    if len(st.session_state.history) < 2:
        return

    df_hist = pd.DataFrame(st.session_state.history)

    colors = {
        "Stocks": "blue",
        "Currency Market": "green",
        "Fixed Income / Credit": "orange",
        "Private Assets": "purple",
        "Crypto": "red",
    }

    fig, ax = plt.subplots(figsize=(10, 5))

    for asset in ASSETS:
        ax.plot(
            df_hist["Step"],
            df_hist[asset],
            marker="o",
            label=asset,
            color=colors[asset]
        )

    ax.set_xlabel("Time")
    ax.set_ylabel("Value (€)")
    ax.set_title("Portfolio Value by Asset Over Time")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=20)
    plt.tight_layout()

    st.pyplot(fig)

def plot_allocation_pie():
    labels = []
    values = []

    for a in ASSETS:
        val = st.session_state.portfolio[a]
        if val > 0:
            labels.append(a)
            values.append(val)

    fig, ax = plt.subplots()

    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Portfolio Allocation")

    st.pyplot(fig)

st.title("Financial Shock Survival Game")

## SETUP INIT

if st.session_state.phase == "setup":

    st.write("You start with **€10,000**. Allocate your capital across the asset classes.")

    with st.expander("Asset Class Definitions"):
        for a in ASSETS:
            st.write(f"**{a}** — {ASSET_DEFINITIONS[a]}")

    cols = st.columns(len(ASSETS))

    for i, asset in enumerate(ASSETS):
        with cols[i]:
            st.number_input(f"{asset} (%)", 0.0, 100.0, key=f"alloc_{asset}")

    total = sum(st.session_state[f"alloc_{a}"] for a in ASSETS)

    remaining = 100 - total

    if remaining > 0:
        st.info(f"Remaining allocation: {remaining:.1f}%")
    elif remaining < 0:
        st.error(f"Exceeded allocation by {abs(remaining):.1f}%")
    else:
        st.success("Allocation complete")

    if st.button("Start Game"):

        if total != 100:
            st.error("Allocation must equal 100%")
        else:

            for a in ASSETS:
                pct = st.session_state[f"alloc_{a}"] / 100
                st.session_state.portfolio[a] = STARTING_CAPITAL * pct
            
            st.session_state.history = []
            save_history("Initial Allocation")

            # RANDOMLY PICK 3 EVENTS
            st.session_state.events = random.sample(ROUNDS, 3)

            st.session_state.round_index = 0
            st.session_state.phase = "shock"
            st.rerun()


## SHOCK

elif st.session_state.phase == "shock":

    event = st.session_state.events[st.session_state.round_index]

    st.header(event["name"])
    st.write(event["description"])
    
    st.subheader("Portfolio distribution after shock")
    plot_allocation_pie()

    before = st.session_state.portfolio.copy()

    rows = []

    for a in ASSETS:
        impact = event["impacts"][a]
        after = before[a] * (1 + impact)

        rows.append(
            {
                "Asset": a,
                "Before": round(before[a], 2),
                "Impact": f"{impact*100:+.0f}%",
                "After": round(after, 2),
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(df)

    st.info(event["insight"])
    
    plot_portfolio_history()

    if st.button("Apply Shock"):

        for a in ASSETS:
            st.session_state.portfolio[a] *= (1 + event["impacts"][a])
        
        save_history(event["name"])
        
        st.session_state.phase = "rebalance"
        st.rerun()


## REBAL

elif st.session_state.phase == "rebalance":

    total = sum(st.session_state.portfolio.values())

    st.subheader("Rebalance Portfolio")
    st.write(f"Current value: €{total:,.2f}")
    
    st.subheader("Your New Allocation")
    plot_allocation_pie()

    cols = st.columns(len(ASSETS))

    for i, asset in enumerate(ASSETS):
        with cols[i]:
            weight = (st.session_state.portfolio[asset] / total) * 100
            st.number_input(asset, 0.0, 100.0, value=round(weight, 1), key=f"rebal_{asset}")

    total_alloc = sum(st.session_state[f"rebal_{a}"] for a in ASSETS)

    remaining = 100 - total_alloc

    if remaining > 0:
        st.info(f"Remaining allocation: {remaining:.1f}%")
    elif remaining < 0:
        st.error(f"Exceeded allocation by {abs(remaining):.1f}%")
    else:
        st.success("Allocation complete")

    label = "Finish Game" if st.session_state.round_index == 2 else "Confirm Rebalance"

    if st.button(label):

        if total_alloc != 100:
            st.error("Allocation must equal 100%")

        else:

            for a in ASSETS:
                pct = st.session_state[f"rebal_{a}"] / 100
                st.session_state.portfolio[a] = total * pct

            if st.session_state.round_index == 2:
                st.session_state.phase = "final"
            else:
                st.session_state.round_index += 1
                st.session_state.phase = "shock"

            st.rerun()


## RESULTS & PLOT

elif st.session_state.phase == "final":

    final_value = sum(st.session_state.portfolio.values())
    total_return = (final_value / STARTING_CAPITAL - 1) * 100

    st.header("Final Results")

    c1, c2, c3 = st.columns(3)

    c1.metric("Initial Capital", f"€{STARTING_CAPITAL:,.0f}")
    c2.metric("Final Value", f"€{final_value:,.2f}")
    c3.metric("Return", f"{total_return:+.2f}%")

    df = pd.DataFrame(
        {
            "Asset": ASSETS,
            "Value": [round(st.session_state.portfolio[a], 2) for a in ASSETS],
        }
    )

    st.dataframe(df)
    plot_portfolio_history()

    if st.button("Play Again"):
        reset_game()
        st.rerun()
