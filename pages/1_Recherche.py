import streamlit as st
import time
import numpy as np
import utils.scrapper as scrp

st.set_page_config(page_title="Plotting Demo", page_icon="📈")

# Check if there is already an existing driver in the session state
if 'driver' not in st.session_state:
    st.session_state.driver = scrp.OpenBrowser()

st.header("Rechercher des missions")

# Initialize session state for form submission and user credentials
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Define the form submission handler
def handle_form_submit():
    st.session_state.form_submitted = True

def open_browser_and_login(username, password):
    scrp.login(st.session_state.driver, website_url, username, password) 

# Main Streamlit app
website_url = "https://www.turnover-it.com"
search_url = "https://www.turnover-it.com/livedemandes"

if not st.session_state.form_submitted:
    with st.sidebar.form(key='my_sidebar_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label='Connecter')

    if submit_button:     
        open_browser_and_login(username, password)      
        st.sidebar.success("Form Submitted!")
else:
    st.sidebar.success("Vous etes connecté")



# List of region names
regions = [
    "Indifférent => Toutes regions", "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", 
    "Bretagne", "Centre", "Corse", "Grand-Est", "Hauts-de-France", 
    "Ile de France", "Normandie", "Nouvelle Aquitaine", "Occitanie", 
    "PACA", "Pays de Loire", "DOMTOM - Guadeloupe", "DOMTOM - Guyane", 
    "DOMTOM - La Réunion", "DOMTOM - Martinique", "DOMTOM - Mayotte", 
    "PAYS - Autres pays", "PAYS - BELGIQUE", "PAYS - CANADA", 
    "PAYS - FRANCE", "PAYS - LUXEMBOURG", "PAYS - MONACO", 
    "PAYS - Nouvelle-Calédonie", "PAYS - SUISSE"
]

job_offers = []

with st.spinner("finding offers..."):
    with st.container():
        with st.form("search form"):
            keywords = st.text_input(label="", placeholder="keywords")
            location = st.selectbox('Location', regions)
            submitted_search = st.form_submit_button("Search")

        if submitted_search:
            data_url = "https://www.turnover-it.com/livedemandes"
            job_offers = scrp.GetData(st.session_state.driver, data_url, keywords, location)
            jobs_titles = [job['title'] for job in job_offers]
            jobs_details = [job['details'] for job in job_offers]
            # st.write(jobs_titles)
with st.container():

    # tabs  = st.tabs(["1","2","3","4","5",])
    # titles_column = st.columns(1)
    if len(job_offers)>0:
        # with titles_column:
        for job in job_offers:
            # st.text(job)
            st.text(job['popup_text'])
            st.subheader(job['title'], divider=True)
            
    else:
        st.text("Résultats:")
    # with details_column:
    #     for det in jobs_details:
    #         st.text(det)
    # with add_column:
    #     for det in jobs_details:
    #         st.link_button(label="Ajouter")

    # for tab in tabs:
    #     with titles_column:
    #         for job in jobs_titles[0:10]:
    #             st.text(job)
    #     with details_column:
    #         for det in jobs_details[0:10]:
    #             st.text(det)
    #     with add_column:
    #         for det in jobs_details[0:10]:
    #             st.link_button(label="Ajouter", url="https://www.google.com")        

