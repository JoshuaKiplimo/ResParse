from annotated_text import annotated_text
import streamlit as st

def printText():
#     annotated_text(
#     "This ",
#     ("is", "verb", "#8ef"),
#     " some ",
#     ("annotated", "adj", "#faa"),
#     ("text", "noun", "#afa"),
#     " for those of ",
#     ("you", "pronoun", "#fea"),
#     " who ",
#     ("like", "verb", "#8ef"),
#     " this sort of ",
#     ("thing", "noun", "#afa"),
#     ".",
#     "- A good resume should be well-organized, easy to read, and concise.",
    
# )
    st.write(
        "A good resume should be *well organized*, *easy to read* and *concise*",
        # ("well organized,", "","#fea"),
        # " ",
        # ("easy to read","", "#fea"),
        # " ",
        # "and",
        # ("concise.", "","#fea"),
    )
    st.write("")
    st.write(
        "It should include your *contact information*, *work experience*, and any *relevant skills* or *acomplishments*.",
        # ("contact information,", "","#fea"),
        # " ",
        # ("work experience,","", "#fea"),
        # " ",
        # "and any",
        # ("relevant skills","", "#fea"),
        # "or",
        # ("acomplishments.","", "#fea"),

    )
    st.write("")
    st.write(
        "It's important to tailor your resume to the specific job or industry that you are applying for and to *highlight your most relevant qualifications and experiences.*",
        # "and to",
        # ("highlight your most relevant qualifications and experiences.", "", "#fea"),
       
    )
    st.write("")
    st.write("""
        Here are some specific tips for making your resume stand out:
        1. Use a clear, professional font and layout.
        2. Keep your resume to one or two pages.
        3. Include specific examples and accomplishments, rather than using vague or overused words.
        4. Tailor your resume to the specific job or industry that you are applying for.
        5. Use bullet points to make your resume easy to scan and read.
        6. Proofread your resume carefully to ensure that it is error-free.
    
    """)
    st.write("")
    st.write(
        "Overall, a good resume should effectively highlight your *skills, experiences, and qualifications, and showcase why you are the best candidate for the job.*",
        #("skills, experiences, and qualifications, and showcase why you are the best candidate for the job.", "", "#fea"),  
    )