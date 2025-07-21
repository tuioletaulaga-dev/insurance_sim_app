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
death_benefit = st.sidebar.slider("Death Benefit (Face Value)", min_value=100000, max_value=2000000, step=50000, value=1000000)

run_button = st.sidebar.button("Run Simulation")

# Core Constants
start_age = 40
policy_term = 25

# Base Lapse Rates
lapse_rates = [
    10.0, 8.0, 7.0, 6.0, 6.0,
    5.0, 5.0, 5.0, 5.0, 5.0,
    4.0, 4.0, 4.0, 4.0, 4.0,
    3.5, 3.5, 3.5, 3.5, 3.5,
    3.0, 3.0, 3.0, 3.0, 25.0    
]

# Base Mortality Rates (qx)
mortality_qx = [
    0.00147, 0.00160, 0.00174, 0.00188, 0.00204, 0.00221, 0.00239, 0.00259, 0.00280,
    0.00303, 0.00328, 0.00355, 0.00384, 0.00415, 0.00449, 0.00486, 0.00526, 0.00569,
    0.00616, 0.00667, 0.00722, 0.00782, 0.00847, 0.00918, 0.00994, 0.01077
]

# Simulation Function
def run_sim(num_policies, num_trials, discount_rate, mortality_multiplier, lapse_multiplier, death_benefit):
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

# Run when button clicked
if run_button:
    st.subheader("Running Monte Carlo Simulation...")
    results = run_sim(
        num_policies=num_policies,
        num_trials=num_trials,
        discount_rate=discount_rate,
        mortality_multiplier=mortality_multiplier,
        lapse_multiplier=lapse_multiplier,
        death_benefit=death_benefit
    )

    # Extract data
    pv = np.array(results["Present Value"])
    deaths = np.array(results["Deaths"])
    lapses = np.array(results["Lapses"])
    pv_per_policy = np.array(results["PV per Policy"])

    # Display summary metrics - 1st Row (Means)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Present Value", f"${pv.mean():,.0f}")
    col2.metric("Avg Deaths per Trial", f"{deaths.mean():.1f}")
    col3.metric("Avg Lapses per Trial", f"{lapses.mean():.1f}")
    col4.metric("Avg PV per Policy", f"${pv_per_policy.mean():,.2f}")

    # Display summary metrics - 2nd Row (Standard Deviations)
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Std Dev PV", f"${pv.std():,.0f}")
    col6.metric("Std Dev Deaths", f"{deaths.std():.1f}")
    col7.metric("Std Dev Lapses", f"{lapses.std():.1f}")
    col8.metric("Std Dev PV/Policy", f"${pv_per_policy.std():,.2f}")

    st.divider()
    st.subheader("Distributions from Simulation")

    # Set visual style
    sns.set(style="whitegrid")

    # Plot 1 - Deaths
    fig1, ax1 = plt.subplots()
    sns.histplot(deaths, bins=30, kde=True, ax=ax1)
    ax1.set_title("Deaths per Trial")
    st.pyplot(fig1)

    # Plot 2 - Lapses
    fig2, ax2 = plt.subplots()
    sns.histplot(lapses, bins=30, kde=True, ax=ax2, color="orange")
    ax2.set_title("Lapses per Trial")
    st.pyplot(fig2)

    # Plot 3 - Total PV
    fig3, ax3 = plt.subplots()
    sns.histplot(pv, bins=30, kde=True, ax=ax3, color="green")
    ax3.set_title("Total Present Value of Claims")
    st.pyplot(fig3)

    # Plot 4 - PV per Policy
    fig4, ax4 = plt.subplots()
    sns.histplot(pv_per_policy, bins=30, kde=True, ax=ax4, color="purple")
    ax4.set_title("Present Value per Policy")
    st.pyplot(fig4)
