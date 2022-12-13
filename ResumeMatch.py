from lib2to3.refactor import get_all_fix_names
import unicodedata
import streamlit as st

import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from difflib import get_close_matches
import csv
import os
import streamlit as st
from streamlit_tags import st_tags
import requests
from PyPDF2 import PdfReader
import re
from annotated_text import annotated_text
from streamlit_echarts import st_echarts
import webbrowser
from packages.common import requestAndParse
from packages.page import extract_maximums, extract_listings
from packages.listing import extract_listing
from pdfGenerator import PDF
import math
import unicodedata
import pyresparser 

import en_core_web_sm
nlp = en_core_web_sm.load()



def record_Audio():
    with st.expander("🎙️" + " Prefer audio assistant instead ?", expanded=False):
            #audiorec_demo_app(parent_dir, build_dir,st_audiorec)
            import speech_recognition as sr  

            # get audio from the microphone                                                                       
            r = sr.Recognizer()   
            if st.button('record'):
                with sr.Microphone() as source:                                                                       
                    st.write("Speak:")                                                                                   
                    audio = r.listen(source)   

                    try:
                        audio_text = r.recognize_google(audio)
                        st.write("You said: " + audio_text)
                        myobj = gTTS(text=audio_text, lang='en', slow=False)
                        # Saving the converted audio in a mp3 file named
                        # welcome 
                        myobj.save("welcome.mp3")
                        # Playing the converted file
                        os.system("mpg321 welcome.mp3")
                        #process_text(audio_text)
                    except sr.UnknownValueError:
                        st.write("Could not understand audio")
                    except sr.RequestError as e:
                        st.write("Could not request results; {0}".format(e))

def glassdoor_scrapper(baseurl, targetnum, list_returnedTuple):
    
    maxJobs, maxPages = extract_maximums(baseurl)
    target_num = targetnum
    if (target_num >= maxJobs):
            print("[ERROR] Target number larger than maximum number of jobs. Exiting program...\n")

    page_index = 1
    total_listingCount = 0

    # initialises prev_url as base_url
    prev_url = baseurl
    
    while total_listingCount <= target_num:
        # clean up buffer
        new_url = update_url(prev_url, page_index)
        page_soup,_ = requestAndParse(new_url)
        listings_set, jobCount = extract_listings(page_soup)
        
        print("\n[INFO] Processing page index {}: {}".format(page_index, new_url))
        print("[INFO] Found {} links in page index {}".format(jobCount, page_index))

        for listing_url in listings_set:

            # to implement cache here

            returned_tuple = extract_listing(listing_url)
            #These are the jobs
            list_returnedTuple.append(returned_tuple)

        total_listingCount = total_listingCount + jobCount
        print("[INFO] Finished processing page index {}; Total number of jobs processed: {}".format(page_index, total_listingCount))
        page_index = page_index + 1
        prev_url = new_url
        #progress_outer.update(jobCount)

def update_url(prev_url, page_index):
        if page_index == 1:
            prev_substring = ".htm"
            new_substring = "_IP" + str(page_index) + ".htm"
        else:
            prev_substring = "_IP" + str(page_index - 1) + ".htm"
            new_substring = "_IP" + str(page_index) + ".htm"

        new_url = prev_url.replace(prev_substring, new_substring)
        return new_url

def get_skills(skills):
    auth_url = "https://auth.emsicloud.com/connect/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = env(payload)
    response = requests.request("POST", auth_url, data=payload, headers=headers)
    if response: 
        response = response.json()
        #print('RESPONSE',response)
        token = response['access_token']
        if token:
            url = "https://emsiservices.com/skills/versions/latest/skills"
            querystring = {"q": skills,"fields":"name","limit":"5"}
            headers = {'Authorization': 'Bearer {token}'.format(token=token)}
            response2 = requests.request("GET", url, headers=headers,params=querystring).json()

# def getUSAGOVJobs(keyword):
#     authkey = env('AUTHKEY')
#     user = env('USERAGENT')
#     host = env('HOST')
#     headers =  { "Host": host,
#             "User-Agent": user,          
#                 "Authorization-Key": authkey      
#             }
#     baseUrl = 'https://data.usajobs.gov/api/'
#     response = requests.get(baseUrl + 'Search?Keyword='+keyword, headers =headers ).json()
#     data = response['SearchResult']['SearchResultItems']
#     for opps in data:
#         with st.expander("👨‍💻" + opps['MatchedObjectDescriptor']['PositionTitle'] + " - " + opps['MatchedObjectDescriptor']['OrganizationName'] , expanded=False):
            
