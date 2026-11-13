import streamlit as st
import pandas as pd

st.set_page_config(page_title="Customer Purchase Pattern Analysis", page_icon="🛒", layout="wide")

st.title("🛒 Customer Purchase Pattern Analysis Using Pig")
st.write("Customer spending and product purchase analysis dashboard")

st.info(
    "Demonstration note: This Streamlit dashboard calculates the analysis using Python and pandas. "
    "It presents the same analysis objectives and sample records as the Apache Pig project, "
    "but it does not execute Apache Pig, Hadoop, or MapReduce."
)

SAMPLE = [
    ["101", "Ravi", "Laptop", 1, 50000],
    ["102", "Pallavi", "Mobile", 2, 15000],
    ["103", "Suresh", "Headphones", 1, 2000],
    ["101", "Ravi", "Mouse", 2, 500],
    ["102", "Pallavi", "Laptop", 1, 50000],
    ["104", "Anil", "Mobile", 1, 15000],
    ["103", "Suresh", "Keyboard", 1, 1500],
    ["101", "Ravi", "Headphones", 2, 2000],
]
COLUMNS = ["Customer_ID", "Customer_Name", "Product", "Quantity", "Price"]

st.sidebar.header("Dataset")
uploaded_file = st.sidebar.file_uploader("Upload customer CSV (optional)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, dtype={"Customer_ID": str})
        missing = [col for col in COLUMNS if col not in df.columns]
        if missing:
            st.error("Missing required columns: " + ", ".join(missing))
            st.stop()
        df = df[COLUMNS].copy()
    except Exception as error:
        st.error(f"Unable to read CSV: {error}")
        st.stop()
else:
    df = pd.DataFrame(SAMPLE, columns=COLUMNS)

for col in ["Customer_ID", "Customer_Name", "Product"]:
    df[col] = df[col].astype(str).str.strip()
for col in ["Quantity", "Price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["Quantity", "Price"])
df = df[(df["Quantity"] >= 0) & (df["Price"] >= 0)].copy()
df["Quantity"] = df["Quantity"].astype(int)
df["Total_Amount"] = df["Quantity"] * df["Price"]

st.header("1. Customer Purchase Dataset")
st.dataframe(df[COLUMNS], use_container_width=True, hide_index=True)

a, b, c = st.columns(3)
a.metric("Total Transactions", len(df))
b.metric("Total Customers", df["Customer_ID"].nunique())
c.metric("Total Products", df["Product"].nunique())

st.header("2. Customer-wise Total Spending")
customer_summary = (
    df.groupby(["Customer_ID", "Customer_Name"], as_index=False)["Total_Amount"]
      .sum()
      .sort_values("Total_Amount", ascending=False)
      .rename(columns={"Total_Amount": "Total_Spending"})
)
st.dataframe(
    customer_summary.style.format({"Total_Spending": "₹{:,.0f}"}),
    use_container_width=True,
    hide_index=True
)
st.bar_chart(customer_summary.set_index("Customer_Name")["Total_Spending"])

st.header("3. Product-wise Purchase Quantity")
product_summary = (
    df.groupby("Product", as_index=False)["Quantity"]
      .sum()
      .sort_values(["Quantity", "Product"], ascending=[False, True])
      .rename(columns={"Quantity": "Total_Quantity"})
)
st.dataframe(product_summary, use_container_width=True, hide_index=True)
st.bar_chart(product_summary.set_index("Product")["Total_Quantity"])

st.header("4. Key Findings")
if not customer_summary.empty:
    best = customer_summary.iloc[0]
    st.success(
        f"Highest spending customer: {best['Customer_Name']} "
        f"(ID: {best['Customer_ID']}) — ₹{best['Total_Spending']:,.0f}"
    )
if not product_summary.empty:
    highest_qty = product_summary["Total_Quantity"].max()
    best_products = product_summary.loc[
        product_summary["Total_Quantity"] == highest_qty, "Product"
    ].tolist()
    st.write(f"Most purchased product(s): {', '.join(best_products)} — {highest_qty} units each.")

st.header("5. Apache Pig Latin Program")
with st.expander("View Pig Latin source code"):
    st.code("""purchases = LOAD '$input'
USING PigStorage(',')
AS (Customer_ID:chararray, Customer_Name:chararray,
    Product:chararray, Quantity:int, Price:double);

clean_data = FILTER purchases
BY Customer_ID != 'Customer_ID';

purchase_amount = FOREACH clean_data GENERATE
    Customer_ID, Customer_Name, Product, Quantity, Price,
    (Quantity * Price) AS Total_Amount;

grouped_data = GROUP purchase_amount
BY (Customer_ID, Customer_Name);

customer_totals = FOREACH grouped_data GENERATE
    group.Customer_ID AS Customer_ID,
    group.Customer_Name AS Customer_Name,
    SUM(purchase_amount.Total_Amount) AS Total_Spending;

sorted_customers = ORDER customer_totals BY Total_Spending DESC;
DUMP sorted_customers;

product_group = GROUP clean_data BY Product;
product_analysis = FOREACH product_group GENERATE
    group AS Product_Name,
    SUM(clean_data.Quantity) AS Total_Quantity;

sorted_products = ORDER product_analysis BY Total_Quantity DESC;
DUMP sorted_products;""", language="pig")

st.download_button(
    "Download dataset as CSV",
    data=df[COLUMNS].to_csv(index=False).encode("utf-8"),
    file_name="customer_purchases.csv",
    mime="text/csv"
)

st.caption("Sample records are the eight transactions supplied for this project.")
