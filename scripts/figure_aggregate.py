import json
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages

# Path to the JSON file
json_path = "../data/intermediate/capability_heights.json"
out_dir = "plots"
os.makedirs(out_dir, exist_ok=True)

def logistic(x, L, k, x0):
    """Logistic / sigmoid model: L / (1 + exp(-k*(x-x0)))"""
    return L / (1.0 + np.exp(-k*(x - x0)))

# Load JSON
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

capabilities = data.get('all', {})

# Create a large figure for all capabilities
plt.figure(figsize=(12, 8))

# Create a color map for different capabilities
colors = plt.cm.tab20(np.linspace(0, 1, len(capabilities)))

# Store legend handles
legend_handles = []

for (cap_key, cap_info), color in zip(capabilities.items(), colors):
    heights = cap_info.get("heights", {})
    if not heights:
        continue

    # Convert to arrays
    years = np.array(sorted([int(y) for y in heights.keys()]))
    y_vals = np.array([float(heights[str(y)]) for y in years])

    # Skip any NaN
    mask = ~np.isnan(y_vals)
    years = years[mask]
    y_vals = y_vals[mask]

    if years.size < 3:
        # Plot points only if too few for fitting
        scatter = plt.scatter(years, y_vals, color=color, alpha=0.6, 
                            label=f"{cap_info.get('name', cap_key)}", zorder=10)
        legend_handles.append(scatter)
        continue

    # Fit logistic curve
    y_max = np.nanmax(y_vals)
    L0 = y_max * 1.2 if y_max > 0 else 1.0
    k0 = 1.0
    x0_0 = np.median(years)

    bounds_lower = [0.0, -10.0, years.min() - 5]
    bounds_upper = [L0 * 10, 10.0, years.max() + 5]

    try:
        popt, _ = curve_fit(
            logistic, years, y_vals,
            p0=[L0, k0, x0_0],
            bounds=(bounds_lower, bounds_upper),
            maxfev=20000
        )

        # Plot data points and fitted curve
        scatter = plt.scatter(years, y_vals, color=color, alpha=0.6, 
                            label=f"{cap_info.get('name', cap_key)}", zorder=10)
        
        # Predicted curve
        x_grid = np.linspace(years.min() - 1, years.max() + 1, 100)
        y_pred = logistic(x_grid, *popt)
        line = plt.plot(x_grid, y_pred, color=color, alpha=0.4, linestyle='-', zorder=5)
        
        legend_handles.append(scatter)
        
    except Exception as e:
        # If fit fails, just plot the points
        scatter = plt.scatter(years, y_vals, color=color, alpha=0.6, 
                            label=f"{cap_info.get('name', cap_key)}", zorder=10)
        legend_handles.append(scatter)

plt.grid(alpha=0.2)
plt.xlabel("Year")
plt.ylabel("Height")
plt.title("Aggregate View of All Capabilities")

# Adjust legend
plt.legend(handles=legend_handles, bbox_to_anchor=(1.05, 1), 
          loc='upper left', borderaxespad=0., 
          bbox_transform=plt.gca().transAxes)

# Adjust layout to prevent legend cutoff
plt.tight_layout()

# Save the plot
output_path = os.path.join(out_dir, "capabilities_aggregate.png")
plt.savefig(output_path, bbox_inches='tight', dpi=150)
print(f"Saved aggregate plot to {output_path}")
plt.close()