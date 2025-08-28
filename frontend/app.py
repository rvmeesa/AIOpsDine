import streamlit as st
import requests
from datetime import datetime
import logging
from frontend.utils import (
    send_faq_query, upload_vision_image, create_order, update_order_status,
    get_recommendations, get_analytics
)

# Configure logging
logging.basicConfig(level="INFO", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(page_title="AIO Restaurant Manager", layout="wide", page_icon="🍽️")

# Load custom CSS
with open("frontend/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("AIO Restaurant Manager")
page = st.sidebar.radio("Navigate", ["FAQ", "Orders", "Vision", "Recommendations", "Analytics", "Office"])

# API base URL
API_BASE = "http://localhost:8000/api"

# Fetch available tables
def get_available_tables():
    try:
        response = requests.get(f"{API_BASE}/tables")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch tables: {str(e)}")
        return [{"id": 6, "table_number": 1}]  # Fallback for demo

# FAQ Page
if page == "FAQ":
    st.header("FAQ")
    query = st.text_input("Ask a question (e.g., 'What vegan dishes do you have?')")
    if st.button("Submit Query"):
        with st.spinner("Processing..."):
            try:
                response = send_faq_query(API_BASE, query)
                st.success(response["response"])
                logger.info(f"FAQ query: {query}, Response: {response['response']}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"FAQ query failed: {str(e)}")
# Orders Page
elif page == "Orders":
    st.header("Manage Orders")
    tab1, tab2 = st.tabs(["Create Order", "Update Order Status"])
    with tab1:
        tables = get_available_tables()
        table_options = {f"Table {t['table_number']} (ID: {t['id']})": t['id'] for t in tables}
        table_selection = st.selectbox("Select Table", list(table_options.keys()))
        table_id = table_options[table_selection]
        st.write("Enter items as JSON (e.g., [{'menu_id': 1, 'quantity': 2}])")
        items_input = st.text_area("Items", value='[{"menu_id": 1, "quantity": 2}]', key="create_order_items_1")
        if st.button("Create Order"):
            with st.spinner("Creating order..."):
                try:
                    import json
                    items_json = json.loads(items_input.strip())
                    logger.info(f"Parsed items JSON: {items_json}")
                    if not isinstance(items_json, list):
                        raise ValueError("Items must be a list of dictionaries")
                    # Convert to OrderItem list
                    from pydantic import BaseModel
                    class OrderItem(BaseModel):
                        menu_id: int
                        quantity: int
                    test_items = [OrderItem(**item) for item in items_json]  # Create Pydantic objects
                    logger.info(f"Hardcoded test payload: {test_items}")
                    response = create_order(API_BASE, table_id, test_items)  # Use Pydantic objects
                    logger.info(f"API response: {response}")
                    st.success(f"Order {response['order_id']} created with status {response['status']}")
                    logger.info(f"Order created: {response}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format. Use: [{'menu_id': 1, 'quantity': 2}]")
                    logger.error("Order creation failed: Invalid JSON format")
                except ValueError as ve:
                    st.error(f"Invalid input: {str(ve)}")
                    logger.error(f"Order creation failed: {str(ve)}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Order creation failed: {str(e)}")

    with tab2:
        order_id = st.number_input("Order ID", min_value=1, step=1)
        new_status = st.selectbox("New Status", ["pending", "preparing", "served", "paid"])
        if st.button("Update Status"):
            with st.spinner("Updating status..."):
                try:
                    response = update_order_status(API_BASE, order_id, new_status)
                    logger.info(f"API response: {response}")  # Add this
                    st.success(f"Order {response['order_id']} updated to {response['status']}")
                    logger.info(f"Order status updated: {response}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Order update failed: {str(e)}")

# Vision Page
elif page == "Vision":
    st.header("Table Status Detection")
    uploaded_file = st.file_uploader("Upload Table Image", type=["jpg", "png"])
    if uploaded_file and st.button("Detect Status"):
        with st.spinner("Detecting table status..."):
            try:
                response = upload_vision_image(API_BASE, uploaded_file)
                st.success(f"Table {response['table_id']}: {response['status']} (Confidence: {response['confidence']})")
                logger.info(f"Vision detection: {response}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Vision detection failed: {str(e)}")

# Recommendations Page
elif page == "Recommendations":
    st.header("Upsell Recommendations")
    order_id = st.number_input("Order ID", min_value=1, step=1)
    if st.button("Get Suggestions"):
        with st.spinner("Fetching recommendations..."):
            try:
                response = get_recommendations(API_BASE, order_id)
                if response["suggestions"]:
                    st.write("Suggested Items:")
                    for item in response["suggestions"]:
                        st.markdown(f"- Item ID {item['item_id']} (Confidence: {item['uplift']:.2f})")
                else:
                    st.info("No suggestions available.")
                logger.info(f"Recommendations for order {order_id}: {response}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Recommendations failed: {str(e)}")

# Analytics Page
elif page == "Analytics":
    st.header("Restaurant Analytics")
    date = st.date_input("Select Date", value=datetime.now())
    range_type = st.selectbox("Range", ["daily", "weekly"])
    if st.button("Fetch KPIs"):
        with st.spinner("Loading analytics..."):
            try:
                response = get_analytics(API_BASE, date.strftime("%Y-%m-%d"), range_type)
                st.subheader("KPIs")
                st.markdown(f"- **Total Orders**: {response['total_orders']}")
                st.markdown(f"- **Total Revenue**: ${response['total_revenue']:.2f}")
                st.markdown(f"- **Average Ticket Size**: ${response['avg_ticket_size']:.2f}")
                st.subheader("Top Items")
                for item in response["top_items"]:
                    st.markdown(f"- {item['name']} (Menu ID: {item['menu_id']}, Quantity: {item['quantity']})")
                logger.info(f"Analytics fetched: {response}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Analytics fetch failed: {str(e)}")

# Office Page (Mock)
elif page == "Office":
    st.header("Office Tasks")
    st.subheader("Pending Tasks (Mock)")
    tasks = [
        {"task": "Renew liquor license", "due": "2025-09-01"},
        {"task": "Confirm large party reservation for 15 guests", "due": "2025-08-25"}
    ]
    for task in tasks:
        st.markdown(f"- {task['task']} (Due: {task['due']})")
    logger.info("Displayed mock office tasks")