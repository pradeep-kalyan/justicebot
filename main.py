import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import PromptTemplate
import pandas as pd
import logging
import datetime

# Initialize logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize language model
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.9,
    max_retries=2,
    api_key="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",
)


# Function to load content from a webpage
def load_web_content(url):
    try:
        loader = WebBaseLoader(url)
        return loader.load().pop().page_content
    except Exception as e:
        logging.error(f"Error loading content from {url}: {e}")
        return ""


# Function to scrape DOJ websites
def scrape():
    outputs = []
    websites = [
        "https://doj.gov.in/",
        "https://njdg.ecourts.gov.in/njdg_v3/",
        "https://doj.gov.in/supreme-court-3/",
        "https://dashboard.doj.gov.in/vacancy-position/",
        "https://njdg.ecourts.gov.in/hcnjdg_v2/",
    ]
    for webpage in websites:
        output = load_web_content(webpage)
        outputs.append(output)
    return outputs


# Load CSV data
def load_csv_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.to_dict(orient="records")
    except Exception as e:
        logging.error(f"Error loading CSV from {file_path}: {e}")
        return []


# Scrape + CSV data
def scrape_and_load_csv():
    scraped_data = scrape()
    csv_data = load_csv_data("hello.csv")
    return scraped_data, csv_data


# Create prompt template with CSV data
def create_prompt_template_with_csv(output, output1, output2, csv_data, user_in):
    csv_content = "\n".join([str(item) for item in csv_data])
    return PromptTemplate.from_template(
        f"""
        ### Scraped text from websites:
        {output}, {output1}, {output2}
        
        ### CSV Data:
        {csv_content}

        ###
        Instruction:
        Analyze the user's input to understand their needs and context.
        Generate responses based on the information retrieved from both scraped text and CSV data.
        You are a bot working for the DOJ website.
        Your task is to answer questions asked by {{user_in}} based on the provided data.
        Ensure the answers are concise, clear, and easy to understand.
        """
    )


# Process user query and return response
def hello(user_in):
    output, csv_data = scrape_and_load_csv()
    prompt = create_prompt_template_with_csv(
        output[0], output[1], output[2], csv_data, user_in
    )
    prompt_in = prompt | llm
    data = prompt_in.invoke(
        input={
            "output": output[0],
            "output1": output[1],
            "output2": output[2],
            "user_in": user_in,
        }
    )
    response = data.content
    return response


# Streamlit application UI setup
st.set_page_config(
    page_title="DOJ Information Assistant",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Check if dark mode state exists, else initialize it
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# Sidebar with theme toggle and FAQ section
with st.sidebar:
    st.title("🛡️ DOJ Info Assistant")
    st.session_state["dark_mode"] = st.checkbox(
        "🌗 Toggle Dark Mode", value=st.session_state["dark_mode"]
    )

    st.markdown("## ℹ️ FAQ")
    with st.expander("View Frequently Asked Questions"):
        st.write(
            """
        **What can I ask?**
        - Questions about DOJ vacancies, Supreme Court cases, etc.

        **How accurate is the information?**
        - Data is sourced directly from DOJ websites.

        **Example Queries:**
        - "Recent Supreme Court rulings."
        - "DOJ job vacancies in 2024."
        """
        )

# Apply dark mode styling if enabled
if st.session_state["dark_mode"]:
    st.markdown(
        """
        <style>
            /* Dark mode styling */
            .css-18e3th9, .css-1d391kg { background-color: #0e1117; color: #f5f5f5; }
            .css-1v0mbdj { color: #f5f5f5; }
            .css-18ni7ap h1 { color: #f5f5f5; }
            .css-15zrgzn { color: #a1a1a1; }
            .css-15tx938 { background-color: #2c2f36; color: #f5f5f5; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Header and Welcome Message
st.title("⚖️ DOJ Information Query Assistant")
st.write(
    "Welcome to the DOJ Bot! Ask questions about DOJ-related topics and get answers quickly."
)

# Tabs for Recent Queries, Query Submission, and FAQ
tab1, tab2, tab3, tab4 = st.tabs(
    ["Ask a Question", "Recent Queries", "FAQ", "Settings"]
)

with tab1:
    st.markdown("### 🔍 Enter Your Question")
    user_input = st.text_input(
        "Type your question here:",
        placeholder="e.g., 'What are the current vacancies in DOJ?'",
    )
    if st.button("Submit Query", key="submit_query"):
        if user_input:
            with st.spinner("Fetching and analyzing information..."):
                response = hello(user_input)
                if response:
                    st.success("✅ Here is the answer:")
                    st.write(response)
                    query_log = {
                        "question": user_input,
                        "response": response,
                        "time": datetime.datetime.now(),
                    }
                    st.session_state["recent_queries"] = st.session_state.get(
                        "recent_queries", []
                    ) + [query_log]
                else:
                    st.error(
                        "❌ Unable to find an answer. Please try a different question."
                    )
        else:
            st.warning("Please enter a question first!")

# Display recent queries
with tab2:
    st.markdown("### 📝 Recent Queries")
    if "recent_queries" in st.session_state and st.session_state["recent_queries"]:
        for query_log in reversed(st.session_state["recent_queries"]):
            st.write(
                f"- **{query_log['question']}** \n\t_Response:_ {query_log['response']}"
            )
    else:
        st.write("No recent queries yet. Your queries will appear here once submitted.")

# FAQ Section in Tab
with tab3:
    st.markdown("### 📋 Frequently Asked Questions")
    st.write(
        """
    **What types of queries can I ask?**
    - DOJ vacancies, Supreme Court cases, government reports, and more.

    **How is the data gathered?**
    - Data is sourced in real-time from DOJ websites.
    """
    )
    st.write("For more questions, please refer to the sidebar FAQ.")

# Settings Tab for additional features
with tab4:
    st.markdown("### ⚙️ Settings")
    export_csv = st.button("Export Recent Queries as CSV")
    if export_csv:
        recent_queries = pd.DataFrame(st.session_state["recent_queries"])
        recent_queries.to_csv("recent_queries.csv", index=False)
        st.write("✅ Recent queries exported as CSV.")

# Footer with additional styling
st.markdown("---")
st.write("🤖 Made with ❤️ by Code 2 Change")

# Add custom CSS for button animations
st.markdown(
    """
    <style>
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
