# import streamlit as st
# import json
# from groq import Client

# # Initialize the Groq client
# client = Client(api_key='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')

# # Load the JSON course data
# with open("course_data.json") as file:
#     course_data = json.load(file)

# # Function to format prompt based on user selections
# def create_prompt(bachelor_background, masters_interest, job_role, program_format):
#     # Basic prompt with user's background
#     prompt = (
#         f"Suggest courses for a student with a bachelor background in {bachelor_background}. "
#         f"They are interested in a Masters in {masters_interest}, targeting a job role in {job_role}. "
#         f"They prefer a {program_format} format. "
#     )
    
#     # Append format-specific instructions to the prompt
#     if program_format == "Project based":
#         prompt += (
#             "Provide the following structure:\n"
#             "1 required course: {suggested course}\n"
#             "2 or 3 Professional development courses: {Suggested professional development courses}\n"
#             "3 to 4 core courses: {suggested core courses}\n"
#             "0 to 1 technical elective: {suggested elective}\n"
#             "2 projects: SEP 799 Part 1 & Part 2"
#         )
#     elif program_format == "Course based":
#         prompt += (
#             "Provide the following structure:\n"
#             "1 required course: {suggested course}\n"
#             "2 or 3 Professional development courses: {Suggested professional development courses}\n"
#             "4 to 6 core courses: {suggested core courses}\n"
#             "0 to 2 technical electives: {suggested electives}"
#         )

#     return prompt

# # Function to get course suggestions from Groq
# def get_course_suggestions(prompt):
#     try:
#         response = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="mixtral-8x7b-32768",
#             temperature=0,
#             max_tokens=1000
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         st.error(f"Failed to retrieve course suggestions: {e}")
#         return None

# # Streamlit UI for gathering inputs
# st.title("Course Suggestion App")

# bachelor_background = st.text_input("What’s your bachelor/undergraduate background?")
# masters_interest = st.selectbox("What is your area of interest in Masters?", ["Automotive", "Automation and Smart Systems", "Digital Manufacturing", "Process Systems"])
# job_role = st.text_input("What job role are you targeting?")
# program_format = st.selectbox("What program format do you prefer?", ["Project based", "Course based"])

# if st.button("Submit"):
#     # Create prompt for Groq
#     prompt = create_prompt(bachelor_background, masters_interest, job_role, program_format)

#     # Get course suggestions from Groq API
#     suggestions = get_course_suggestions(prompt)

#     if suggestions:
#         # Display suggestions
#         st.write("Course Suggestions:")
#         st.write(suggestions)
#     else:
#         st.error("Failed to retrieve course suggestions. Please try again.")


import streamlit as st
from groq import Client
hide_streamlit_style = """
    <style>
    #GithubIcon {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {overflow: hidden;}
    header {visibility: hidden;}
    </style>
"""
# Initialize the Groq client
client = Client(api_key='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')

