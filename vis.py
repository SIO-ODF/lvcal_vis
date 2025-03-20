import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

data = []

# Read the file (can change this)
with open("metcal - Copy (4).out", "r") as file:
    lines = file.readlines()

# Parse the lines and assemble the dataframe
# Each sensor gets its own line
for line in lines:
    parts = line.strip().split()

    # Update the date if a new DATE line is found (should only be header)
    if line.startswith("DATE"):
        date_part = parts[1]

    # Detect time updates and assemble timestamp, allow it to break here
    if line.startswith("TIME") and date_part is not None:
        time_part = parts[1]
        current_timestamp = datetime.strptime(
            f"{date_part} {time_part}", "%d-%b-%Y %H:%M:%S"
        )

    # Detect sensor data (excluding headers and metadata)
    # Always seems to be 9 entries, sensor lines start with TP of some variety
    elif len(parts) == 9 and parts[0].startswith("TP"):
        sensor_id = parts[0]
        rawd = float(parts[1])
        value = float(parts[3])
        serial = parts[-1]  # Use Serial number instead of "TP1M"
        data.append([current_timestamp, sensor_id, rawd, value, serial])

# Convert to DataFrame
df = pd.DataFrame(data, columns=["Timestamp", "Sensor", "Rawd", "Value", "Serial"])
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
sensors = df["Serial"].unique()  # For later in visualizing

# Handle the setpoints (setting, time HH:MM)
setpoints_df = pd.read_csv("setpoints.csv", dtype={"sp": float, "time": str})
setpoints_df["Datetime"] = setpoints_df["time"].apply(lambda x: datetime.strptime(f"{date_part} {x}:00", "%d-%b-%Y %H:%M:%S"))

# Figure setup
fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 8), sharex=True)

# Plot Rawd (raw output) on the first subplot
for sensor in sensors:
    subset = df[df["Serial"] == sensor]
    axes[0].plot(
        subset["Timestamp"], subset["Rawd"], label=f"{sensor}", linestyle="--")
axes[0].set_ylabel("Rawd Readings")
axes[0].set_title("Sensor Rawd Readings Over Time", pad=20)
axes[0].legend()
axes[0].grid()

# Plot Value (transformed with current coefs) on the second subplot
for sensor in sensors:
    subset = df[df["Serial"] == sensor]
    axes[1].plot(subset["Timestamp"], subset["Value"], label=f"{sensor}")
axes[1].set_ylabel("Value Readings")
axes[1].set_title("Sensor Value Readings Over Time", pad=20)
axes[1].set_xlabel("Timestamp")
axes[1].legend()
axes[1].grid()

# Add vertical lines for the setpoints
for idx, row in setpoints_df.iterrows():
    setpoint_time = row["Datetime"]
    sp_value = row["sp"]
    
    # Draw the vertical line at the setpoint time
    axes[0].axvline(setpoint_time, color="grey", linestyle="-", linewidth=2)
    axes[1].axvline(setpoint_time, color="grey", linestyle="-", linewidth=2)
    
    # Add label for the setpoint value at the top of the figure
    axes[0].text(setpoint_time, max(df["Rawd"]) * 1.05, f"{sp_value}", ha="center", va="bottom", color="black", fontsize=10)
    axes[1].text(setpoint_time, max(df["Value"]) * 1.05, f"{sp_value}", ha="center", va="bottom", color="black", fontsize=10)

plt.xticks(rotation=45)
plt.tight_layout()

# Save the figure
plt.savefig("sensor_data_subplots.png", dpi=300, bbox_inches="tight")
plt.close()
