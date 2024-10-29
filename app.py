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
            model="claude-3-sonnet-20240307",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4096,
            temperature=0.7
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error getting response from Claude 3.5 Sonnet: {str(e)}")
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
    [This section should provide a clear, concise overview of the entire BATNA analysis. Focus on key findings, critical recommendations, and immediate action items. Write this in a way that executives can quickly grasp the situation and make informed decisions.]

    2. CLIENT'S BATNA ANALYSIS
    [This section requires a detailed examination of our position, focusing on all possible alternatives and their implications. Present this information in a clear table format that allows for quick comparison and understanding.]
    Present this as a table with three columns:
    | Alternatives Analysis | Strength Assessment | Weakness Evaluation |

    3. VENDOR'S BATNA ANALYSIS
    [This section should analyze the vendor's position with the same rigor as our own analysis. Consider their alternatives, strengths, and weaknesses from their perspective.]
    Present this as a table with three columns:
    | Alternative Options | Strength Areas | Weakness Areas |

    4. RISK ASSESSMENT & MITIGATION
    [This section should provide a comprehensive analysis of potential risks and corresponding mitigation strategies. It should demonstrate thorough consideration of all possible scenarios.]
    Present this as a table with three columns:
    | Risk Category | Mitigation Strategy | Contingency Plan |

    5. NEGOTIATION STRATEGY
    [This section should outline our comprehensive approach to the negotiation, detailing how we plan to achieve our objectives while maintaining positive relationships.]

    6. NEGOTIATION TACTICS
    [This section should provide specific, actionable guidance on how to execute the negotiation strategy, including detailed response scenarios and timing considerations.]

    7. RECOMMENDATIONS
    [This section should synthesize the entire analysis into clear, actionable recommendations with supporting rationale.]


    Please ensure:
    1. Each section provides deep and comprehensive analysis supported by the provided information
    2. Information flows logically between sections
    3. All recommendations are practical and actionable
    4. Both short-term and long-term implications are addressed
    5. The document maintains a professional, clear writing style
    6. Tables are used only where specified
    7. Bullet points are used only for clear step-by-step processes
    8. Each section begins with an introduction paragraph

    Format your response with:
    - Clear bold section headings
    - Professional paragraph structure
    - Tables where specified
    - Numbered sequences where appropriate
    - Consistent formatting throughout
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
