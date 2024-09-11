#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd

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

def compare_with_original(total_daily_usage, simulated_cost):
    original_usage = total_daily_usage.set_index('AnonymisedMPRN')
    comparison = pd.DataFrame({
        'AnonymisedMPRN': total_daily_usage['AnonymisedMPRN'],
        'Original Usage': total_daily_usage['Daily Usage'],
        'Simulated Cost': simulated_cost
    })
    comparison['Difference'] = comparison['Simulated Cost'] - comparison['Original Usage']
    comparison['Percent Difference'] = (comparison['Difference'] / comparison['Original Usage']) * 100
    return comparison


# In[ ]:




