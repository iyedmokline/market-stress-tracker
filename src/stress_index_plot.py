
import matplotlib.pyplot as plt
from datetime import datetime

# === Data (Dates during my internship at BIAT – La Banque Internationale Arabe de Tunisie, Front Office Trading Floor) ===

dates = [
    "2025-06-16", "2025-06-17", "2025-06-18", "2025-06-19", "2025-06-20",
    "2025-06-23", "2025-06-24", "2025-06-25", "2025-06-26", "2025-06-27",
    "2025-06-30", "2025-07-01", "2025-07-02", "2025-07-03", "2025-07-04",
    "2025-07-07", "2025-07-08", "2025-07-09", "2025-07-10", "2025-07-11",
    "2025-07-14", "2025-07-15", "2025-07-16", "2025-07-17", "2025-07-18",
    "2025-07-21", "2025-07-22", "2025-07-23", "2025-07-24", "2025-07-25",
    "2025-07-28", "2025-07-29"
]

values = [
    53.51, 50.78, 53.42, 53.83, 53.73,
    55.15, 59.69, 69.23, 70.21, 70.49,
    67.82, 57.97, 57.61, 50.2, 49.73,
    50.27, 51.9, 42.67, 29.57, 30.04,
    31.23, 32.87, 29.79, 29.98, 27.94,
    27.28, 27.27,27.65, 31.01, 31.64,
    30.01, 31.19
]

x = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

# === Chart ===
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#f9f9fc')

# Colored zones for stress levels
ax.axhspan(0, 33.33, facecolor='#d6f5d6', alpha=0.5)
ax.axhspan(33.33, 66.66, facecolor='#fff6cc', alpha=0.5)
ax.axhspan(66.66, 100, facecolor='#fddddd', alpha=0.5)

# Curve with glow effect
ax.plot(x, values, color='#1f77b4', linewidth=2.5, zorder=3)
ax.scatter(x, values, color='white', edgecolor='#1f77b4', s=60, zorder=4, linewidth=2)

# Styled title
ax.set_title("Composite Market Stress Index\nJune 16 → July 25, 2025",
             fontsize=18, fontweight='bold', color='#222222', loc='center')

# Axes and labels
ax.set_xlabel("Date", fontsize=13, labelpad=10)
ax.set_ylabel("Stress (0 to 100)", fontsize=13, labelpad=10)

# Tick labels
ax.tick_params(axis='x', labelrotation=45)
ax.set_ylim(20, 80)

# Grid
ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.4)

# Remove borders
for spine in ax.spines.values():
    spine.set_visible(False)

# Global font setting
plt.rcParams['font.family'] = 'DejaVu Sans'

plt.tight_layout()
plt.show()


