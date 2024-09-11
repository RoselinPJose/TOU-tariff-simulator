#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import pandas as pd
import numpy as np
from simulation1 import simulate_tariff, compare_with_original

st.title('Custom Tariff TOU Tariff Simulator')

# File upload for consumption and usage data.
#Files upload
 #consumption_summed_file: This is the file that contains each customer's half-hour usage charge summed for a month.
 #total_daily_usage_file: This file contains the total daily energy usage for each customer. 
consumption_summed_file = st.file_uploader("Upload Consumption Summed File", type=["xlsx"], key="consumption_summed_file")
total_daily_usage_file = st.file_uploader("Upload Total Daily Usage File", type=["xlsx"], key="total_daily_usage_file")

#The files are uploaded by the user and then read into pandas DataFrames.
if consumption_summed_file and total_daily_usage_file:
    """
    Read and process the consumption and daily usage data files once they are uploaded.
    The data includes customer energy consumption over half-hour periods (consumption_summed) 
    and the total daily energy usage for each customer (total_daily_usage).
    """
    # Read the uploaded files
    consumption_summed = pd.read_excel(consumption_summed_file)
    total_daily_usage = pd.read_excel(total_daily_usage_file)

    #Column names are converted to strings because sometimes time columns (like "00:00", "00:30") might be treated differently. This ensures the column names are processed consistently throughout the analysis.
    # Convert all column names to strings in both DataFrames
    consumption_summed.columns = consumption_summed.columns.astype(str)

    # Section for creating custom tariffs based on time ranges
    st.subheader("Create Custom Tariff with Time Ranges")
    """
    Allow the user to input their custom tariff values based on the time of day. 
    They can define general rates for the daytime, and special rates for night 
    and peak time periods.
    """
    
    # Input general rate for daytime
    general_rate = st.number_input("Enter General Daytime Rate (kWh)", value=0.2, step=0.01, key="general_rate")

    # Define time ranges for night, and peak
    night_start = st.time_input("Night Start Time", value=pd.to_datetime("23:00:00").time(), key="night_start")
    night_end = st.time_input("Night End Time", value=pd.to_datetime("08:00:00").time(), key="night_end")
    
    # Define peak time ranges
    peak_start = st.time_input("Peak Start Time", value=pd.to_datetime("17:00:00").time(), key="peak_start")
    peak_end = st.time_input("Peak End Time", value=pd.to_datetime("19:00:00").time(), key="peak_end")
    
    # Input rate multipliers
    night_multiplier = st.number_input("Enter Night Rate Multiplier", value=0.5, step=0.1, key="night_multiplier")
    peak_multiplier = st.number_input("Enter Peak Rate Multiplier", value=1.5, step=0.1, key="peak_multiplier")

    #Limit: This is the maximum amount of energy (in kWh) that can be consumed before an additional charge is applied.
    #Excess Multiplier: If a customer exceeds the energy limit, the excess usage is multiplied by this value.
    # Input parameters for limit and excess multiplier
    limit = st.number_input("Enter Limit (kWh)", min_value=0.0, step=0.1)
    excess_multiplier = st.number_input("Enter Excess Multiplier", min_value=1.0, step=0.1)
    
    if st.button("Run Simulation with Custom Tariff", key="run_simulation"):
        """
        Once the "Run Simulation" button is pressed, the simulation is carried out 
        using the custom tariff rates provided by the user. The results will include
        the simulated costs for each customer, comparisons with original usage, 
        and various visualizations.
        """
        # Initialize rates with general rate
        custom_tariff_rates = pd.Series(general_rate, index=consumption_summed.columns[1:])
        #This section initializes the tariff rates for each half-hour interval. By default, it sets all intervals to the general daytime rate.
        #For each half-hour time, the code checks if it falls into the night or peak period and applies the corresponding rate multiplier.
        
        # Apply rates based on time ranges
        #Peak Rates: If the time falls within the defined peak period, the rate for that interval is multiplied by the peak multiplier.
        #Night Rates: If the time falls within the night period, the rate is multiplied by the night multiplier.
        #Daytime Rates: All other times remain at the general rate.
        for time_str in custom_tariff_rates.index:
            time_obj = pd.to_datetime(time_str).time()
        
            # Apply peak rates
            if peak_start <= time_obj < peak_end:
                custom_tariff_rates[time_str] *= peak_multiplier
            # Apply night rates
            elif (night_start <= time_obj) or (time_obj < night_end):
                custom_tariff_rates[time_str] *= night_multiplier
        # Daytime rate remains as general_rate (already initialized)

        # Run the simulation with the custom tariff rates
        #The custom tariff rates are applied to the half-hourly consumption for each customer, and the total cost for the month is calculated for each customer.
        simulated_cost = simulate_tariff(consumption_summed, custom_tariff_rates, limit=limit, excess_multiplier=excess_multiplier)
    
        # Compare with original usage
        #The simulated cost is compared against the original usage to assess how much customers would save or spend more under the new tariff structure.
        comparison = compare_with_original(total_daily_usage, simulated_cost)
        
        # Display results
        st.write("Simulation Results:")
        st.dataframe(comparison)
        
        # Compare with original usage
        comparison = compare_with_original(total_daily_usage, simulated_cost)
        
        # Add Savings column
        comparison['Savings'] = comparison['Original Usage'] - comparison['Simulated Cost']
        
        # Visualization: Histogram of Percentage Differences
        st.subheader("Interpretation of Results")
        st.write("Histogram of Percentage Differences:")
        fig, ax = plt.subplots()
        comparison['Percent Difference'].hist(bins=50, ax=ax)
        ax.set_title('Percentage Difference Distribution for Custom Tariff')
        ax.set_xlabel('Percentage Difference (%)')
        ax.set_ylabel('Number of Customers')
        st.pyplot(fig)
        
        """
        Count how many customers experienced an increase, decrease, or no change in their energy costs.
        This is done by analyzing the percentage difference between their original usage and simulated costs.
        """
        # Count of Increases, Decreases, No Change
        st.write("Count of Customers with Increase, Decrease, or No Change:")
        comparison['Change'] = comparison['Percent Difference'].apply(
            lambda x: 'Increase' if x > 0 else ('Decrease' if x < 0 else 'No Change'))
        change_counts = comparison['Change'].value_counts()
        
        fig, ax = plt.subplots()
        change_counts.plot(kind='bar', ax=ax, color=['green', 'red', 'blue'])
        ax.set_title('Customer Count by Change Category for Custom Tariff')
        ax.set_xlabel('Change Category')
        ax.set_ylabel('Number of Customers')
        st.pyplot(fig)
        
        # New Feature: Scatter Plot of Savings
        st.subheader("Customer Savings Analysis - Scatter Plot")
        fig, ax = plt.subplots()
        comparison['Customer Index'] = comparison.index
        ax.scatter(comparison['Customer Index'], comparison['Savings'], 
                   c=['green' if x > 0 else 'red' for x in comparison['Savings']], s=50)
        ax.axhline(0, color='black', linewidth=1)
        ax.set_title('Customer Savings Analysis')
        ax.set_xlabel('Customer Index')
        ax.set_ylabel('Savings')
        st.pyplot(fig)
        
        # Add Savings column
        comparison['Savings'] = comparison['Original Usage'] - comparison['Simulated Cost']
        
        # Visualization: Histogram with KDE Overlay
        st.subheader("Customer Savings Analysis - Histogram with KDE Overlay")
        
        fig, ax = plt.subplots()
        sns.histplot(comparison['Savings'], kde=True, ax=ax, color='blue', bins=30)
        ax.set_title('Distribution of Customer Savings with KDE')
        ax.set_xlabel('Savings')
        ax.set_ylabel('Number of Customers')
        st.pyplot(fig)
        
        # Define savings thresholds for segmentation
        high_savings_threshold = 50   # Adjust threshold based on your data
        moderate_savings_threshold = 10
        moderate_loss_threshold = -10
        high_loss_threshold = -50
        
        """
        Segment customers based on their savings to classify them into categories:
        'High Savings', 'Moderate Savings', 'Minimal Change', 'Moderate Loss', 'High Loss'.
        This segmentation helps understand the impact of the tariff changes on different customers.
        """
        # Segment customers
        conditions = [
            (comparison['Savings'] >= high_savings_threshold),
            (comparison['Savings'] >= moderate_savings_threshold) & (comparison['Savings'] < high_savings_threshold),
            (comparison['Savings'] > moderate_loss_threshold) & (comparison['Savings'] < moderate_savings_threshold),
            (comparison['Savings'] <= moderate_loss_threshold) & (comparison['Savings'] > high_loss_threshold),
            (comparison['Savings'] <= high_loss_threshold)
        ]
        choices = ['High Savings', 'Moderate Savings', 'Minimal Change', 'Moderate Loss', 'High Loss']
        comparison['Segment'] = np.select(conditions, choices)
        
        # Count customers in each segment
        segment_counts = comparison['Segment'].value_counts().sort_index()
        
        # Visualization: Bar plot of customer segments
        st.subheader("Customer Segmentation Based on Savings")
        
        fig, ax = plt.subplots()
        segment_counts.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Customer Segmentation by Savings')
        ax.set_xlabel('Segment')
        ax.set_ylabel('Number of Customers')
        
        # Define the ranges for each segment (as example thresholds)
        ranges = {
            'High Savings': (50, float('inf')),  # Replace with actual savings thresholds
            'Moderate Savings': (10, 50),
            'Minimal Change': (-10, 10),
            'Moderate Loss': (-50, -10),
            'High Loss': (float('-inf'), -50)
        }

        # Add bands to the plot for each segment range
        for idx, (segment, count) in enumerate(segment_counts.items()):
            range_start, range_end = ranges[segment]
    
            # Set the band color based on the segment
            color = 'lightgreen' if 'Savings' in segment else 'lightcoral' if 'Loss' in segment else 'lightgrey'
    
            # Add the band with a rectangle patch
            ax.axhspan(ymin=range_start, ymax=range_end, xmin=idx - 0.4, xmax=idx + 0.4, color=color, alpha=0.3)

            # Annotate the bar with the range
            ax.text(idx, count, f"{range_start} to {range_end}%", ha='center', va='bottom', fontsize=10, color='black')

        st.pyplot(fig)
        
        # Display the count of customers in each segment
        st.subheader("Customer Count in Each Segment:")
        # Write each segment and its customer count to the Streamlit app
        for segment, count in segment_counts.items():
            st.write(f"{segment}: {count} customers")
