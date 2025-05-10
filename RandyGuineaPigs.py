# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns

# --- Simulation Functions ---
def simulate_matings(n_females=10, target_pregnancies=1, 
                     pregnancy_chance=0.091, pregnant_chance=0.0):
    """
    Simulates a guinea pig lovefest until a set number of pregnancies occur.

    Parameters:
    - n_females (int): Number of lady pigs available for romancing.
    - target_pregnancies (int): How many successful snuggles should lead to pregnancies.
    - pregnancy_chance (float): Chance of baby-making success with an unpregnant pig.
    - pregnant_chance (float): Chance of impregnating a pig who’s already preggers (typically zero).

    Returns:
    - dict: A record of each female's total snuggle sessions, split by pregnancy status.
    """
    knocked_up = set()
    shag_stats = {
        sow: {'total': 0, 'while_pregnant': 0, 'while_unpregnant': 0}
        for sow in range(n_females)
    }

    while len(knocked_up) < min(target_pregnancies, n_females):
        lucky_sow = random.randint(0, n_females - 1)
        already_preggers = lucky_sow in knocked_up
        conception_odds = pregnant_chance if already_preggers else pregnancy_chance

        shag_stats[lucky_sow]['total'] += 1
        if already_preggers:
            shag_stats[lucky_sow]['while_pregnant'] += 1
        else:
            shag_stats[lucky_sow]['while_unpregnant'] += 1

        if not already_preggers and random.random() < conception_odds:
            knocked_up.add(lucky_sow)

    return shag_stats

@st.cache_data(show_spinner=True)
def run_simulations(n_females=10, target_pregnancies=1, simulations=100, 
                    pregnancy_chance=0.091, pregnant_chance=0.0):
    """
    Runs the guinea pig mating simulation multiple times to analyze snuggle stats.

    Parameters:
    - n_females (int): Number of female guinea pigs per simulation.
    - target_pregnancies (int): Baby bumps required to end each mating spree.
    - simulations (int): Total number of times we run the guinea pig dating experiment.
    - pregnancy_chance (float): Probability of pregnancy if unpregnant.
    - pregnant_chance (float): Probability of pregnancy if already pregnant (should be zero).

    Returns:
    - pd.DataFrame: A log of piggy passion across all simulations.
    """
    all_matings = []

    for sim in range(simulations):
        session_log = simulate_matings(
            n_females=n_females,
            target_pregnancies=target_pregnancies,
            pregnancy_chance=pregnancy_chance,
            pregnant_chance=pregnant_chance
        )

        for sow_id, stats in session_log.items():
            all_matings.append({
                'Simulation': sim,
                'Female': sow_id,
                'Mating Count': stats['total'],
                'Shagged while Pregnant': stats['while_pregnant'],
                'Shagged while not Pregnant': stats['while_unpregnant']
            })

    return pd.DataFrame(all_matings)

# --- Streamlit UI ---
st.title("🐹 Guinea Pig Shagging Simulator")
st.markdown("This simulation explores the effects of shagging strategies on guinea pig population dynamics.")

with st.expander("💡 More information on how these guinea pig shenanigans are coded"):
    st.markdown("""
This app simulates guinea pig shagging sessions until a target number of pregnancies is achieved. Two functions do the heavy lifting:

- `simulate_matings(...)`: simulates one round of shagging and returns snuggle stats per female.
- `run_simulations(...)`: runs the above multiple times to provide meaningful distributions.

Here's how the functions are structured:
```python
def simulate_matings(n_females=10, target_pregnancies=1, 
                     pregnancy_chance=0.091, pregnant_chance=0.0):
    ""
    Simulates a guinea pig lovefest until a set number of pregnancies occur.
    
    Parameters:
    - n_females (int): Number of lady pigs available for romancing.
    - target_pregnancies (int): How many successful snuggles should lead to pregnancies.
    - pregnancy_chance (float): Chance of baby-making success with an unpregnant pig.
    - pregnant_chance (float): Chance of impregnating a pig who's already preggers (typically zero).
    
    Returns:
    - dict: A record of each female's total snuggle sessions, split by pregnancy status.
    ""

@st.cache_data(show_spinner=True)
def run_simulations(n_females=10, target_pregnancies=1, simulations=100, 
                    pregnancy_chance=0.091, pregnant_chance=0.0):
    ""
    Runs the guinea pig shagging simulation multiple times to analyze snuggle stats.

    Parameters:
    - n_females (int): Number of female guinea pigs per simulation.
    - target_pregnancies (int): Baby bumps required to end each shagging spree.
    - simulations (int): Total number of times we run the guinea pig dating experiment.
    - pregnancy_chance (float): Probability of pregnancy if unpregnant.
    - pregnant_chance (float): Probability of pregnancy if already pregnant (should be zero).

    Returns:
    - pd.DataFrame: A log of piggy passion across all simulations.
    ""
```""")

