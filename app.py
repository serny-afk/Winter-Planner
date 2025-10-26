import streamlit as st
import pandas as pd
import os

csv_file = "unavail.csv"

st.title("Winter Meetup Planner")

# Preset friend list
friends_list = ["Evan", "Zhen Yang", "Delon", "Zheng Da", "Ray", "Shao Ren", 
                "Eujin", "Mikaeil", "Jovan", "Sean", "Kai Jie", "Sern Yuan"]

# Possible dates
possible_dates = pd.date_range("2025-12-06", "2026-01-23").strftime("%Y-%m-%d").tolist()
df = pd.DataFrame({"Date": possible_dates})

# Friend selects their name
name = st.selectbox("Select your name:", friends_list)
unavailable_dates = st.multiselect("Select dates you CANNOT attend", possible_dates)

# ---- Submit availability ----
if st.button("Submit"):
    new_entry = pd.DataFrame({
        "Friend": [name],
        "Unavailable Dates": [",".join(unavailable_dates)]
    })

    try:
        if os.path.exists(csv_file):
            # Load existing CSV
            old_df = pd.read_csv(csv_file)
            # Remove previous submission for this friend
            old_df = old_df[old_df["Friend"] != name]
            # Combine old + new
            combined_df = pd.concat([old_df, new_entry], ignore_index=True)
            combined_df.to_csv(csv_file, index=False)
        else:
            # First submission, create CSV with headers
            new_entry.to_csv(csv_file, index=False)

        st.success(f"{name}'s availability has been recorded!")

    except Exception as e:
        st.error(f"Error saving submission: {e}")

# ---- Read and show availability ----
if os.path.exists(csv_file):
    unavail_df = pd.read_csv(csv_file)

    # Convert CSV to dict {friend: [unavailable_dates]}
    unavailable = {}
    for _, row in unavail_df.iterrows():
        friend = row["Friend"]
        dates_str = row["Unavailable Dates"]
        if pd.isna(dates_str) or dates_str.strip() == "":
            unavailable[friend] = []
        else:
            unavailable[friend] = [d.strip() for d in dates_str.split(",")]

    # Compute availability table
    for friend in friends_list:
        cant_make = unavailable.get(friend, [])
        df[friend] = df["Date"].apply(lambda d: 0 if d in cant_make else 1)

    df["Total Available"] = df.iloc[:, 1:].sum(axis=1)

    # Show table and best day
    st.subheader("Availability Summary")
    st.dataframe(df)

    best_count = df["Total Available"].max()
    best_days = df[df["Total Available"] == best_count]["Date"].tolist()
    st.success(f"Best day(s) for meetup: {', '.join(best_days)} ({best_count} people available)")

else:
    st.info("No submissions yet. Once friends submit, the availability summary will appear here.")