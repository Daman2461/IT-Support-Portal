import streamlit as st
import requests

st.set_page_config(page_title="SupportOpsAgent Demo", page_icon="🤖")
st.title("SupportOpsAgent: LLM-Powered Support Automation")

st.markdown("""
Enter a customer support message and user ID. The agent will classify the intent, retrieve policy context, and take action.
""")

with st.form("support_form"):
    user_input = st.text_area("Customer Message", "I want a refund for my damaged item")
    user_id = st.number_input("User ID", min_value=1, value=1)
    submitted = st.form_submit_button("Submit")

if submitted:
    with st.spinner("Processing..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/support/resolve",
                json={"user_input": user_input, "user_id": user_id},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                st.success(f"**Intent:** {result['intent']}")
                st.json(result["action_result"])
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

st.markdown("---")
st.markdown("[View API docs](http://127.0.0.1:8000/docs)") 