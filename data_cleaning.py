from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "ApexPlanet_DataAnalytics_Dataset.xlsx"
OUTPUT = ROOT / "output"
DOCS = ROOT / "docs"

OUTPUT.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)

df = pd.read_excel(INPUT, sheet_name="Sales_Dataset")

# Profile
profile = pd.DataFrame({
    "Column": df.columns,
    "Data_Type": [str(df[c].dtype) for c in df.columns],
    "Missing_Count": [int(df[c].isna().sum()) for c in df.columns],
    "Missing_Percentage": [(df[c].isna().mean() * 100).round(2) for c in df.columns],
    "Unique_Values": [int(df[c].nunique(dropna=True)) for c in df.columns],
})
profile.to_csv(DOCS / "data_quality_profile.csv", index=False)

duplicates = df[df["Order_ID"].duplicated(keep=False)].sort_values("Order_ID")
duplicates.to_csv(DOCS / "duplicate_order_id_report.csv", index=False)

# Clean
clean = df.copy()
clean["Order_Date"] = pd.to_datetime(clean["Order_Date"], errors="coerce")

for c in ["Order_ID", "Customer_ID", "Customer_Name", "Gender", "City", "Product", "Category"]:
    clean[c] = clean[c].astype("string").str.strip()

clean["Age"] = clean["Age"].fillna(clean["Age"].median())
clean["City"] = clean["City"].fillna("Unknown")

clean["Age_Group"] = pd.cut(
    clean["Age"],
    bins=[0, 17, 25, 35, 50, 65, np.inf],
    labels=["Under 18", "18-25", "26-35", "36-50", "51-65", "66+"],
    include_lowest=True
)

clean["Sales_Check"] = (clean["Quantity"] * clean["Unit_Price"]).round(2)
clean["Sales_Check_Status"] = np.where(
    np.isclose(clean["Sales_Check"], clean["Total_Sales"], atol=0.01),
    "Valid", "Mismatch"
)
clean["Transaction_ID"] = [f"TXN{i:06d}" for i in range(1, len(clean) + 1)]

clean = clean[
    ["Transaction_ID", "Order_ID", "Order_Date", "Customer_ID", "Customer_Name",
     "Age", "Age_Group", "Gender", "City", "Product", "Category",
     "Quantity", "Unit_Price", "Total_Sales", "Sales_Check", "Sales_Check_Status"]
]

clean.to_csv(OUTPUT / "sales_cleaned.csv", index=False)
clean.to_excel(OUTPUT / "sales_cleaned.xlsx", index=False)

print("Task 1 cleaning completed.")
print(f"Rows: {len(clean)}")
print(f"Columns: {len(clean.columns)}")
