#!/usr/bin/env python
# coding: utf-8

import pandas as pd

#This function simulate_tariff calculates the total cost for each customer based on their energy consumption and a custom tariff structure.
 #consumption_summed: This is a DataFrame that contains the half-hourly energy usage for each customer over a month.
 #rates: A dictionary that maps each time period (e.g., '00:00', '00:30') to a specific tariff rate.
 #limit: The maximum allowed energy consumption (in kWh) before additional charges are applied.
 #excess_multiplier: The multiplier applied to any energy usage beyond the specified limit.
 #total_cost: This Series will store the total cost for each customer. It's initialized with zero for each customer.
def simulate_tariff(consumption_summed, rates, limit, excess_multiplier):
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
#A new DataFrame called comparison is created. It contains the following columns:
#AnonymisedMPRN: The unique identifier for each customer.
#Original Usage: The original daily energy usage for each customer from the total_daily_usage file.
#Simulated Cost: The calculated total cost for each customer based on the custom tariff structure from the simulate_tariff() function.
def compare_with_original(total_daily_usage, simulated_cost):
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
