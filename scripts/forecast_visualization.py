import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates

# Read the CSV file
df = pd.read_csv('../predictions/forecast_summary.csv')

# Function to convert date string to datetime
def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

# Select a capability to visualize (let's use 'physical_intuition' as it has good data)
capability = 'code_generation'
cap_data = df[df['capability'] == capability].copy()

# Convert dates to datetime
cap_data['predicted_date'] = pd.to_datetime(cap_data['predicted_date'])
cap_data['ci_lower'] = pd.to_datetime(cap_data['ci_lower'])
cap_data['ci_upper'] = pd.to_datetime(cap_data['ci_upper'])

# Create the visualization
plt.figure(figsize=(12, 7))

# Plot the current performance point
current_perf = cap_data['current_performance'].iloc[0]
current_date = datetime.now()
plt.scatter(current_date, current_perf, color='blue', s=100, 
           label='Current Performance', zorder=5)

# Plot predicted points with confidence intervals
for _, row in cap_data.iterrows():
    plt.scatter(row['predicted_date'], row['threshold'], color='red', 
               s=80, zorder=4)
    plt.hlines(y=row['threshold'], xmin=row['ci_lower'], 
              xmax=row['ci_upper'], color='red', alpha=0.3)

# Connect current performance to predictions with a curve
dates = [current_date] + [d for d in cap_data['predicted_date']]
values = [current_perf] + [t for t in cap_data['threshold']]

# Create smooth curve
dates_num = mdates.date2num(dates)
z = np.polyfit(dates_num, values, 2)
p = np.poly1d(z)

# Generate points for smooth curve
date_range = pd.date_range(start=current_date, 
                          end=cap_data['predicted_date'].max(), 
                          periods=100)
plt.plot(date_range, p(mdates.date2num(date_range)), 
         '--', color='navy', alpha=0.5, label='Projected Trend')

# Customize the plot
plt.title(f'Forecast Curve for {capability.replace("_", " ").title()}', 
          fontsize=14, pad=20)
plt.xlabel('Year', fontsize=12)
plt.xticks(rotation=90)
plt.ylabel('Performance Level', fontsize=12)
plt.grid(True, alpha=0.3)

# Format x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(mdates.YearLocator(2))

# Add confidence interval legend
plt.plot([], [], color='red', alpha=0.3, linewidth=10, 
         label='95% Confidence Interval')

plt.legend()

# Adjust layout and save
plt.tight_layout()
plt.savefig('plots/forecast_curve.png', dpi=300, bbox_inches='tight')
plt.close()