#             st.write(opps['MatchedObjectDescriptor']["UserArea"]["Details"]["JobSummary"])
#             if st.button(key= opps['MatchedObjectId'], label="View Online"):
#                 webbrowser.open_new_tab(opps['MatchedObjectDescriptor']['PositionURI'])
def display_postings(job_listings):
    for job in job_listings:
       
        with st.expander("👨‍💻" + job['Company Name'] + " - " + job['Company Role'] , expanded=False):
           
            st.write(job['Description'])


def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def pdf_reader(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
    

def cleanData(text):
    args = [
    ("\\\n", ""), #Removes \r\n
    ("(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", " "), #Removes links
    ("\\< \\>", ""), #removes < >
    ("\\[ \\]", ""),# Removes [\\]
    ("\\[.*?\\]", ""), #Removes text within [ ]
    ("\\<.*?\\>", ""), #Removes text within <>
    ("\\*", ""), #Removes dashes
    ("  ", ""),
    ("[\d-]", ""),
    ("[^\w\s]", ""),
    ("[ ]{2,}",""), #Removes every empty space whose len is greater than 1
    ]
    for old, new in args:
        text = re.sub(old, new, text)
    return text

def tokenize_and_get_nouns(text):
    text_tokens = word_tokenize(text)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    tagged = nltk.pos_tag(tokens_without_sw)
    tags, nouns = {'NNP', "NN", "NNS","NNPS"}, []
    for word, tag in tagged: 
        if tag in tags:   
            nouns.append(word)
    return nouns

def tokenize_and_get_verbs(text):
    text_tokens = word_tokenize(text)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    tagged = nltk.pos_tag(tokens_without_sw)
    tags, nouns = {'VB', "VBD", "VBG","VBN"}, []
    for word, tag in tagged: 
        if tag in tags:   
            nouns.append(word)
    return nouns
def read_universal_skills():
    fileobj=open('./readme.txt')
    universalSkills=[]
    for line in fileobj:
        universalSkills.append(line.strip().lower())
    return universalSkills

def get_common_skills(resumeSkills, universalSkills):
    skillsSet = set()
    final = {}
    for word in resumeSkills:
        for str in universalSkills:
            if word.lower() in str:
                if word in final:
                    final[word].add(str)
                else:
                    final[word] = set()
                    final[word].add(str)

    for key in list(final):
        if len(final[key]) > 10:
            del final[key]
    skillsSet= set()
    for key2 in final:
        
        y = get_close_matches(key2.lower(), list(final[key2]), 5, 0.6)
        if y:
            for item in y:
                skillsSet.add(item)
    return skillsSet
def unicode_normalize(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
def get_top_resume_skills(skillsSet):
    data = dict()
    with open('./TechnologySkills.csv', 'r') as infile:  
        # Iterate over each row in the csv using reader object
        for sk in skillsSet:
            csv_reader = csv.reader(infile)
            for row in csv_reader:
                # row variable is a list that represents a row in csv
                if row[1].lower() == sk:
                    if row[0] in data:
                        data[row[0]] += 1
                    else:
                        data[row[0]] = 1
            infile.seek(0)
    data = sorted(data.items(), key = lambda x:-x[1])
    print(data)
    return data
def process_url(top_keyword, job_type):
    top_keyword= str(top_keyword).lower().replace(" ", "%20")
    top_keyword += "%20" + job_type
    return "https://www.glassdoor.com/Job/jobs.htm?sc.keyword="+ top_keyword+ "&jobType=" + job_type +"&fromAge=-1&minSalary=0&includeNoSalaryJobs=False&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0"
def _max_width_():
    max_width_str = f"max-width: 1400px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )



def startApp():
    global opportunity_kind
    st.set_page_config(
        page_title = "Review Your Resume",
        page_icon=":notepad:",
        )
    _max_width_()
   
    st.title("Career Matches")
    st.header("")
    with st.expander("ℹ️ - About this app", expanded=True):

        st.write(
            """     
    -   *Career Matches* is an app that extracts skills from your resume to help you get matched to careers and opportunities that match your skills
    -   It used keyword extraction technique that leverages NLP and compares it with a massive database of careers and skills 
    -   No personal data is stored
    -   You can download a pdf analysis of your resume for your later analysis
            """
        )
    st.write("")
    st.write("")  
   

    st.write("")
    st.write("")
    st.subheader("📁 Upload your resume as pdf")
    uploaded_file = st.file_uploader(label= "",type=['pdf'], accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)  
    #record_Audio()

    st.write("")
    st.write("")
            
    if uploaded_file is not None:
            
            save_image_path = './resume/'+uploaded_file.name
            with open(save_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.write("")
            st.write("")
            st.write("")
            st.write("")
        
            resume_data = pyresparser.ResumeParser(save_image_path).get_extracted_data()
            
            if resume_data['skills']:
                resume_text = pdf_reader(save_image_path)
                clean = cleanData(resume_text)
                resumeverbs = tokenize_and_get_verbs(clean)
                #st.write(resumeverbs)
                x = resume_text.split(" ")
                over_used = {'reliable', 'social', 'friendly', 'motivated', 'leader', 'successful', 'experienced', 'creative', 'outgoing', 'dependable', 'independent', 'bilingual', 'educated', 'driven', 'trained', 'team player', 'adaptable', 'innovative', 'confident', 'organized', 'enthusiastic', 'expert', 'skilled', 'proficient', 'organise', 'detail-oriented', 'problem solver', 'inform', 'responsible', 'manage', 'conduct'}
                found_overUsed = []
                for word in over_used:
                    y = get_close_matches(word, x, 5, 0.8)
                    #st.write(y)
                    if len(y)>0:
                        found_overUsed.append(word)
                #st.write(found_overUsed)

            # st.write(len(resumeverbs)/len(clean)*100)
                skillsSet = get_common_skills(resume_data['skills'], read_universal_skills())
                data = get_top_resume_skills(skillsSet)
                
                st.subheader ("🧐 Resume Analysis")
                st.write(
                    """
                    - A good resume should be well-organized, easy to read, and concise.
                    - It should include your contact information, work experience, education, and any relevant skills or accomplishments. 
                    - It's important to tailor your resume to the specific job or industry that you are applying for, and to highlight your most relevant qualifications and experiences.
                    - Here are some specific tips for making your resume stand out:
                        1. Use a clear, professional font and layout.
                        2. Keep your resume to one or two pages.
                        3. Include specific examples and accomplishments, rather than using vague or overused words.
                        4. Tailor your resume to the specific job or industry that you are applying for.
                        5. Use bullet points to make your resume easy to scan and read.
                        6. Proofread your resume carefully to ensure that it is error-free.
                    
                    Overall, a good resume should effectively highlight your skills, experiences, and qualifications, and showcase why you are the best candidate for the job.
                    """
                )
                st.write("")
                st.write("")
                st.write("")
                 
                with st.expander(label="📝 Your resume - click to view", expanded= False):
                    
                
                    resume_text2 = ""
                    for word in x:
                        
                        if word in resumeverbs:
                            resume_text2 += str((word, "Action Word")) + " "
                        elif word in over_used:
                            resume_text2 += str((word, "Commonly Used word")) + " "
                        else:
                            resume_text2 += word + " "
                    # 
                    st.write(resume_text2)
                    annotated_text(resume_text2)

                        



                st.subheader("🔎 Closer Look")
                if found_overUsed:
                    st.write( 
                    """
                    - It seems that there is an **occurence of commonly overused words your resume**.\n

                    """
                    )
                    st.write(
                    f'- These words, or a variation of these words found in your resume:  **{ ", ".join(f"{w}"for w in found_overUsed)}** say nothing specific about your performance.'
                    )
                    st.write(
                    """
                    \n - It's important to use these words sparingly and to **focus on using specific, concrete examples and accomplishments to demonstrate your skills and qualifications**. Instead of simply saying that you are a "hardworking" or "motivated" person, try to include specific examples of times when you went above and beyond in your job or took on a challenging project and were able to successfully complete it.
                    \n - This will help make your resume more impactful and memorable to potential employers.
                    """
                    )
                
                else:
                    st.write( 
                    """
                    -  Your resume is great, there is **no occurence of commonly overused words**
                    """
                    )
                if len(resumeverbs)>2:
                    st.write( 
                    """
                    - Your resume is **great**, there is use of active verbs in describing your accomplishments.

                    """
                    )
                else:
                    st.write( 

                    """
                        A quick review of your resume shows that there is minimal use of active verbs

                        It is important to use active verbs in a resume because they make your accomplishments and responsibilities sound more dynamic and impressive. **Active verbs help to portray you as a proactive and capable individual who can take charge and get things done. They also make your resume more engaging and easy to read, which can help to catch the attention of potential employers**.

                    """
                    )

                
                st.write("")
                st.write("")
                st.subheader("👷 Where Are Your Skills Commonly Used")  
                st.write("")
                st.write("")
                data2 = []
                majority = data[0][1]

                for name, val in data:
                    data2.append({"value":(val/majority)*100 , "name":name})
                option = {
                    "tooltip": {
                        "trigger": 'item',
                        "formatter": '{b} : <br/>{c}%'
                    },
                    "darkMode": False,
                    "toolbox": {
                        "show": True,
                        "feature": {
                        "mark": { "show": True },
                        "dataView": { "show": True, "readOnly": False },
                        "restore": { "show": True },
                        "saveAsImage": { "show": True }
                        }
                    },
                    "series": (
                        {
                        "name": 'Nightingale Chart',
                        "type": 'pie',
                        "radius": [50, 200],
                        "center": ['40%', '50%'],
                        "roseType": 'area',
                        "itemStyle": {
                            "borderRadius": 8
                        },
                        "data": data2[0:6]
                        },
                    )
                    }
                st_echarts(options=option, width="100%", key=0, height= "400%", theme="light")

                skillsSet = [skill for skill in skillsSet]
                
                st.subheader ("Core Competencies")
                st_tags(label="Please delete  data that may be irrelevant", text ="Skills", value = resume_data['skills'], key = "2")
                st.subheader ("Less Weighted Skills")
                st_tags(label="Please delete  data that may be irrelevant", text ="Skills", value = skillsSet, key = "1")
                

                #FETCH DATA FROM GLASSDOOR
                # submitted = False
                with st.form("my_form"):
                    st.write("To match you to opportunities that align with skills in your resume")
                    val = st.selectbox(label = "What are you looking for?", options = ("Internship", "Job"))
                
                    # Every form must have a submit button.
                    submitted =  st.form_submit_button("Submit")
                if submitted:
                    opportunity_kind = val
                    list_returnedTuple = []
                    with st.spinner('Please wait as  I fetch relevant job postings ...'):
                        base_url = process_url(data[0][0], opportunity_kind)
                        glassdoor_scrapper(base_url, 4, list_returnedTuple)
                        display_postings(list_returnedTuple)
                    st.success('Done!')
                    pdf = PDF('P', 'mm', 'Letter')
                    pdf.alias_nb_pages()
                    # Set auto page break
                    pdf.set_auto_page_break(auto = True, margin = 15)
                    #Add Page
                    pdf.add_page()
                    # specify font
                    pdf.set_font('helvetica', 'BIU', 16)
                    pdf.set_font('times', '', 12)
                    pdf.chapter_subTitle("YOUR INFORMATION")
                    pdf.cell(10, 8, "Name: "+ resume_data['name'], ln=2)
                    pdf.cell(10, 8, "Email: "+ resume_data['email'], ln=2)
                    pdf.cell(10, 8, "Years of Experience: "+ str(resume_data['total_experience']), ln=2)
                    if resume_data['college_name']:
                        pdf.cell(10, 8, "College Name: "+ resume_data['college_name'], ln=2)
                    pdf.ln()
                    pdf.chapter_subTitle("TOP COMPETENCIES")
                    for item in skillsSet:
                        pdf.cell(10, 5, "- "+item, ln=2)
                    pdf.ln()
                    pdf.chapter_subTitle("OTHER SKILLS")
                    for skill in resume_data['skills']:
                        pdf.cell(10, 5, "- "+skill, ln=2)
                    pdf.ln()

                    if data:
                        pdf.chapter_subTitle("Percentage match of skills and use among professionals")
                        majority = data[0][1]
                        for i in range(0,10):
                            name, val = data[i][0], data[i][1]
                            pdf.cell(10, 5, " - "+ name + ": " + str(math.ceil((val/majority)*100))+ "%", ln=2)
                            pdf.ln()
                            pdf.ln()
                    
                    pdf.chapter_subTitle("JOBS")
                    for job in list_returnedTuple:
                        name  = str(unicode_normalize(job["Company Name"])).replace("b'", "")
                        role  = str(unicode_normalize(job["Company Role"])).replace("b'", "")
                        final = f'{name}{": "}{role}'
                        pdf.ln()
                        pdf.chapter_subTitle(final)
                        desc = str(unicode_normalize(job['Description'].replace("b'", "").replace("/n", ".")))
                        pdf.multi_cell(0, 7, txt = desc)
                        pdf.ln()
                        pdf.set_text_color(0,0,255)
                        pdf.cell(w = 10, h = 7, txt = "View In browser", ln=2, link = job['Requested Url'])
                        pdf.set_text_color(0,0,0)
                        # line break
                        pdf.ln()
                    
                    pdf.output("pdf_2.pdf")
                    with open("pdf_2.pdf", "rb") as pdf_file:
                        pdf_byte =pdf_file.read()
                    st.download_button(label="Download Your Resume Report",
                    data=pdf_byte,
                    style="background-color: #DD3300;",
                    file_name="Report.pdf",
                    mime='application/octet-stream')
                    
startApp()