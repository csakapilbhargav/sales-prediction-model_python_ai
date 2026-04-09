import pandas as pd
import numpy as np

def generate_csv():
    years = list(range(2000, 2027))
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    all_data = []
    
    # Base values that will grow slightly over the years
    base_revenue = 4000000
    base_expenses = 3500000
    
    for year in years:
        # Yearly growth factor
        growth = 1 + (year - 2000) * 0.05 
        
        for month in months:
            # Add some randomness and seasonality
            seasonal_factor = 1 + np.sin(months.index(month) * (np.pi / 6)) * 0.1
            random_factor = np.random.uniform(0.9, 1.1)
            
            revenue = int(base_revenue * growth * seasonal_factor * random_factor)
            expenses = int(base_expenses * growth * seasonal_factor * np.random.uniform(0.85, 1.05))
            
            gross_profit = revenue - expenses
            net_profit = int(gross_profit * 0.6)
            
            # Realistic ratios
            quick_ratio = round(np.random.uniform(1.0, 2.5), 2)
            current_ratio = round(quick_ratio + 0.2, 2)
            
            all_data.append({
                'Year': year,
                'Month': month,
                'Revenue': revenue,
                'Expenses': expenses,
                'Gross_Profit': gross_profit,
                'Net_Profit': net_profit,
                'Quick_Ratio': quick_ratio,
                'Current_Ratio': current_ratio
            })

    df = pd.DataFrame(all_data)
    df.to_csv('sales_data.csv', index=False)
    print(f"Generated sales_data.csv with {len(df)} records (2000-2026) successfully!")

if __name__ == "__main__":
    generate_csv()
