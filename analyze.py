import pandas as pd

df = pd.read_csv("data/commute_data.csv")

# Convert to minutes
df["minutes"] = df["duration_seconds"] / 60

# -----------------------------------
# AVERAGE COMMUTE PER CITY
# -----------------------------------

grouped = df.groupby(["person", "origin", "destination"])["minutes"].mean().reset_index()

print("\n=== Average Commutes ===")
print(grouped.sort_values("minutes"))

# -----------------------------------
# BEST CITY OVERALL (COMBINED)
# -----------------------------------

# Normalize all "home cities"
def get_home(row):
	if row["direction"] == "to_work":
		return row["origin"]
	else:
		return row["destination"]

df["home_city"] = df.apply(get_home, axis=1)

summary = df.groupby(["home_city", "person"])["minutes"].mean().reset_index()

pivot = summary.pivot(index="home_city", columns="person", values="minutes")

pivot["combined"] = pivot.mean(axis=1)

print("\n=== Best Cities (Combined) ===")
print(pivot.sort_values("combined"))

# -----------------------------------
# WORST CASE (IMPORTANT)
# -----------------------------------

worst = df.groupby(["home_city", "person"])["minutes"].max().reset_index()

print("\n=== Worst Case Commutes ===")
print(worst.sort_values("minutes", ascending=False))