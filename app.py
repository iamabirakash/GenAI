from dotenv import load_dotenv
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_core.prompts import PromptTemplate

load_dotenv()
st.header("College Research Assistant")
colleges = [
    "IIT Delhi",
    "IIT Bombay",
    "IIT Madras",
    "IIT Kanpur",
    "IIT Kharagpur",
    "NIT Trichy",
    "NIT Surathkal",
    "BITS Pilani",
    "VIT Vellore",
    "SRM University",
    "KIIT University",
    "Amity University",
    "Lovely Professional University (LPU)",
    "Heritage Institute of Technology",
    "Techno Main Salt Lake"
]
lines = [5,10,15,20,25,30,35,40,45,50]
selected_college = st.selectbox(
    "Select a College from the list below to get detailed information about it:",
    colleges
)


# selected_lines = st.selectbox(
#     "Select no of lines",
#     lines
# )

if st.button("Submit"):
    # prompt = f"""
    # You are an expert education and career counselor.

    # Provide detailed information about {selected_college}, in not more than 10 line including its history, courses offered, campus facilities, faculty, placement records, and any other relevant information that would help a prospective student make an informed decision about applying to this college.
    

    
    # prompt_template = PromptTemplate(
    #     template = """You are an expert education and career counselor.
    #     Provide detailed information about {college_name}, in {num_lines} lines including its history, courses offered, campus facilities, faculty, placement records, and any other relevant information that would help a prospective student make an informed decision about applying to this college.""",
    #     input_variables=["college_name", "num_lines"],
    # )
    

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=1.2,
        api_key=os.getenv("API_KEY"),
    )

    chatPromptTemplate = ChatPromptTemplate.from_messages([
        ("system", """You are an expert education and career counselor.
            Your job is to provide accurate, structured, and student-friendly information about colleges.
            Always include:
            1. Introduction
            2. History
            3. Courses Offered
            4. Campus Facilities
            5. Faculty
            6. Placements
            7. Rankings & Recognition
            8. Admission Process
            9. Student Life
            10. Conclusion
            Keep the response concise and well formatted.
            """
        ),
        ("ai","""Sure! Please tell me the name of the college. I will provide a detailed report covering its history, academics, placements, campus life, and admissions."""
        ),
        ("human","Generate a detailed report about {college_name}."
        ),
    ])

    parser = StrOutputParser()
    prompt = chatPromptTemplate.format(college_name=selected_college)
    response = model.invoke(prompt)
    result = parser.invoke(response)
    st.subheader(f"📘 Report for {selected_college}")
    st.write(result)
# print(result)

