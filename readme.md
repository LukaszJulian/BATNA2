BATNA Document Creation Assistant A Streamlit web application that helps procurement professionals prepare for negotiations by creating comprehensive BATNA (Best Alternative To a Negotiated Agreement) documents using Anthropic's Claude 3.5 AI model. Features

Step-by-step guided input collection AI-powered BATNA document generation Professional document formatting Export options for final documents Progress tracking Session state management

Installation

Clone this repository:

bashCopygit clone https://github.com/yourusername/batna-assistant.git cd batna-assistant

Install the required packages:

bashCopypip install -r requirements.txt

Set up your environment:

Create a .streamlit/secrets.toml file in your project directory Add your Anthropic API key: tomlCopyANTHROPIC_API_KEY = "your-api-key-here"

Run the application:

bashCopystreamlit run app.py Usage

Launch the application Fill in each section of the BATNA document with relevant information:

Negotiation Subject Project Value Company Profile & Industry Scope Description Targets Vendors & Suppliers Interests Advantages Disadvantages

Review and generate the final BATNA document Export the document in your preferred format

Requirements

Python 3.8+ Streamlit Anthropic API access Internet connection

Security Note Never commit your .streamlit/secrets.toml file or expose your API keys. The .gitignore file is configured to exclude this file. License MIT License Contributing Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
