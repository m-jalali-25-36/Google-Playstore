import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

def get_categores(name):
    
    try:
        response = requests.get(f"{BASE_URL}/categores/?name={name}", proxies= {"http": None,"https": None,})
        response.raise_for_status() 
        data = response.json() 
        return data.get('categores', []) 
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []


def create_app():
    st.subheader("Add New App")
    app_id = st.text_input("App ID")
    app_name = st.text_input("App Name")
    rating = st.number_input("Rating", min_value=0.0, max_value=5.0, step=0.1)
    rating_count = st.number_input("Rating Count", min_value=0, step=1)
    installs = st.number_input("Installs", min_value=0, step=1)
    price = st.number_input("Price", min_value=0.0, step=0.01)
    currency = st.text_input("Currency", max_chars=10)
    free = st.checkbox("Free")
    developer_id = st.number_input("Developer ID", min_value=1, step=1)
    
    if st.button("Create App"):
        data = {
            "AppID": app_id,
            "AppName": app_name,
            "Rating": rating,
            "RatingCount": rating_count,
            "Installs": installs,
            "Price": price,
            "Currency": currency,
            "Free": free,
            "DeveloperID": developer_id
        }
        response = requests.post(f"{BASE_URL}/apps/", json=data, proxies= {"http": None,"https": None,})
        st.write(response.json())

def list_apps():
    st.subheader("App List")
    category_query = st.text_input("Search for an category:")
    categories = get_categores(category_query)
    cat = [x['CategoryName'] for x in categories]
    cat.insert(0, 'All')
    category = st.selectbox('Select Category', options=cat)
    category = [x['CategoryID'] for x in categories if x['CategoryName'] == category][0] if category != 'All' else None
    rating = st.slider('Select Minimum Rating', 0, 5, 0)
    price = st.slider('Select Maximum Price', 0, 100, 0)
    content_rating = st.selectbox('Select Content Rating', options=['All', 'Everyone', 'Teen', 'Mature'])
    items_per_page = 10
    list_page_number = st.session_state.page_number  if 'page_number' in st.session_state else 1
    
    params = {
        "category_id": category,
        "rating": rating if rating else None,
        "price": price if price else None,
        "content_rating": content_rating if content_rating != 'All' else None,
        "page": list_page_number,
        "limit": items_per_page
    }
    response = requests.get(f"{BASE_URL}/apps/",params=params, proxies= {"http": None,"https": None,})
    if response.status_code == 200:
        response_json = response.json()
        apps = response_json.get("apps", [])
        if apps:
            df = pd.DataFrame(apps)
            st.dataframe(df)

            total_apps = response_json.get("total", 10)
            total_pages = (total_apps // items_per_page) + (1 if total_apps % items_per_page > 0 else 0)
            
            pagination = [1] if list_page_number > 3 else []
            pagination.extend([x for x in range(list_page_number-3, list_page_number+4) if 1 <= x <= total_pages])
            pagination.append(total_pages)
            st.radio('Select Page', options=pagination, key='page_number', index=pagination.index(list_page_number), horizontal=True)
            
        else:
            st.write("No apps found.")
    else:
        st.error("Error retrieving data.")

def delete_app():
    st.subheader("Delete App")
    app_id = st.text_input("App ID to delete")
    if st.button("Delete App"):
        response = requests.delete(f"{BASE_URL}/apps/{app_id}", proxies= {"http": None,"https": None,})
        st.write(response.json())

def update_app():
    st.subheader("Edit App")
    app_id = st.text_input("App ID to edit")
    app_name = st.text_input("App Name")
    rating = st.number_input("Rating", min_value=0.0, max_value=5.0, step=0.1)
    rating_count = st.number_input("Rating Count", min_value=0, step=1)
    installs = st.number_input("Installs", min_value=0, step=1)
    price = st.number_input("Price", min_value=0.0, step=0.01)
    currency = st.text_input("Currency", max_chars=10)
    free = st.checkbox("Free")
    developer_id = st.number_input("Developer ID", min_value=1, step=1)
    
    if st.button("Update App"):
        data = {
            "AppName": app_name,
            "Rating": rating,
            "RatingCount": rating_count,
            "Installs": installs,
            "Price": price,
            "Currency": currency,
            "Free": free,
            "DeveloperID": developer_id
        }
        response = requests.put(f"{BASE_URL}/apps/{app_id}", json=data, proxies= {"http": None,"https": None,})
        st.write(response.json())

def main():
    st.title("App Management")
    menu = ["Add App", "List Apps", "Delete App", "Edit App"]
    choice = st.sidebar.radio("Select Operation", menu, key='app_page')
    
    if choice == "Add App":
        create_app()
    elif choice == "List Apps":
        list_apps()
    elif choice == "Delete App":
        delete_app()
    elif choice == "Edit App":
        update_app()

if __name__ == "__main__":
    main()