# Define complete course lists for each stream
course_structure = {
    "required_course": "SEP 769 / Cyber Physical Systems",
    "professional_development_courses": [
        "SEP 6EP3 / Entrepreneurial Thinking & Innovation",
        "SEP 6MK3 / Fundamentals of Marketing",
        "SEP 6TC3 / Technical Communications",
        "SEP 6X03 / Livable Cities, the Built and Natural Environment",
        "SEP 705 / Green Engineering, Sustainability and Public Policy",
        "SEP 709 / Emerging Issues, Technology and Public Policy",
        "SEP 710 / International Governance and Environmental Sustainability",
        "SEP 725 / Practical Project Management for Today’s Business Environment",
        "SEP 760 / Design Thinking",
        "SEP 770 / Total Sustainability Management",
        "SEP 773 / Leadership for Innovation"
    ],
    "project_courses": [
        "SEP 799 / M.Eng. Project in Systems and Technology Part 1",
        "SEP 799 / M.Eng. Project in Systems and Technology Part 2"
    ],
    "streams": {
        "Automotive": {
            "core_courses": [
                "SEP 6AE3 / Internal Combustion Engines",
                "SEP 6DV3 / Vehicle Dynamics",
                "SEP 711 / Electric Powertrain Components Design",
                "SEP 716 / Automotive Safety Design",
                "SEP 722 / Electric Drive Vehicles",
                "SEP 724 / Intelligent Transportation Systems",
                "SEP 734 / Issues in Vehicle Productions",
                "SEP 740 / Deep Learning",
                "SEP 742 / Visual Perception for Autonomous Vehicles",
                "SEP 775 / Introduction to Computational Natural Language Processing",
                "SEP 798 / Management and Control of Electric Vehicle Batteries"
            ],
            "technical_electives": [
                "MECH ENG 6Z03 / CAD/CAM/CAE",
                "SEP 780 / Advanced Robotics and Automation",
                "SEP 783 / Sensors and Actuators",
                "SEP 791 / Augmented Reality, Virtual Reality and Mixed Reality"
            ]
        },
        "Automation and Smart Systems": {
            "core_courses": [
                "SEP 713 / Cloud Computing",
                "SEP 728 / Internet of Things (IoT) and industrial Internet of Things (IoT) Systems",
                "SEP 752 / Systems Modeling and Optimization",
                "SEP 767 / Multivariate Statistical Methods for Big Data Analysis and Process Improvement",
                "SEP 780 / Advanced Robotics and Automation",
                "SEP 785 / Machine Learning",
                "SEP 791 / Augmented Reality, Virtual Reality and Mixed Reality",
                "CAS 771 / Introduction to Big Data Systems and Applications",
                "SEP 740 / Deep Learning",
                "SEP 775 / Introduction to Computational Natural Language Processing",
                "SEP 742 / Visual Perception for Autonomous Vehicles",
                "SEP 758 / Software Design Tools and Methods",
                "SEP 759 / Prototyping Web and Mobile Applications"
            ],
            "technical_electives": [
                "SEP 718 / Industrial Automation",
                "SEP 723 / Industrial Components, Networks, and Interoperability",
                "SEP 783 / Sensors and Actuators",
                "SEP 6CS3 / Computer Security",
                "SEP 6DA3 / Data Analytics and Big Data",
                "SEP 6DM3 / Data Mining"
            ]
        },
        "Digital Manufacturing": {
            "core_courses": [
                "SEP 718 / Industrial Automation",
                "SEP 723 / Industrial Components, Networks, and Interoperability",
                "SEP 728 / Internet of Things (IoT) and industrial Internet of Things (IoT) Systems",
                "SEP 735 / Additive Manufacturing",
                "SEP 740 / Deep Learning",
                "SEP 752 / Systems Modeling and Optimization",
                "SEP 758 / Software Design Tools and Methods",
                "SEP 759 / Prototyping Web and Mobile Applications",
                "SEP 780 / Advanced Robotics and Automation",
                "SEP 783 / Sensors and Actuators",
                "SEP 791 / Augmented Reality, Virtual Reality and Mixed Reality"
            ],
            "technical_electives": [
                "SEP 6FM3 / Computer Integrated Manufacturing (CIM) and Flexible Manufacturing",
                "SEP 742 / Visual Perception for Autonomous Vehicles",
                "SEP 767 / Multivariate Statistical Methods for Big Data Analysis and Process Improvement",
                "SEP 775 / Introduction to Computational Natural Language Processing",
                "SEP 785 / Machine Learning"
            ]
        },
        "Process Systems": {
            "core_courses": [
                "SEP 750 / Model Predictive Control Design and Implementation",
                "SEP 751 / Process Design and Control for Operability",
                "SEP 752 / Systems Modeling and Optimization",
                "SEP 767 / Multivariate Statistical Methods for Big Data Analysis and Process Improvement",
                "SEP 718 / Industrial Automation",
                "SEP 783 / Sensors and Actuators",
                "SEP 739 / Distributed Computing for Process Control",
                "SEP 740 / Deep Learning"
            ],
            "technical_electives": [
                "CHEM ENG 773 / Advanced Concepts of Polymer Extrusion",
                "CHEM ENG 740 / Advanced PSE Tools and Methods",
                "SEP 6IT3 / Internet Technologies and Databases",
                "ECE 710 / Engineering Optimization",
                "ECE 732 / Non-linear Control Systems",
                "ECE 736 / 3D Image Processing and Computer Vision",
                "ECE 744 / System-on-a-Chip (SOC) Design and Test: Part I - Methods",
                "ECE 778 / Introduction to Nanotechnology",
                "SFWR ENG 6HC3 / The Human Computer Interface",
                "COMP SCI 6F03 / Distributed Computer Systems",
                "COMP SCI 6TE3 / Continuous Optimization"
            ]
        }
    }
}

# Function to create prompt for Groq based on user input
def create_groq_prompt(bachelor_background, masters_interest, job_role, program_format):
    prompt = (
        f"Suggest relevant courses for a student with a bachelor’s background in {bachelor_background}, "
        f"who is pursuing a Masters in {masters_interest} with a career goal of becoming a {job_role}. "
        f"The student prefers a {program_format} format.\n"
        "The available course categories are:\n"
        f"- Required Course: {course_structure['required_course']}\n"
        f"- Professional Development Courses: {', '.join(course_structure['professional_development_courses'])}\n"
        f"- Core Courses for {masters_interest}: {', '.join(course_structure['streams'][masters_interest]['core_courses'])}\n"
        f"- Technical Electives for {masters_interest}: {', '.join(course_structure['streams'][masters_interest]['technical_electives'])}\n"
    )

    if program_format == "Project based":
        prompt += (
            "Suggested structure:\n"
            "1 Required course, 2-3 Professional development courses, 3-4 core courses, "
            "0-1 technical elective, 2 projects (SEP 799 Part 1 & Part 2)."
        )
    else:  # Course based
        prompt += (
            "Suggested structure:\n"
            "1 Required course, 2-3 Professional development courses, 4-6 core courses, "
            "0-2 technical electives."
        )

    return prompt

# Function to get course suggestions from Groq API
def get_course_suggestions(prompt):
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Failed to retrieve course suggestions: {e}")
        return None

# Streamlit UI for gathering inputs
st.title("Course Suggestion App")

bachelor_background = st.text_input("What’s your bachelor/undergraduate background?")
masters_interest = st.selectbox("What is your area of interest in Masters?", ["Automotive", "Automation and Smart Systems", "Digital Manufacturing", "Process Systems"])
job_role = st.text_input("What job role are you targeting?")
program_format = st.selectbox("What program format do you prefer?", ["Project based", "Course based"])

if st.button("Submit"):
    # Create prompt for Groq
    prompt = create_groq_prompt(bachelor_background, masters_interest, job_role, program_format)

    # Get course suggestions from Groq API
    suggestions = get_course_suggestions(prompt)

    if suggestions:
        # Display suggestions
        st.write("Course Suggestions:")
        st.write(suggestions)
    else:
        st.error("Failed to retrieve course suggestions. Please try again.")
