CUSTOM_CSS = """
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2E86C1;
        --secondary-color: #AED6F1;
        --background-color: #F8F9F9;
        --text-color: #21618C;
    }

    /* Header styling */
    .stApp header {
        background-color: var(--primary-color) !important;
        color: white !important;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8F9F9;
    }

    section[data-testid="stSidebar"] > div {
        background-color: #EBF5FB;
        padding: 1rem;
    }

    section[data-testid="stSidebar"] .st-expander {
        background-color: white;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    /* Form styling */
    div[data-testid="stForm"] {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Button styling */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        background-color: #21618C;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Info boxes styling */
    .stAlert {
        background-color: #D4E6F1;
        color: #21618C;
        border: 1px solid #AED6F1;
        border-radius: 5px;
    }

    /* Text area styling */
    .stTextArea textarea {
        border: 1px solid #AED6F1;
        border-radius: 5px;
    }

    .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(46,134,193,0.2);
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--text-color);
    }

    /* Document history items */
    .document-history-item {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid var(--primary-color);
        margin-bottom: 0.5rem;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: var(--primary-color);
    }

    /* Download buttons */
    .download-button {
        background-color: #2E86C1;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem 0;
    }

    /* Custom container for the main content */
    .main-content {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    /* Title container */
    .title-container {
        background-color: #2E86C1;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .title-container h1 {
        color: white;
        margin: 0;
    }

    /* Sidebar title */
    .sidebar-title {
        background-color: #2E86C1;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        color: white;
    }
</style>
"""
