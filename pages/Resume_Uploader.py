## This app version contain extraction of Resume, SOP and Reference letter and store into database
## add Name, 

import streamlit as st
import pandas as pd
import PyPDF2
import os
from groq import Groq
import re
from sqlalchemy import create_engine
import urllib.parse

# Set Streamlit page configuration
st.set_page_config(page_icon="📄", page_title="Upload your Resume for future opportunity")

# Hide Streamlit's default style elements for a cleaner UI
hide_streamlit_style = """
    <style>
    #GithubIcon {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {overflow: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize Groq client with API key from Streamlit secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("GROQ_API_KEY not found in Streamlit secrets. Please add it to proceed.")
    st.stop()

# Define the system message tailored for resume extraction
system_message_resume = """
You are an advanced AI assistant specializing in extracting and structuring information from resumes. Your primary function is to analyze resume content, regardless of format or layout, and extract key information with high accuracy.

Key Responsibilities:
1. Education: Extract degrees, institutions, graduation dates, and relevant coursework.
2. Experience: Capture job titles, company names, employment dates, and key responsibilities or achievements.
3. Skills: Identify both technical and soft skills listed.
4. Projects: Extract project titles, descriptions, technologies used, and roles.
5. Extra-Curricular: Note any additional activities, leadership roles, certifications, or awards.
6. Name: Person Name, first Name, Last Name
7. Email id: Email of person

Handling Variations:
- Recognize and correctly interpret different terminologies and formats.
- Adapt to various date formats and structures.
- Handle resumes with varying levels of detail and completeness.

Output Format:
Present all extracted information with clear section labels. Use the following specific section headers in your output:

- **Education**
- **Experience**
- **Skills**
- **Projects**
- **Extra-Curricular**
- **Name**
- **Email id**

For each section, provide detailed information as lists where applicable. If a particular section is not present in the resume, indicate it as "N/A".

Quality Assurance:
1. Verify that all available information has been captured.
2. Ensure the structure is consistent and properly formatted.
3. Double-check dates and titles for accuracy.
4. Confirm that entity names and details are correctly associated.

Error Handling:
If you encounter ambiguous or unclear information, provide your best interpretation and note any uncertainties in a separate "Notes" section.

Remember, your goal is to provide a comprehensive, accurate, and consistently structured representation of the resume's content, regardless of its original format or layout. Always use the specified section headers in your output.
"""

# Define the system message tailored for SOP and Reference letters
system_message_sop_reference = """
You are an advanced AI assistant specializing in analyzing SOPs and Reference letters. Your primary function is to summarize the key motivations and endorsements in the content provided.

For SOPs, focus on the student's motivation for pursuing their course of study. Provide a concise summary of the key points and aspirations mentioned in the SOP.

For Reference letters, summarize the key endorsements and characteristics of the candidate as highlighted by the referee. Focus on the most significant qualities, achievements, and recommendations mentioned.

Output Format:
- For SOPs, provide a summary of motivations without any specific headings.
- For Reference letters, summarize key endorsements without any specific headings.

Your summary should be comprehensive yet concise, capturing the essence of the document in a few paragraphs.
"""

# Function to extract text from PDF using PyPDF2
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text + "\n"
    return text

# Function to create the prompt for the Groq API
def create_prompt(pdf_text, type="resume"):
    if type == "resume":
        prompt = f"""
Please analyze the following resume content and extract all relevant information according to the detailed guidelines provided. Your task is to:

1. Extract Education details including degrees, institutions, graduation dates, and relevant coursework.
2. Capture Experience details including job titles, company names, employment dates, and key responsibilities or achievements.
3. Identify Skills, both technical and soft.
4. Extract Projects including project titles, descriptions, technologies used, and roles.
5. Note any Extra-Curricular activities, leadership roles, certifications, or awards.

Present your findings with clear section labels as specified below. Use the following section headers in your output:

- **Education**
- **Experience**
- **Skills**
- **Projects**
- **Extra-Curricular**
- **Name**
- **Email id**
- **Notes** (if any)

If a particular section is not present in the resume, indicate it as "N/A".

Here's the resume content to analyze:

{pdf_text}

Please provide a thorough and accurate extraction of this resume's content, handling any variations in terminology or layout as needed, and strictly adhering to the specified section headers.
"""
    elif type == "sop":
        prompt = f"""
Please analyze the following Statement of Purpose (SOP) content and provide a concise summary of the student's motivation for pursuing their course of study. Extract and present the key reasons, aspirations, and goals mentioned in the SOP.

Here's the SOP content to analyze:

{pdf_text}

Provide a comprehensive yet concise summary capturing the essence of the student's motivations and goals.
"""
    elif type == "reference":
        prompt = f"""
Please analyze the following Reference Letter content and provide a concise summary of the key endorsements and characteristics of the candidate as highlighted by the referee. Focus on the most significant qualities, achievements, and recommendations mentioned.

Here's the Reference Letter content to analyze:

{pdf_text}