# Sidebar Inputs
st.sidebar.header("Simulation Parameters")
population_sizes = st.sidebar.multiselect(
    "Select Population Sizes", [100, 200, 300, 400], default=[100, 300]
)
simulations = st.sidebar.slider("Number of Simulations", 10, 500, 100, step=10)
target_pregnancies = st.sidebar.number_input("Target Pregnancies", 1, 500, 100)
pregnancy_chance = st.sidebar.slider("Pregnancy Chance (unpregnant)", 0.01, 0.5, 0.091, 0.005)

if st.sidebar.button("Run Simulation"):
    st.write("Crunching numbers... hold onto your hay bales 🐾")

    frames = []
    for pop in population_sizes:
        df = run_simulations(
            n_females=pop,
            target_pregnancies=target_pregnancies,
            simulations=simulations,
            pregnancy_chance=pregnancy_chance
        )
        df['Population'] = pop
        frames.append(df)

    mate_df = pd.concat(frames, ignore_index=True)

    melted_df = mate_df.melt(
        id_vars=['Population','Simulation', 'Female'],
        value_vars=['Shagged while Pregnant', 'Shagged while not Pregnant'],
        var_name='Mating Type',
        value_name='Shag_counts'
    )

    frequency_table = (
        melted_df
        .groupby(['Population','Simulation', 'Mating Type', 'Shag_counts'])
        .size()
        .reset_index(name='Num Females')
    )

    st.subheader("📊 Sample Output Data")
    st.dataframe(mate_df.head(2))

    st.subheader("🧮 Evaluation of Shagging Reproduction")
    mean_attempts = (mate_df
                     .groupby(['Simulation','Population'])
                     ['Mating Count'].sum().reset_index()
                     .groupby(['Population']).mean().reset_index()
                     .drop('Simulation', axis=1)
                     .rename(columns={'Mating Count': 'Mean Shagging Attempts'})
    )
    st.dataframe(mean_attempts)

    st.subheader("📊 Total Shagging Attempts per Population")
    agg_df = mate_df.groupby(['Simulation', 'Population'])['Mating Count'].sum().reset_index()
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.histplot(data=agg_df, x='Mating Count', hue='Population', bins=50, alpha=0.6, ax=ax2)
    ax2.set_title('Distribution of Shagging Attempts')
    ax2.set_xlabel('Shagging Attempts')
    ax2.set_ylabel('Shagging Attempt Frequency')
    st.pyplot(fig2)

    st.subheader("📊 Histogram of Mating Count per Female")

    for pop in mate_df['Population'].unique():
        st.markdown(f"**Population {pop} Females**") 
        fig, ax = plt.subplots(figsize=(10, 6))
        subset = mate_df[mate_df['Population'] == pop]
        sns.histplot(
            data=subset,
            x='Mating Count',
            bins=50,
            kde=False,
            ax=ax
        )
        ax.set_title(f"Distribution of Shag Counts per Female — Population {pop}")
        ax.set_xlabel("Number of Shags per Female")
        ax.set_ylabel("Frequency of a Female with a certain Shag Count")
        st.pyplot(fig)

    st.subheader("📉 Shagging Frequency Table")
    st.dataframe(frequency_table.head(2))

    st.subheader("📈 Distribution of Guinea Pig Shagging")
    for pop in frequency_table['Population'].unique():
        st.markdown(f"**Population {pop} Females**")
        fig, ax = plt.subplots(figsize=(10, 6))
        subset = frequency_table[frequency_table['Population'] == pop]
        sns.lineplot(data=subset,
                    x='Shag_counts',
                    y='Num Females',
                    hue='Mating Type',
                    errorbar='ci',
                    ax=ax)
        ax.set_title(f"Distribution of Shag Counts by Type — Population {pop}")
        ax.set_xlabel("Number of Shags")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
    
else:
    st.info("Use the sidebar to configure and run the simulation.")
