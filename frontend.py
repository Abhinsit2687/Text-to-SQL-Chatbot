# =========================
# STREAMLIT FRONTEND
# =========================

import streamlit as st
from main import ask_database


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Data Analyst 2.0",
    page_icon="🤖",
    layout="centered"
)


# =========================
# TITLE
# =========================
st.title("🤖 AI Data Analyst 2.0")

st.markdown(
    "Ask questions about your database using natural language."
)


# =========================
# USER INPUT
# =========================
user_query = st.text_area(
    "💬 Enter your question:",
    placeholder="e.g. Show top 5 most expensive products"
)


# =========================
# BUTTON
# =========================
if st.button("Analyze"):

    if user_query.strip() == "":

        st.warning("Please enter a question.")

    else:

        with st.spinner("Analyzing your query using Gemini..."):

            output = ask_database(user_query)

        st.success("Analysis Complete ✅")


        # =========================
        # SHOW RESULT
        # =========================
        if "error" in output:

            st.error(output["error"])

        else:

            # Show columns
            st.subheader("📌 Columns")

            st.write(output["columns"])


            # Show data
            st.subheader("📊 Query Results")

            st.dataframe(output["results"])


# =========================
# CUSTOM CSS
# =========================
st.markdown(
    """
    <style>

    textarea {
        font-size: 16px !important;
    }

    .stDataFrame {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)