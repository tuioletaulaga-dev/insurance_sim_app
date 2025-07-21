import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(page_title="Monte Carlo Insurance Profitability Simulator", layout="wide")

# Sidebar Controls
st.sidebar.header("Simulation Controls")

num_policies = st.sidebar.slider("Number of Policies", 100, 10000, 5000, step=100)
num_trials = st.sidebar.slider("Number of Trials", 100, 10000, 1000, step=100)
discount_rate = st.sidebar.slider("Discount Rate (Claims)", 0.00, 0.10, 0.06, step=0.01)
investment_rate = st.sidebar.slider("Investment Rate (Premiums)", 0.00, 0.10, 0.08, step=0.01)
mortality_multiplier = st.sidebar.slider("Mortality Multiplier", 0.5, 2.0, 1.0, step=0.1)
lapse_multiplier = st.sidebar.slider("Lapse Multiplier", 0.5, 2.0, 1.0, step=0.1)
death_benefit = st.sidebar.slider("Death Benefit", 100_000, 2_000_000, 1_000_000, step=50_000)
annual_premium = st.sidebar.slider("Annual Policy Premium", 0, 1000, 500, step=1)

run_button = st.sidebar.button("Run Simulation")

# Constants
start_age = 40
policy_term = 25

lapse_rates = [
    10.0, 8.0, 7.0, 6.0, 6.0,
    5.0, 5.0, 5.0, 5.0, 5.0,
    4.0, 4.0, 4.0, 4.0, 4.0,
    3.5, 3.5, 3.5, 3.5, 3.5,
    3.0, 3.0, 3.0, 3.0, 25.0,
    70.0, 30.0, 20.0, 20.0, 15.0
]

mortality_qx = [
    0.00147, 0.00160, 0.00174, 0.00188, 0.00204, 0.00221, 0.00239, 0.00259, 0.00280,
    0.00303, 0.00328, 0.00355, 0.00384, 0.00415, 0.00449, 0.00486, 0.00526, 0.00569,
    0.00616, 0.00667, 0.00722, 0.00782, 0.00847, 0.00918, 0.00994, 0.01077
]

def run_sim(...):
    qx_dict = dict(zip(range(40, 66), [q * mortality_multiplier for q in mortality_qx]))
    lapse_dict = dict(zip(range(1, 31), [l / 100 * lapse_multiplier for l in lapse_rates]))
    
    claim_discount_factors = [1 / (1 + discount_rate) ** (i + 1) for i in range(policy_term)]
    premium_discount_factors = [1 / (1 + investment_rate) ** (i + 1) for i in range(policy_term)]

    results = {
        "Claim PV": [], "Premium PV": [], "Profit PV": [],
        "Deaths": [], "Lapses": [],
        "PV per Policy": [], "Premium per Policy": [], "Profit per Policy": []
    }

    for _ in range(num_trials):
        total_claim_pv = 0
        total_premium_pv = 0
        deaths = 0
        lapses = 0

        for _ in range(num_policies):
            policy_claim_pv = 0
            policy_premium_pv = 0

            for year in range(policy_term):
                age = start_age + year
                year_idx = year + 1
                lapse = lapse_dict.get(year_idx, 0)
                qx = qx_dict.get(age, 0)

                if np.random.random() <= lapse:
                    lapses += 1
                    break

                # Premium paid if policy in-force
                policy_premium_pv += annual_premium * premium_discount_factors[year]

                if np.random.random() <= qx:
                    deaths += 1
                    policy_claim_pv += death_benefit * claim_discount_factors[year]
                    break

            total_claim_pv += policy_claim_pv
            total_premium_pv += policy_premium_pv

        profit_pv = total_premium_pv - total_claim_pv

        results["Claim PV"].append(total_claim_pv)
        results["Premium PV"].append(total_premium_pv)
        results["Profit PV"].append(profit_pv)
        results["Deaths"].append(deaths)
        results["Lapses"].append(lapses)
        results["PV per Policy"].append(total_claim_pv / num_policies)
        results["Premium per Policy"].append(total_premium_pv / num_policies)
        results["Profit per Policy"].append(profit_pv / num_policies)

    return results

# Run
if run_button:
    st.subheader("Running Monte Carlo Simulation...")
    results = run_sim(
        num_policies=num_policies,
        num_trials=num_trials,
        discount_rate=discount_rate,
        investment_rate=investment_rate,
        mortality_multiplier=mortality_multiplier,
        lapse_multiplier=lapse_multiplier,
        death_benefit=death_benefit,
        annual_premium=annual_premium
    )

    # Extract arrays
    claim_pv = np.array(results["Claim PV"])
    premium_pv = np.array(results["Premium PV"])
    profit_pv = np.array(results["Profit PV"])
    deaths = np.array(results["Deaths"])
    lapses = np.array(results["Lapses"])
    pv_per_policy = np.array(results["PV per Policy"])
    premium_per_policy = np.array(results["Premium per Policy"])
    profit_per_policy = np.array(results["Profit per Policy"])

    # Row 1 – Means
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg PV of Premiums", f"${premium_pv.mean():,.0f}")
    c2.metric("Avg Premium per Policy", f"${premium_per_policy.mean():,.2f}")
    c3.metric("Avg Profit (PV)", f"${profit_pv.mean():,.0f}")
    c4.metric("Avg Profit per Policy", f"${profit_per_policy.mean():,.2f}")

    # Row 2 – Standard Deviations
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Std Dev of Premium PV", f"${premium_pv.std():,.0f}")
    c6.metric("Std Dev Premium/Policy", f"${premium_per_policy.std():,.2f}")
    c7.metric("Std Dev Profit (PV)", f"${profit_pv.std():,.0f}")
    c8.metric("Std Dev Profit/Policy", f"${profit_per_policy.std():,.2f}")

    # Row 3 – Previous Core Metrics
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Claim PV", f"${claim_pv.mean():,.0f}")
    m2.metric("Avg Deaths per Trial", f"{deaths.mean():.1f}")
    m3.metric("Avg Lapses per Trial", f"{lapses.mean():.1f}")
    m4.metric("Avg Claim PV per Policy", f"${pv_per_policy.mean():,.2f}")

    # Row 4 – Std Devs for above
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Std Dev Claim PV", f"${claim_pv.std():,.0f}")
    s2.metric("Std Dev Deaths", f"{deaths.std():.1f}")
    s3.metric("Std Dev Lapses", f"{lapses.std():.1f}")
    s4.metric("Std Dev Claim PV/Policy", f"${pv_per_policy.std():,.2f}")

    # Visualizations
    st.subheader("Distribution Plots")
    sns.set(style="whitegrid")

    def plot_dist(data, title, color="blue"):
        fig, ax = plt.subplots()
        sns.histplot(data, bins=30, kde=True, ax=ax, color=color)
        ax.set_title(title)
        return fig

    st.pyplot(plot_dist(profit_per_policy, "Profit per Policy", "green"))
    st.pyplot(plot_dist(premium_per_policy, "Premium per Policy", "orange"))
    st.pyplot(plot_dist(pv_per_policy, "Claim PV per Policy", "purple"))
    st.pyplot(plot_dist(deaths, "Deaths per Trial"))
    st.pyplot(plot_dist(lapses, "Lapses per Trial", "red"))
