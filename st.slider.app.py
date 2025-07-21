import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Streamlit Page Config
st.set_page_config(page_title="Monte Carlo Insurance Simulator", layout="wide")

# Sidebar - User Controls
st.sidebar.header("Simulation Controls")

num_policies = st.sidebar.slider("Number of Policies", min_value=100, max_value=10000, step=100, value=5000)
num_trials = st.sidebar.slider("Number of Trials", min_value=100, max_value=10000, step=100, value=1000)
discount_rate = st.sidebar.slider("Discount Rate", min_value=0.00, max_value=0.10, step=0.01, value=0.06)
mortality_multiplier = st.sidebar.slider("Mortality Multiplier", min_value=0.5, max_value=2.0, step=0.1, value=1.0)
lapse_multiplier = st.sidebar.slider("Lapse Multiplier", min_value=0.5, max_value=2.0, step=0.1, value=1.0)

run_button = st.sidebar.button("Run Simulation")

# Core Inputs
start_age = 40
policy_term = 25
death_benefit = 1_000_000

# Define lapse and mortality tables
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


# Run Simulation Function
def run_sim(num_policies, num_trials, discount_rate, mortality_multiplier, lapse_multiplier):
    qx_dict = dict(zip(range(40, 66), [q * mortality_multiplier for q in mortality_qx]))
    lapse_dict = dict(zip(range(1, 31), [l / 100 * lapse_multiplier for l in lapse_rates]))

    discount_factors = [1 / (1 + discount_rate) ** (i + 1) for i in range(policy_term)]

    results = {
        "Present Value": [],
        "Deaths": [],
        "Lapses": [],
        "PV per Policy": []
    }

    for _ in range(num_trials):
        trial_pv = 0
        trial_deaths = 0
        trial_lapses = 0

        for _ in range(num_policies):
            for year in range(policy_term):
                age = start_age + year
                year_index = year + 1

                lapse_prob = lapse_dict.get(year_index, 0.0)
                mortality_prob = qx_dict.get(age, 0.0)

                if np.random.random() <= lapse_prob:
                    trial_lapses += 1
                    break

                if np.random.random() <= mortality_prob:
                    trial_pv += death_benefit * discount_factors[year]
                    trial_deaths += 1
                    break

        results["Present Value"].append(trial_pv)
        results["Deaths"].append(trial_deaths)
        results["Lapses"].append(trial_lapses)
        results["PV per Policy"].append(trial_pv / num_policies)

    return results


# When button clicked, run simulation
if run_button:
    st.subheader("Running Monte Carlo Simulation...")
    results = run_sim(num_policies, num_trials, discount_rate, mortality_multiplier, lapse_multiplier)

    # Summary Stats
    pv = np.array(results["Present Value"])
    deaths = np.array(results["Deaths"])
    lapses = np.array(results["Lapses"])
    pv_per_policy = np.array(results["PV per Policy"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Present Value", f"${pv.mean():,.0f}")
    col2.metric("Avg Deaths per Trial", f"{deaths.mean():.1f}")
    col3.metric("Avg Lapses per Trial", f"{lapses.mean():.1f}")

    # Plots
    sns.set(style="whitegrid")

    st.subheader("Distribution of Simulation Results")

    fig1, ax1 = plt.subplots()
    sns.histplot(deaths, bins=30, kde=True, ax=ax1)
    ax1.set_title("Number of Deaths per Trial")
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    sns.histplot(lapses, bins=30, kde=True, color="orange", ax=ax2)
    ax2.set_title("Number of Lapses per Trial")
    st.pyplot(fig2)

    fig3, ax3 = plt.subplots()
    sns.histplot(pv, bins=30, kde=True, color="green", ax=ax3)
    ax3.set_title("Total Present Value of Claims per Trial")
    st.pyplot(fig3)

    fig4, ax4 = plt.subplots()
    sns.histplot(pv_per_policy, bins=30, kde=True, color="purple", ax=ax4)
    ax4.set_title("Present Value per Policy")
    st.pyplot(fig4)
