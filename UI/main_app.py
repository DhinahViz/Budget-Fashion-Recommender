import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import random
import datetime

# Page setup
st.set_page_config(page_title="🛍️ Unified Fashion Recommender", layout="wide")

# Load original product data
df = pd.read_csv("fashion_products_real.csv")
df = df[df["Category"] != "Dress"]

# Paths
base_dir = os.path.dirname(__file__)
filtered_path = os.path.join(base_dir, "filtered_results.csv")
history_path = os.path.join(base_dir, "user_history.csv")

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
max_price = st.sidebar.slider("💰 Maximum Budget", 100, 3000, 1500, step=100)
min_rating = st.sidebar.slider("⭐ Minimum Rating", 1.0, 5.0, 4.0, step=0.1)
category_options = ["All"] + sorted(df["Category"].unique())
category = st.sidebar.selectbox("👕 Category", category_options)

# Apply filters
filtered_df = df[(df["Price"] <= max_price) & (df["Rating"] >= min_rating)]
if category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == category]

# Save filtered results
filtered_df.to_csv(filtered_path, index=False)

# Hero section
st.markdown("<h1 style='text-align:center;'>🛍️Fashion Recommender</h1>", unsafe_allow_html=True)

# Display products
st.subheader("🎯 Filtered Products")
st.markdown(f"Showing **{len(filtered_df)}** products based on your filters.")
for _, row in filtered_df.iterrows():
    st.markdown(f"""
    <div style='background:#111;padding:1rem;margin:0.5rem;border-radius:10px;color:white;'>
        <strong>{row['Product_Name']}</strong><br>
        🏷️ {row['Brand']}<br>
        📦 {row['Category']}<br>
        💸 ₹{row['Price']}<br>
        ⭐ {row['Rating']}
    </div>
    """, unsafe_allow_html=True)

# Button Columns
col1, col2, col3, col4 = st.columns(4)

# ✅ Save to History
with col1:
    if st.button("✅ Save to History"):
        if not filtered_df.empty:
            try:
                # Always append new products to history, keeping only unique rows
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                filtered_df['Saved_At'] = now
                if os.path.exists(history_path):
                    existing = pd.read_csv(history_path)
                    combined = pd.concat([existing, filtered_df]).drop_duplicates().reset_index(drop=True)
                else:
                    combined = filtered_df.copy()
                combined.to_csv(history_path, index=False)
                st.success("✅ Products successfully saved to history!")
            except Exception as e:
                st.error(f"❌ Error saving history: {e}")
        else:
            st.warning("⚠️ No products to save.")

# 📜 View History
with col2:
    if st.button("📜 View History"):
        if os.path.exists(history_path):
            try:
                history_df = pd.read_csv(history_path)
                if history_df.empty:
                    st.info("📭 History is empty—try saving products first.")
                else:
                    st.subheader("📜 Your Saved History")
                    with st.expander("Show History List"):
                        for _, prod in history_df.iterrows():
                            saved_at = prod['Saved_At'] if 'Saved_At' in prod else 'N/A'
                            st.markdown(f"""
                            <div style='background:#222;padding:1rem;margin:0.5rem;border-radius:10px;color:white;'>
                                <strong>{prod['Product_Name']}</strong><br>
                                🏷️ {prod['Brand']}<br>
                                📦 {prod['Category']}<br>
                                💸 ₹{prod['Price']}<br>
                                ⭐ {prod['Rating']}<br>
                                🕒 Saved At: {saved_at}
                            </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error loading history: {e}")
        else:
            st.warning("⚠️ History file not found. Save products first.")

# 📊 Chartize Visual Insights
with col3:
    if st.button("📊 Chart Insights"):
        st.subheader("📊 Chart Insights")
    chart_type = st.selectbox("Choose Chart Type", ["Bar", "Pie", "Line"])
    if chart_type == "Bar":
        avg_rating = filtered_df.groupby("Brand")["Rating"].mean().sort_values(ascending=False).head(10)
        st.bar_chart(avg_rating)
    elif chart_type == "Pie":
        counts = filtered_df["Category"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    elif chart_type == "Line":
        trend_df = filtered_df.sort_values("Price")
        fig, ax = plt.subplots()
        ax.plot(trend_df["Price"], trend_df["Rating"], marker='o', linestyle='-', color='orchid')
        ax.set_xlabel("Price")
        ax.set_ylabel("Rating")
        ax.set_title("Price vs Rating Trend")
        st.pyplot(fig)

# 🧠 SmartPick AI Suggestions
with col4:
    if st.button("🧠 SmartPick"):
        st.subheader("🧠 AI-Based Smart Pick")

        def calculate_smart_score(row):
            score = (row["Rating"] * 2.5) - (row["Price"] / 500)
            if category != "All" and row["Category"] == category:
                score += 2
            return score

        filtered_df["SmartScore"] = filtered_df.apply(calculate_smart_score, axis=1)
        best_product = filtered_df.sort_values("SmartScore", ascending=False).iloc[0]

        st.markdown(f"""
        <div style='background:#111;padding:1rem;margin:0.5rem;border-radius:10px;color:white;'>
            <strong>{best_product['Product_Name']}</strong><br>
            🏷️ {best_product['Brand']}<br>
            📦 {best_product['Category']}<br>
            💸 ₹{best_product['Price']}<br>
            ⭐ {best_product['Rating']}<br>
            🧠 SmartScore: {round(best_product['SmartScore'], 2)}
        </div>
        """, unsafe_allow_html=True)

        # Summary Insights
        st.markdown("---")
        st.subheader("🔍 Smart Summary")
        st.markdown(f"🔹 Most Common Brand: **{filtered_df['Brand'].mode()[0]}**")
        st.markdown(f"🔹 Highest Rated Product: **{filtered_df.loc[filtered_df['Rating'].idxmax()]['Product_Name']}**")
        st.markdown(f"🔹 Average Price: ₹{int(filtered_df['Price'].mean())}")
