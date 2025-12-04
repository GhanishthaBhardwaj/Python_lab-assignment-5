#Name: GHnanishtha Bhardwaj
#Class: B.tech CSE 1st Year (AI ML) Section A
#Roll No: 2501730296

import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

print("Working directory:", os.getcwd())

data_dir = "data"
output_dir = "output"
Path(output_dir).mkdir(exist_ok=True)


folder_path = Path(data_dir)
csv_list = list(folder_path.glob("*.csv"))
frames_list = []

print("Reading CSV files from:", data_dir)

for csv_file in csv_list:
    try:
        temp_df = pd.read_csv(csv_file)
        temp_df["src_file"] = csv_file.name
        frames_list.append(temp_df)
        print("Loaded:", csv_file.name)
    except Exception as err:
        print("Error loading:", csv_file.name, "->", err)

if len(frames_list) == 0:
    print("No data found.")
    raise SystemExit

energy_df = pd.concat(frames_list, ignore_index=True)


energy_df["timestamp"] = pd.to_datetime(energy_df["timestamp"], errors="coerce")
energy_df = energy_df.dropna(subset=["timestamp"])

print("\nData Loaded Successfully. Preview:\n")
print(energy_df.head())


def daily_usage(table):
    return table.resample("D", on="timestamp")["kwh"].sum()

def weekly_usage(table):
    return table.resample("W", on="timestamp")["kwh"].sum()

def building_stats(table):
    return table.groupby("building")["kwh"].agg(["mean", "min", "max", "sum"])

daily_totals = daily_usage(energy_df)
weekly_totals = weekly_usage(energy_df)
building_summary = building_stats(energy_df)

print("\n--- Building Summary ---\n")
print(building_summary)


class MeterReading:
    def __init__(self, when, units):
        self.timestamp = when
        self.kwh = units

class Building:
    def __init__(self, label):
        self.name = label
        self.readings = []

    def add_reading(self, reading_obj):
        self.readings.append(reading_obj)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.readings)

    def generate_report(self):
        total = self.calculate_total_consumption()
        return f"{self.name}: Total monthly consumption = {total:.2f} kWh"

class BuildingManager:
    def __init__(self):
        self.items = {}

    def add_reading(self, building_name, when, units):
        if building_name not in self.items:
            self.items[building_name] = Building(building_name)
        self.items[building_name].add_reading(MeterReading(when, units))

    def generate_all_reports(self):
        lines = []
        for b in self.items.values():
            lines.append(b.generate_report())
        return lines

manager = BuildingManager()

for _, row in energy_df.iterrows():
    manager.add_reading(row["building"], row["timestamp"], row["kwh"])

print("\n--- OOP Building Reports ---\n")
for line in manager.generate_all_reports():
    print(line)


plt.figure(figsize=(14, 10))

plt.subplot(3, 1, 1)
plt.plot(daily_totals.index, daily_totals.values)
plt.title("Daily Electricity Usage")
plt.xlabel("Date")
plt.ylabel("kWh")

plt.subplot(3, 1, 2)
plt.bar(weekly_totals.index.astype(str), weekly_totals.values)
plt.title("Weekly Electricity Usage")
plt.xlabel("Week")
plt.ylabel("kWh")

plt.subplot(3, 1, 3)
plt.scatter(energy_df["timestamp"], energy_df["kwh"], alpha=0.5)
plt.title("Scatter Plot — All Readings")
plt.xlabel("Timestamp")
plt.ylabel("kWh")

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "dashboard.png"))
plt.close()

print("\nDashboard saved as output/dashboard.png")

energy_df.to_csv(os.path.join(output_dir, "cleaned_energy_data.csv"), index=False)
building_summary.to_csv(os.path.join(output_dir, "building_summary.csv"))

with open(os.path.join(output_dir, "summary.txt"), "w") as f:
    f.write("Campus Energy Summary Report\n")
    f.write("----------------------------\n")
    f.write(f"Total Campus Consumption: {energy_df['kwh'].sum():.2f} kWh\n")
    f.write(f"Highest Consuming Building: {building_summary['sum'].idxmax()}\n")
    f.write("\nWeekly Totals:\n")
    f.write(str(weekly_totals))
    f.write("\n\nDaily Totals:\n")
    f.write(str(daily_totals))

print("Export complete: cleaned_energy_data.csv, building_summary.csv, summary.txt")
print("Project Finished.")