Provide a comprehensive yet concise summary capturing the essence of the referee's endorsement and the candidate's key qualities.
"""
    return prompt

# Function to call the Groq API with the extracted text
def groq_api_call(prompt, doc_type="resume"):
    try:
        system_message = system_message_resume if doc_type == "resume" else system_message_sop_reference
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred while communicating with Groq API: {str(e)}")
        return None

# Function to parse the AI response and extract sections
def parse_ai_response(ai_response, type="resume"):
    data = {}
    
    if type == "resume":
        sections = ["Education", "Experience", "Skills", "Projects", "Extra-Curricular", "Notes","Name","Email id"]
        for section in sections:
            pattern = rf"\*\*{section}\*\*(.*?)\n(?=\*\*|$)"
            match = re.search(pattern, ai_response, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if not content:
                    content = "N/A"
                data[section] = content
            else:
                data[section] = "N/A"
    elif type == "sop":
        data["Motivation"] = ai_response.strip()
    elif type == "reference":
        data["Endorsements"] = ai_response.strip()
    
    return data

# Function to process the parsed data into a pandas DataFrame
def process_data_to_df(resume_data, sop_summary, reference_summary):
    df = pd.DataFrame([{
        "Education": resume_data.get("Education", "N/A"),
        "Experience": resume_data.get("Experience", "N/A"),
        "Skills": resume_data.get("Skills", "N/A"),
        "Projects": resume_data.get("Projects", "N/A"),
        "Extra-Curricular": resume_data.get("Extra-Curricular", "N/A"),
        "Name":resume_data.get("Name","N/A"),
        "Email id":resume_data.get("Email id","N/A"),
        "SOP Motivation": sop_summary,
        "Reference Summary": reference_summary,
    }])
    return df

# # Function to store data into MySQL database
# def store_data_to_db(df):
#     password = urllib.parse.quote_plus('Meet@2001')  # Replace with your actual password
#     engine = create_engine(f'mysql+mysqlconnector://root:{password}@localhost:3306/testdb')
    
#     try:
#         # Append the new data to the existing table
#         result = df.to_sql('resume_ai', con=engine, if_exists='append', index=False)
#         st.success(f"Number of rows affected: {result}")
#     except Exception as e:
#         st.error(f"An error occurred while storing data to the database: {str(e)}")

def store_data_to_db(df):
    # Use urllib.parse to safely handle special characters in password
    password = urllib.parse.quote_plus('4JBhsn93F1')
    
    # Update connection string with new database details
    engine = create_engine(
        f'mysql+mysqlconnector://sql3747402:{password}@sql3.freesqldatabase.com:3306/sql3747402'
    )
    
    try:
        # Append the new data to the existing table
        result = df.to_sql('resume_ai', con=engine, if_exists='append', index=False)
        st.success(f"Number of rows affected: {result}")
    except Exception as e:
        st.error(f"An error occurred while storing data to the database: {str(e)}")

# Streamlit application
def main():
    st.title("📄 Upload your doc for future opportunity")

    st.sidebar.title("Upload Your Documents")
    uploaded_resume = st.sidebar.file_uploader("Choose a Resume PDF file", type="pdf")
    uploaded_sop = st.sidebar.file_uploader("Choose an SOP PDF file", type="pdf")
    uploaded_reference = st.sidebar.file_uploader("Choose a Reference Letter PDF file", type="pdf")

    resume_data = {}
    sop_summary = "N/A"
    reference_summary = "N/A"

    if uploaded_resume is not None:
        with st.spinner("Extracting text from Resume PDF..."):
            resume_text = extract_text_from_pdf(uploaded_resume)

        if not resume_text.strip():
            st.error("No text could be extracted from the uploaded Resume PDF.")
        else:
            st.subheader("Extracted Text from Resume")
            st.text_area("Resume Text", resume_text, height=300)

            resume_prompt = create_prompt(resume_text, type="resume")
            resume_response = groq_api_call(resume_prompt, doc_type="resume")

            if resume_response:
                resume_data = parse_ai_response(resume_response, type="resume")
                st.subheader("### Extracted Resume Information")
                for section, content in resume_data.items():
                    st.write(f"#### {section}")
                    st.write(content)

    if uploaded_sop is not None:
        with st.spinner("Extracting text from SOP PDF..."):
            sop_text = extract_text_from_pdf(uploaded_sop)

        if not sop_text.strip():
            st.error("No text could be extracted from the uploaded SOP PDF.")
        else:
            st.subheader("Extracted Text from SOP")
            st.text_area("SOP Text", sop_text, height=300)

            sop_prompt = create_prompt(sop_text, type="sop")
            sop_response = groq_api_call(sop_prompt, doc_type="sop")

            if sop_response:
                sop_data = parse_ai_response(sop_response, type="sop")
                sop_summary = sop_data.get("Motivation", "N/A")
                st.subheader("### SOP Motivation Summary")
                st.write(sop_summary)

    if uploaded_reference is not None:
        with st.spinner("Extracting text from Reference Letter PDF..."):
            reference_text = extract_text_from_pdf(uploaded_reference)

        if not reference_text.strip():
            st.error("No text could be extracted from the uploaded Reference Letter PDF.")
        else:
            st.subheader("Extracted Text from Reference Letter")
            st.text_area("Reference Letter Text", reference_text, height=300)

            reference_prompt = create_prompt(reference_text, type="reference")
            reference_response = groq_api_call(reference_prompt, doc_type="reference")

            if reference_response:
                reference_data = parse_ai_response(reference_response, type="reference")
                reference_summary = reference_data.get("Endorsements", "N/A")
                st.subheader("### Reference Summary")
                st.write(reference_summary)

    # Combine all extracted data into a DataFrame and display
    if uploaded_resume is not None or uploaded_sop is not None or uploaded_reference is not None:
        data_df = process_data_to_df(resume_data, sop_summary, reference_summary)
        st.subheader("### Combined Data for Database Storage")
        st.write(data_df)

        # Store the data into the MySQL database
        if st.button("Store Data to Database"):
            store_data_to_db(data_df)

# Run the main function
if __name__ == "__main__":
    main()