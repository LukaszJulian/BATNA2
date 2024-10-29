import streamlit as st
import anthropic
from datetime import datetime
from style import CUSTOM_CSS
import io
from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page configuration
st.set_page_config(
    page_title="BATNA Document Creator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS once at the start
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'collected_data' not in st.session_state:
        st.session_state.collected_data = {}
    if 'final_document' not in st.session_state:
        st.session_state.final_document = None
    if 'show_document' not in st.session_state:
        st.session_state.show_document = False
    if 'document_history' not in st.session_state:
        st.session_state.document_history = []  # List of tuples (timestamp, document, metadata)

# Initialize the Anthropic client
def init_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        if not api_key:
            st.error("API key not found in secrets.")
            st.stop()
            return None
            
        client = anthropic.Anthropic(api_key=api_key)
        return client
    except KeyError:
        st.error("'ANTHROPIC_API_KEY' not found in Streamlit secrets. Please check your secrets configuration.")
        st.stop()
        return None
    except Exception as e:
        st.error(f"Failed to initialize Anthropic client. Error: {str(e)}")
        st.stop()
        return None

def get_assistant_response(client, prompt):
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4096,
            temperature=0.7
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error getting response from Claude 3 Sonnet: {str(e)}")
        st.write("Detailed error:", str(e))
        return None

def generate_pdf(content, filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []
    
    # Create custom style for headers
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        spaceAfter=30,
        fontSize=16
    )
    
    # Split content into sections and format
    sections = content.split('\n\n')
    for section in sections:
        if section.strip():
            if section.startswith('#') or any(section.startswith(str(i)) for i in range(1, 8)):
                # Headers
                p = Paragraph(section, header_style)
            else:
                # Regular text
                p = Paragraph(section, styles["Normal"])
            flowables.append(p)
            flowables.append(Spacer(1, 12))
    
    doc.build(flowables)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_word(content, filename):
    doc = Document()
    doc.add_heading('BATNA Document', 0)
    
    # Split content into sections and format
    sections = content.split('\n\n')
    for section in sections:
        if section.strip():
            if section.startswith('#') or any(section.startswith(str(i)) for i in range(1, 8)):
                # Headers
                doc.add_heading(section, level=1)
            else:
                # Regular text
                doc.add_paragraph(section)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    doc_bytes = buffer.getvalue()
    buffer.close()
    return doc_bytes

def render_sidebar_history():
    with st.sidebar:
        st.title("Document History")
        if not st.session_state.document_history:
            st.info("No documents generated yet")
        else:
            for idx, (timestamp, doc, metadata) in enumerate(st.session_state.document_history[::-1]):
                with st.expander(f"📄 {metadata['negotiation_subject']} - {timestamp.strftime('%Y-%m-%d %H:%M')}"):
                    st.write(f"**Subject:** {metadata['negotiation_subject']}")
                    st.write(f"**Project Value:** {metadata['project_value']}")
                    if st.button("View", key=f"view_{idx}"):
                        st.session_state.final_document = doc
                        st.session_state.collected_data = metadata
                        st.session_state.show_document = True
                        st.rerun()

def generate_batna_document():
    client = init_client()
    if not client:
        return

    prompt = """As an expert in procurement negotiations and BATNA analysis, create a comprehensive and strategic BATNA document based on the following information:

    {input_data}

    Carry out a very detailed and in-depth analysis based on user input. Then create very detailed and comprehensive answers according to the structure below:

    1. EXECUTIVE SUMMARY
       - High-level overview of key findings
       - Strategic imperatives

    2. CLIENT'S BATNA ANALYSIS
       A. Primary Alternatives
       B. Strengths Assessment       
       C. Weaknesses Evaluation

    3. VENDOR'S BATNA ANALYSIS
       A. Likely Alternatives       
       B. Vendor Strengths    
       C. Vendor Weaknesses

    4. RISK ASSESSMENT & MITIGATION
       A. Strategic Risks    
       B. Mitigation Strategies       
       C. Contingency Planning

    5. NEGOTIATION STRATEGY
       A. Strategic Framework
          - Core objectives
          - Non-negotiables
          - Flexibility points
          - Success criteria

    6. NEGOTIATION TACTICS
       A. Communication Strategy
          - Key messages
          - Timing considerations
          - Channel selection
          - Stakeholder management
       
       B. Response Scenarios
          - Best case responses
          - Worst case responses
          - Counter-proposals
          - Escalation protocols
       
       C. Timing Considerations
          - Critical milestones
          - Decision points
          - Market timing
          - Pressure points

    7. RECOMMENDATIONS
       A. Strategic Priorities
          - Immediate actions
          - Medium-term initiatives
          - Long-term considerations
       
       B. Critical Success Factors
          - Key enablers
          - Risk factors
          - Dependencies
          - Support requirements

    Please ensure:
    - Each section contains detailed analysis supported by the provided information
    - Practical and actionable recommendations are included
    - Clear linkages between different sections are established
    - Specific examples and scenarios are provided where relevant
    - Quantitative and qualitative aspects are addressed
    - Both short-term and long-term implications are considered

    Format your response with:
    - Clear bold headings and subheadings
    - Formulated text with bullet points for key information where sensible
    - Use table format where it makes sense, e.g. points 2,3 and 4
    - Numbered lists for sequential steps
    - Bold and cursive text for critical points
    - Professional and concise language
    """
    
    formatted_data = "\n\n".join([f"{k.replace('_', ' ').title()}: {v}" 
                                 for k, v in st.session_state.collected_data.items()])
    
    with st.spinner("Generating comprehensive BATNA document using Claude 3.5..."):
        response = get_assistant_response(client, prompt.format(input_data=formatted_data))
        if response:
            st.session_state.final_document = response
            st.session_state.show_document = True
            st.rerun()

def render_input_form():
    sections = {
        "negotiation_subject": "Negotiation Subject",
        "project_value": "Project Value",
        "company_profile": "Company's Profile & Industry",
        "scope_description": "Scope Description",
        "targets": "Targets to be Achieved",
        "vendors": "Vendors & Suppliers to be Invited",
        "interests": "Client's Interests & Vendor's Interests",
        "advantages": "Client's Negotiation Advantages & Vendors' Negotiation Advantages",
        "disadvantages": "Client's Negotiation Disadvantages & Vendors' Negotiation Disadvantages"
    }
    
    help_texts = {
        "negotiation_subject": "What is the main topic or subject of the negotiation?",
        "project_value": "What is the estimated financial value of the project?",
        "company_profile": "Brief description of your company and industry context",
        "scope_description": "Detailed description of what is being negotiated",
        "targets": "What specific goals do you want to achieve?",
        "vendors": "List of potential suppliers/vendors to negotiate with",
        "interests": "What are the key interests of both parties?",
        "advantages": "What advantages does each party bring to the negotiation?",
        "disadvantages": "What are the weaknesses or challenges for each party?"
    }

    # Compact header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### BATNA Input Form")
    with col2:
        if st.button("Clear All Fields", use_container_width=True):
            st.session_state.collected_data = {}
            st.rerun()

    # Create form for all inputs
    with st.form("batna_form"):
        # Create two columns for inputs
        col1, col2 = st.columns(2)
        
        # Split sections between columns
        sections_list = list(sections.items())
        mid_point = len(sections_list) // 2 + len(sections_list) % 2
        
        all_fields_filled = True
        
        # First column
        with col1:
            for key, title in sections_list[:mid_point]:
                st.subheader(title)
                if key in help_texts:
                    st.info(help_texts[key])
                
                value = st.text_area(
                    "Enter information:",
                    value=st.session_state.collected_data.get(key, ""),
                    height=80,
                    key=f"input_{key}",
                    label_visibility="collapsed"
                )
                
                if not value.strip():
                    all_fields_filled = False
        
        # Second column
        with col2:
            for key, title in sections_list[mid_point:]:
                st.subheader(title)
                if key in help_texts:
                    st.info(help_texts[key])
                
                value = st.text_area(
                    "Enter information:",
                    value=st.session_state.collected_data.get(key, ""),
                    height=80,
                    key=f"input_{key}",
                    label_visibility="collapsed"
                )
                
                if not value.strip():
                    all_fields_filled = False
        
        # Submit button
        submitted = st.form_submit_button("Generate BATNA Document", use_container_width=True)
        if submitted:
            if all_fields_filled:
                # Save all inputs
                for key in sections.keys():
                    st.session_state.collected_data[key] = st.session_state[f"input_{key}"]
                generate_batna_document()
            else:
                st.error("Please fill in all fields before generating the BATNA document.")

def main():
    st.title("BATNA Assistant")
    st.markdown("---")
    
    initialize_session_state()
    render_sidebar_history()
    
    if not st.session_state.show_document:
        render_input_form()
    else:
        # Display generated document
        st.header("📄 Generated BATNA Document")
        st.markdown("---")
        
        if st.session_state.final_document:
            # Add expander to show input data
            with st.expander("View Input Data", expanded=False):
                for key, value in st.session_state.collected_data.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    st.markdown(f"{value}")
                    st.markdown("---")
            
            st.markdown(st.session_state.final_document)
            
            # Export options
            st.markdown("---")
            st.subheader("Export Options")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Create New Document", use_container_width=True):
                    # Clear all input fields
                    st.session_state.collected_data = {}
                    st.session_state.show_document = False
                    st.rerun()
            
            with col2:
                st.download_button(
                    label="Download as Text",
                    data=st.session_state.final_document,
                    file_name=f"BATNA_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                pdf_data = generate_pdf(st.session_state.final_document, "BATNA_document.pdf")
                st.download_button(
                    label="Download as PDF",
                    data=pdf_data,
                    file_name=f"BATNA_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col4:
                word_data = generate_word(st.session_state.final_document, "BATNA_document.docx")
                st.download_button(
                    label="Download as Word",
                    data=word_data,
                    file_name=f"BATNA_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
