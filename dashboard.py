import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Google Play Apps Dashboard", layout="wide")

API_URL = "http://127.0.0.1:8000/apps/"

page = st.sidebar.radio("Select a Page", ["Home", "Analysis", "CRUD Operations"])

if page == "Home":
    st.header("Welcome to the Google Play Apps Dashboard")
    st.write("This is the home page. Here, you can navigate through the dashboard to view analysis and perform CRUD operations.")

elif page == "Analysis":
    st.header("App Analysis & Filters")
    category = st.sidebar.text_input("Category")
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 2.5, 0.1)
    max_price = st.sidebar.number_input("Maximum Price ($)", 0.0, 100.0, 10.0)
    proxies = {
        "http": None,
        "https": None
    }
    params = {"category": category, "min_rating": min_rating, "max_price": max_price}
    response = requests.get(API_URL, params=params, proxies=proxies)

    if response.status_code == 200:
        apps = response.json()
        df = pd.DataFrame(apps)

        if df.empty:
            st.warning("No data available!")
        else:
            st.subheader("Apps List")
            st.dataframe(df)

            st.subheader("Rating Distribution")
            fig_rating = px.histogram(df, x="Rating", nbins=20, title="App Rating Distribution", color_discrete_sequence=["#636EFA"])
            st.plotly_chart(fig_rating, use_container_width=True)

            df['Released'] = pd.to_datetime(df['Released'], errors='coerce')
            df_release = df.groupby(df['Released'].dt.year).size().reset_index(name='Count')

            st.subheader("Release Trend")
            if not df_release.empty:
                fig_release = px.line(df_release, x="Released", y="Count", markers=True, title="App Releases Over Time", color_discrete_sequence=["#EF553B"])
                st.plotly_chart(fig_release, use_container_width=True)
            else:
                st.warning("No data available for release trends!")

            st.subheader("Top Categories")
            df_category = df["Category"].value_counts().reset_index()
            df_category.columns = ["Category", "Count"]

            fig_category = px.bar(df_category, x="Category", y="Count", title="Top App Categories", color_discrete_sequence=["#00CC96"])
            st.plotly_chart(fig_category, use_container_width=True)

    else:
        st.error("Error fetching data from API")

elif page == "CRUD Operations":

    st.sidebar.header("CRUD Operations")

    operation = st.sidebar.radio("Choose an operation", ["Create", "Read", "Update", "Delete"])

    if operation == "Create":
        st.subheader("Create a New App")
        app_name = st.text_input("App Name")
        category = st.text_input("Category")
        rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=2.5)
        price = st.number_input("Price ($)", min_value=0.0, value=0.0)
        
        if st.button("Create App"):
            app_data = {"AppName": app_name, "Category": category, "Rating": rating, "Price": price}
            response = requests.post(API_URL, json=app_data)
            if response.status_code == 200:
                st.success("App created successfully")
            else:
                st.error("Failed to create app")

    elif operation == "Read":
        st.subheader("Get App Details")
        app_id = st.number_input("Enter App ID", min_value=1)
        
        if st.button("Fetch App"):
            response = requests.get(f"{API_URL}{app_id}")
            if response.status_code == 200:
                app = response.json()
                st.write(f"App Name: {app['AppName']}")
                st.write(f"Category: {app['Category']}")
                st.write(f"Rating: {app['Rating']}")
                st.write(f"Price: ${app['Price']}")
            else:
                st.error("App not found")

    elif operation == "Update":
        st.subheader("Update App Details")
        app_id = st.number_input("Enter App ID to Update", min_value=1)
        app_name = st.text_input("New App Name")
        category = st.text_input("New Category")
        rating = st.number_input("New Rating", min_value=0.0, max_value=5.0, value=2.5)
        price = st.number_input("New Price ($)", min_value=0.0, value=0.0)
        
        if st.button("Update App"):
            app_data = {"AppName": app_name, "Category": category, "Rating": rating, "Price": price}
            response = requests.put(f"{API_URL}{app_id}", json=app_data)
            if response.status_code == 200:
                st.success("App updated successfully")
            else:
                st.error("Failed to update app")

    elif operation == "Delete":
        st.subheader("Delete an App")
        app_id = st.number_input("Enter App ID to Delete", min_value=1)
        
        if st.button("Delete App"):
            response = requests.delete(f"{API_URL}{app_id}")
            if response.status_code == 200:
                st.success("App deleted successfully")
            else:
                st.error("Failed to delete app")