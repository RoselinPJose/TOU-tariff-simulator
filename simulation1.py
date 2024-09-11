#!/usr/bin/env python
# coding: utf-8

import pandas as pd

#This function simulate_tariff calculates the total cost for each customer based on their energy consumption and a custom tariff structure.
def simulate_tariff(consumption_summed, rates, limit, excess_multiplier):
    """
    Simulates the total energy cost for each customer based on the custom tariff rates provided.

    Parameters:
    -----------
    consumption_summed : pd.DataFrame
        A DataFrame where each row represents a customer and each column (except the first) 
        represents their energy usage for a half-hour period over a month.
        
    rates : dict
        A dictionary containing the rates for each half-hour period (as column names).
        The rates will be applied to the consumption data.

    limit : float
        The maximum amount of energy (in kWh) that is charged at the base rate. 
        Any usage above this limit will be charged at a higher rate (based on excess_multiplier).

    excess_multiplier : float
        The multiplier applied to any energy usage that exceeds the limit.

    Returns:
    --------
    pd.Series
        A Series where each value represents the total cost of energy usage for a customer 
        based on the rates and limit provided.
    """
    total_cost = pd.Series(0, index=consumption_summed.index)
    
    for column in consumption_summed.columns[1:]:  # Start from the second column assuming the first is AnonymisedMPRN
        if column in rates:
            rate = rates[column]
            usage = consumption_summed[column]
            normal_usage = usage.apply(lambda x: min(x, limit))
            extra_usage = usage.apply(lambda x: max(x - limit, 0))
            total_cost += normal_usage * rate + extra_usage * rate * excess_multiplier
        else:
            print(f"Warning: No rate found for column '{column}'. Skipping this column.")
    
    return total_cost
    #Loop: The loop goes through each half-hourly column in the consumption_summed DataFrame, starting from the second column (assuming the first column contains customer identifiers, such as AnonymisedMPRN).
    #Check: For each time column (e.g., '00:00', '00:30'), it checks if there's a corresponding rate in the rates dictionary.
    #Rate and Usage: If a rate exists for that time period, it assigns the corresponding rate and retrieves the energy usage for that time period.

#This function compare_with_original compares the simulated costs against the original usage for each customer, calculating the difference and percentage change.
#Set Index: The total_daily_usage DataFrame is indexed by AnonymisedMPRN to ensure that customer usage data is properly aligned with the simulated cost data.
def compare_with_original(total_daily_usage, simulated_cost):
    """
    Compares the simulated cost of energy usage with the original daily usage to calculate 
    the differences and percentage differences for each customer.

    Parameters:
    -----------
    total_daily_usage : pd.DataFrame
        A DataFrame where each row represents a customer, with columns for the 'AnonymisedMPRN' 
        (customer ID) and 'Daily Usage' (total daily energy usage for the customer).

    simulated_cost : pd.Series
        A Series representing the simulated energy cost for each customer after applying the tariff.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the following columns:
        - 'AnonymisedMPRN': Customer ID
        - 'Original Usage': The total daily energy usage for each customer
        - 'Simulated Cost': The simulated cost of energy usage for each customer
        - 'Difference': The difference between the simulated cost and the original usage
        - 'Percent Difference': The percentage difference between the simulated cost and the original usage
    """
    original_usage = total_daily_usage.set_index('AnonymisedMPRN')
    comparison = pd.DataFrame({
        'AnonymisedMPRN': total_daily_usage['AnonymisedMPRN'],\
        'Original Usage': total_daily_usage['Daily Usage'],
        'Simulated Cost': simulated_cost
    })
    comparison['Difference'] = comparison['Simulated Cost'] - comparison['Original Usage']
    comparison['Percent Difference'] = (comparison['Difference'] / comparison['Original Usage']) * 100
    return comparison
#Difference: This column shows the absolute difference between the simulated cost and the original usage. It indicates how much more or less a customer would pay under the new tariff.
#Percent Difference: This column calculates the percentage difference between the simulated cost and the original usage, giving a relative measure of the impact of the new tariff.
