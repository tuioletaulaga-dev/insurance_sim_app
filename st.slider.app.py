import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page title ---
st.title("Life Insurance Simulation with Lapses")

# --- User Inputs via Sliders ---
num_policies = st.slider("Number of Policies", min_value=100, max_value=10000, value=1000, step=100)
num_trials = st.slider("Number of Trials", min_value=100, max_value=5000, value=1000, step=100)
policy_term = st.slider("Policy Term (years)", min_value=1, max_value=50, value=20)
start_age = st.slider("Starting Age", min_value=20, max_value=90, value=40)
death_benefit = st.slider("Death Benefit", min_value=1000, max_value=1000000, value=100000, step=1000)
discount_rate = st.slider("Discount Rate", min_value=0.00, max_value=0.20, value=0.06, step=0.005)

# --- Mortality and lapse assumptions ---
qx_dict = {age: min(0.0005 + 0.0001 * (age - start_age), 0.2) for age in range(start_age, start_age + policy_term + 1)}
lapse_dict = {year: 0.05 for year in range(1, policy_term + 1)}  # constant lapse rate
discount_factors = [(1 / (1 + discount_rate)) ** t for t in range(policy_term)]

# --- Simulation Logic ---
present_values = []
death_counts = []
lapse_counts = []

for trial in range(num_trials):
    trial_pv = 0
    trial_deaths = 0
    trial_lapses = 0

    for _ in range(num_policies):
        policy_lapsed = False

        for year_from_start in range(policy_term):
            current_age = start_age + year_from_start
            year = year_from_start + 1

            qx = qx_dict.get(current_age, 0)
            lapse_rate = lapse_dict.get(year, 0)

            if np.random.random() <= lapse_rate:
                trial_lapses += 1
                policy_lapsed = True
                break

            if np.random.random() <= qx:
                trial_pv += death_benefit * discount_factors[year_from_start]
                trial_deaths += 1
                break

    present_values.append(trial_pv)
    death_counts.append(trial_deaths)
    lapse_counts.append(trial_lapses)

# --- Display Results ---
st.subheader("Simulation Summary")
st.write(f"Average Present Value: ${np.mean(present_values):,.2f}")
st.write(f"Average Deaths per Trial: {np.mean(death_counts):.2f}")
st.write(f"Average Lapses per Trial: {np.mean(lapse_counts):.2f}")
st.write(f"Average PV per Policy: ${np.mean(present_values) / num_policies:,.2f}")

# --- Plot Histogram ---
fig, ax = plt.subplots()
ax.hist(present_values, bins=30, color='skyblue', edgecolor='black')
ax.set_title("Distribution of Present Values Across Trials")
ax.set_xlabel("Present Value")
ax.set_ylabel("Frequency")
st.pyplot(fig)
