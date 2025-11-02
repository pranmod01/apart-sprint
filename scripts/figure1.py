import json
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages

# Path to the JSON file (adjust if necessary)
json_path = "capability_heights.json"

# Output directory for plots
out_dir = "plots"
os.makedirs(out_dir, exist_ok=True)

def logistic(x, L, k, x0):
    """Logistic / sigmoid model: L / (1 + exp(-k*(x-x0)))"""
    return L / (1.0 + np.exp(-k*(x - x0)))

def jacobian_logistic(x_vals, params):
    """Return Jacobian matrix for logistic at x_vals for parameters [L, k, x0].
       For each x: [d/dL, d/dk, d/dx0]
    """
    L, k, x0 = params
    z = k * (x_vals - x0)
    s = 1.0 / (1.0 + np.exp(-z))  # sigmoid(k*(x-x0))
    ds_dk = s * (1 - s) * (x_vals - x0)
    ds_dx0 = s * (1 - s) * (-k)
    # dy/dL = s
    # dy/dk = L * ds_dk
    # dy/dx0 = L * ds_dx0
    J = np.vstack([
        s,
        L * ds_dk,
        L * ds_dx0
    ]).T  # shape (n_points, 3)
    return J

# Load JSON
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Use the 'all' group by default
capabilities = data.get('all', {})

# Create PDF with all figures (optional)
pdf_path = os.path.join(out_dir, "capabilities_logistic_fits.pdf")
pdf = PdfPages(pdf_path)

for cap_key, cap_info in capabilities.items():
    heights = cap_info.get("heights", {})
    if not heights:
        print(f"Skipping {cap_key}: no heights data")
        continue

    # Convert to arrays
    years = np.array(sorted([int(y) for y in heights.keys()]))
    y_vals = np.array([float(heights[str(y)]) for y in years])

    # Skip any NaN
    mask = ~np.isnan(y_vals)
    years = years[mask]
    y_vals = y_vals[mask]

    if years.size == 0:
        print(f"Skipping {cap_key}: no valid numeric points")
        continue

    # Plot setup
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(years, y_vals, color='C0', label='data', zorder=10)
    ax.set_title(f"{cap_info.get('name', cap_key)} ({cap_key})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Height")
    ax.grid(alpha=0.3)

    # If too few data points, skip fit
    if len(years) < 3:
        ax.text(0.02, 0.95, "Not enough points for reliable logistic fit",
                transform=ax.transAxes, va='top', color='red')
        # Save and continue
        fname = f"{cap_key}_points_only.png"
        fig.savefig(os.path.join(out_dir, fname), bbox_inches='tight', dpi=150)
        pdf.savefig(fig)
        plt.close(fig)
        print(f"{cap_key}: plotted points only (n={len(years)})")
        continue

    # Fit logistic curve
    # initial guesses and bounds
    y_max = np.nanmax(y_vals)
    L0 = y_max * 1.2 if y_max > 0 else 1.0
    k0 = 1.0
    x0_0 = np.median(years)

    # bounds: L >= 0, k between -10 and 10, x0 between min-5 and max+5
    ub_L = max(L0 * 10, y_max + 1e-6)
    bounds_lower = [0.0, -10.0, years.min() - 5]
    bounds_upper = [ub_L, 10.0, years.max() + 5]

    try:
        popt, pcov = curve_fit(
            logistic, years, y_vals,
            p0=[L0, k0, x0_0],
            bounds=(bounds_lower, bounds_upper),
            maxfev=20000
        )
    except Exception as e:
        print(f"{cap_key}: logistic fit failed ({e}); plotting points only")
        ax.text(0.02, 0.95, f"Fit failed: {e}", transform=ax.transAxes, va='top', color='red')
        fname = f"{cap_key}_fit_failed.png"
        fig.savefig(os.path.join(out_dir, fname), bbox_inches='tight', dpi=150)
        pdf.savefig(fig)
        plt.close(fig)
        continue

    # Predicted curve and 95% CI
    x_pad = 1.5
    x_grid = np.linspace(years.min() - x_pad, years.max() + 3.0, 300)
    y_pred = logistic(x_grid, *popt)

    # Compute 95% CI using linear approximation from covariance: var(y_hat) = J * pcov * J^T
    if pcov is None or np.any(np.isnan(pcov)):
        # no covariance -> cannot compute CI
        y_lower = np.maximum(0, y_pred - 1.96 * np.std(y_vals))
        y_upper = y_pred + 1.96 * np.std(y_vals)
    else:
        J = jacobian_logistic(x_grid, popt)  # shape (n_grid, 3)
        # compute variance for each predicted point
        y_var = np.array([np.dot(Ji, np.dot(pcov, Ji)) for Ji in J])
        y_std = np.sqrt(np.maximum(0, y_var))
        y_lower = y_pred - 1.96 * y_std
        y_upper = y_pred + 1.96 * y_std
        # clip lower to zero for nonnegative metrics
        y_lower = np.clip(y_lower, 0, None)

    # Plot fitted curve and CI
    ax.plot(x_grid, y_pred, color='C1', lw=2, label='logistic fit')
    ax.fill_between(x_grid, y_lower, y_upper, color='C1', alpha=0.25, label='95% CI')

    # Annotate fit parameters and their standard errors (if available)
    try:
        perr = np.sqrt(np.diag(pcov))
        param_text = (f"L={popt[0]:.4g} ± {perr[0]:.4g}\n"
                      f"k={popt[1]:.4g} ± {perr[1]:.4g}\n"
                      f"x0={popt[2]:.2f} ± {perr[2]:.2f}")
    except Exception:
        param_text = f"L={popt[0]:.4g}\nk={popt[1]:.4g}\nx0={popt[2]:.2f}"
    ax.text(0.98, 0.02, param_text, transform=ax.transAxes,
            ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
            fontsize=9)

    ax.legend()
    fname = f"{cap_key}.png"
    fig.savefig(os.path.join(out_dir, fname), bbox_inches='tight', dpi=150)
    pdf.savefig(fig)
    plt.close(fig)
    print(f"Saved plot for {cap_key} -> {os.path.join(out_dir, fname)}")

pdf.close()
print(f"All plots saved into {out_dir}, combined PDF at {pdf_path}")