import streamlit as st
import anthropic
from datetime import datetime
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Page configuration
st.set_page_config(
    page_title="BATNA Document Creator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def initialize_session_state():
    if 'collected_data' not in st.session_state:
        st.session_state.collected_data = {}
    if 'final_document' not in st.session_state:
        st.session_state.final_document = None
    if 'show_document' not in st.session_state:
        st.session_state.show_document = False
    if 'document_history' not in st.session_state:
        st.session_state.document_history = []

def save_to_history(document, data):
    """Save generated document to history with timestamp"""
    # Keep only the 10 most recent documents
    if len(st.session_state.document_history) >= 10:
        st.session_state.document_history.pop(0)  # Remove oldest document
        
    history_entry = {
        'timestamp': datetime.now(),
        'document': document,
        'metadata': {
            'subject': data.get('negotiation_subject', 'Untitled'),
            'value': data.get('project_value', 'N/A'),
            'data': data.copy()
        }
    }
    st.session_state.document_history.append(history_entry)

def render_sidebar_history():
    with st.sidebar:
        st.title("Recent Documents")
        
        if not st.session_state.document_history:
            st.info("No documents generated yet")
            return

        # Display documents from newest to oldest
        for idx, entry in enumerate(reversed(st.session_state.document_history)):
            with st.expander(
                f"📄 {entry['metadata']['subject'][:40]}... \n"
                f"{entry['timestamp'].strftime('%Y-%m-%d %H:%M')}"
            ):
                st.write(f"**Project Value:** {entry['metadata']['value']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View", key=f"view_{idx}", use_container_width=True):
                        st.session_state.final_document = entry['document']
                        st.session_state.collected_data = entry['metadata']['data']
                        st.session_state.show_document = True
                        st.rerun()
                
                with col2:
                    if st.button("Delete", key=f"delete_{idx}", use_container_width=True):
                        st.session_state.document_history.remove(entry)
                        st.rerun()
        
        if st.session_state.document_history:
            if st.button("Clear History", use_container_width=True):
                st.session_state.document_history = []
                st.rerun()

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
            model="claude-3-opus-20240229",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4096,
            temperature=0.7
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error getting response from Claude 3 Opus: {str(e)}")
        st.write("Detailed error:", str(e))
        return None

# Simple and reliable PDF generator
def generate_pdf(content, filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("BATNA Analysis Document", title_style))
    story.append(Spacer(1, 12))
    
    # Process content
    try:
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                if paragraph.startswith('#') or any(paragraph.startswith(str(i)) for i in range(1, 9)):
                    # Heading style
                    story.append(Paragraph(paragraph, styles['Heading1']))
                    story.append(Spacer(1, 12))
                else:
                    # Normal text style
                    story.append(Paragraph(paragraph, styles['Normal']))
                    story.append(Spacer(1, 6))
    except Exception as e:
        st.error(f"Error processing content for PDF: {str(e)}")
        return None
    
    try:
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    except Exception as e:
        st.error(f"Error building PDF: {str(e)}")
        return None

def generate_batna_document():
    client = init_client()
    if not client:
        return

    prompt = """Create a comprehensive BATNA document based on the following information:

    {input_data}

    Please elaborate detailed and comprehensive answers to the below structured block and points after a very deep and thorough analysis of different scenarios has been carried out by you. If other points should be added within the blocks, please do so with a brief explanation of why:

    1. EXECUTIVE SUMMARY
    [This section should provide a concise yet comprehensive overview of the entire analysis, key findings, and critical recommendations.]

    2. CLIENT'S BATNA ANALYSIS
    | Alternative Options | Strength Assessment | Risk Assessment |
    Present a detailed analysis of each viable alternative, including implementation feasibility, cost implications, and strategic fit.

    3. VENDOR'S BATNA ANALYSIS
    | Market Position | Vendor Capabilities | Constraints Analysis |
    Analyze the vendor's alternatives, market position, and potential responses to different scenarios.

    4. RISK ASSESSMENT & MITIGATION
    | Risk Category | Mitigation Strategy | Contingency Plan |
    Provide a comprehensive analysis of potential risks and detailed mitigation strategies.

    5. NEGOTIATION STRATEGY
    Present a detailed strategic approach covering:
    - Core objectives and non-negotiables
    - Value creation opportunities
    - Power dynamics and leverage points
    - Relationship management approach

    6. NEGOTIATION TACTICS
    Detail specific tactical recommendations including:
    - Opening positions
    - Communication strategies
    - Response scenarios
    - Timing considerations

    7. IMPLEMENTATION ROADMAP
    Outline a clear implementation plan with:
    - Key milestones and timelines
    - Resource requirements
    - Success metrics
    - Review points

    8. RECOMMENDATIONS
    Provide clear, actionable recommendations with:
    - Immediate next steps
    - Critical success factors
    - Resource requirements
    - Expected outcomes

    Format the response professionally, using clear headings and maintaining a structured, business-appropriate tone throughout."""
    
    formatted_data = "\n\n".join([f"{k.replace('_', ' ').title()}: {v}" 
                                 for k, v in st.session_state.collected_data.items()])
    
    with st.spinner("Generating BATNA document..."):
        response = get_assistant_response(client, prompt.format(input_data=formatted_data))
        if response:
            st.session_state.final_document = response
            save_to_history(response, st.session_state.collected_data)
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
                value = st.text_area(
                    "Enter information:",
                    value=st.session_state.collected_data.get(key, ""),
                    height=150,
                    key=f"input_{key}",
                    label_visibility="collapsed"
                )
                
                if not value.strip():
                    all_fields_filled = False
                st.markdown("---")
        
        # Second column
        with col2:
            for key, title in sections_list[mid_point:]:
                st.subheader(title)
                value = st.text_area(
                    "Enter information:",
                    value=st.session_state.collected_data.get(key, ""),
                    height=150,
                    key=f"input_{key}",
                    label_visibility="collapsed"
                )
                
                if not value.strip():
                    all_fields_filled = False
                st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button("Generate BATNA Document", use_container_width=True)
        if submitted:
            if all_fields_filled:
                for key in sections.keys():
                    st.session_state.collected_data[key] = st.session_state[f"input_{key}"]
                generate_batna_document()
            else:
                st.error("Please fill in all fields before generating the BATNA document.")

def main():
    st.title("🤝 BATNA Document Creation Assistant")
    
    # Professional description
    st.markdown("""
        <div style='background-color: #EBF5FB; padding: 1rem; border-radius: 10px; border-left: 5px solid #2E86C1; margin-bottom: 2rem;'>
            <p style='color: #2E86C1; font-size: 1.1em; margin-bottom: 0.5rem;'><strong>Professional BATNA Document Generator</strong></p>
            <p style='font-size: 0.95em; color: #34495E; line-height: 1.5;'>
                Leverage advanced AI to create detailed Best Alternative To a Negotiated Agreement (BATNA) documents. 
                Our assistant helps procurement professionals analyze negotiation positions, assess risks, 
                and develop strategic alternatives for successful negotiations.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
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
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Create New Document", use_container_width=True):
                    st.session_state.collected_data = {}
                    st.session_state.show_document = False
                    st.rerun()
            
            with col2:
                if st.download_button(
                    label="Download as PDF",
                    data=generate_pdf(st.session_state.final_document, "BATNA_document.pdf"),
                    file_name=f"BATNA_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                ):
                    st.success("PDF downloaded successfully!")

if __name__ == "__main__":
    main()
