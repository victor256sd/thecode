# Copyright (c) 2025 victor256sd
# All rights reserved.

import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
import re

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

# Definitive CSS selectors for Streamlit 1.45.1+
st.markdown("""
<style>
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Load config file with user credentials.
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initiate authentication.
authenticator = stauth.Authenticate(
    config['credentials'],
)

# Call user login form.
result_auth = authenticator.login("main")
    
# If login successful, continue to aitam page.
if st.session_state.get('authentication_status'):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state.get('name')}* !')

    # # Initialize chat history.
    # if "ai_response" not in st.session_state:
    #     st.session_state.ai_response = []
    
    # Model list, Vector store ID, assistant IDs (one for initial upload eval, 
    # the second for follow-up user questions).
    MODEL_LIST = ["gpt-4o-mini"] #, "gpt-4.1-nano", "gpt-4.1", "o4-mini"] "gpt-5-nano"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    INSTRUCTION_ENCRYPTED = b'gAAAAABpFXAUdJ0_W8SDxm9j3LAtKyHNB3G89-Wi4KUBySxH7fcrNJR39rY_UM3TQVS68VJLfdhL_bnlbZXLDQr0p5rFw3_GLftxzXCODn1-r6rJM1vCbC9X5junFKIbv4-Hs54oKOWhbHQD1hET5R1gxL03YnAXs6CIjRWA8pV0c_7JKKuz1GENMqrZVkTUofbK_Qmv_cNbSc_3ncV3P2BiyNCJf5J9tJe_RREXopVgAhJSonipHIwVg_QZJ3itiAmUbC1WiQkbaBgs3tNzFKY0XgqVhc_qc-U0XzcPh7iX3eO_Q6rdO46AGusyYXvjKZnyvBJNEM3A9L0joSB48hymoNCTzfSx374RNbFUBXk-uMhGya7NvALnKJUEwtvzaGmv4_G_yKOMYhflVmvHfH780xpM8DQiwrghmIR5tyfTZWTdLdt_gcBQtovl8jTnSbe2R-ew1bogYEd7TTX4828KFqegWdwaXB5fGImBpeXDyOz0gYZdtTRe9cX-dl2vAfxeTd__6bHmwbyLewrcg4JIEAsXvVadSAMDuHNNypPnXytKo0ZcTX68X1y_jVJ0KPCyBgJ-RaqvPPzmCNHseAo8X6FiFHkzX5_phaP0Lb7G2Tl7jy0feQ66ugN_tLiQsGh12bUmwy4RDgPcFSVifzYFuQSyTOHD8Gdbx8ZOpviC0ZLkVXJQGk80mPQdvIU6OKa5AXQcUCojLQWBt3VI0j7RYxKw2y9fK_dOdWIYyOgCLKJcmKIty51ipVbNIsHW8XS6MJWPXENGW7YjN9hXdNxNgt5fCX2ssf5YABinjSoOXzdStnA5B0ZzsQxS4PQJvsFiK4dyCCPF0dg_x2tdbc-mNPfqxLP5FC3Pq8LsphqmSt8bvSnCL8MbLzSNHmDRyJ24kDLlZiE2CcixaFiyOTPhHLQOcDftQs79OoYstGsBrsNdWEMvE55ClE0xPm91AMViBDpgPSbScsEuQz3ldgaxX2-Zdf1DDD3UW3irH6iiggObzgJFgYc-gZOcNcDmodcL23cMazGpkHqJV9pyIPH271hanEBlevB8Y9kYreJjkbX13x1A1hBWmDwfOMrXmXjX31TrLkZ2GAPrh06deiKesiaTyeH1XWAzhM9EQxrF3xcGXqqlult5B6QxbgQpZMiNx_s9x1XtALdQ4rIeL26HvwcWi0RonXx2xNvMQaJUfwYE8WNf0Ae5w_4lkbxqwwkVFsFqoGqcwUfDRzpjUD8DIib3wPtTQl33I1p-rh5A_TsxGWtCm34BAzUY2h4kl2QfZvGVhCXVlKooSVSpgDu6eGCisQDCAym9VcQJMIdqbcXTJk4d4NQGllrycbc55m-Eq0ag2JZAHPT5jEEp5NYuNkg_qOXuBiYDFp4FIjaz3u4sIAWC8c_OEUqpYfK0OMc75pjMDE-ZcMx-wU8EqeVpRyNNqmERaKWH6B8lsJF1udyUC-PYFsNgyFX_VO9ZdI7RlBALO4BGqjjUw7eSbEWgzcdgrVM46A3ybNQWv8O4r05wb2-xQ9yFTsk4fcHO2Z5yJDYrOMzywKzg_M3PciBuK4GP-rN0hB3JhrUgRofp1tGnFYzf7fQMTYRfemCbkv0njJ0kDr543H0DBF3pr3jc9ztpACCBgdWSyJ5IknwF8mjoDUHLPzgYYRSagDJbSGh2sjoJeuAfSjAyAu3IaJ9wfFjjKunJfwhtk5ysRwA7bih1REcmgiye9nwkmVDYf8Uoz6VQBQZOST_yYse8qHxHUpYIsuBLqEgQBZ93tnSLmpL9G0QDY3YYdvTm4Ms6oC8ubuihPibqyW-QIDwWnaw2b216qCtAXWJ9EHmFDZzPFA6NVcOcQy9mCYg6RVgKG5ErEOe0sCZcDFUhLH4YT8aDDKcXHa9wcn_vyh5-wJd-diWXPUvvwx1r60Vc-QCEEyXTotEelfLyb97STm2PsUZsqw8zf28wpBhOah_x-mtcXS6fG1NYHbejtm7R0ATLuuprk6jRm2i4gtEYF3rtpD02P788aRm0idTvK1n4kZOMwLlqWP1oHZjX1-1Q_V35mRSOpOP8yb32TluLuBDxXTg2dq9LiyVDhwtoyoJBc0_onOkzwyahYJPjcVyhN9EBt8o6n1BXP6bW99Qwx0qmvgJPubyuRYJ60Keoqe6-JR6ZdbgM0FEfrwetyl6DckeGGJEOYgY8xGPAXcPXyJgYO4BTiT7XyTSjABGAfIbRDFUlVwTNfmK0b4vQD5hY3ZxTMclKrSm8ViDhXpvF0AGnPEiP_FykYDIrIiip_tDNPUg6TLXnYTUSdSCZ35aQCAnJm_IaMzEFlAJ_7olpB184r6Yh__uAdjGWKi5_LOLNah89znzJ_M0EOIczNb_fL_MYV5EwBgx34bEw9yfIPAJVq1xZVYSNp55r2yF6tjjlUbbGRDgozafYqUfe9t90SiF-rv4y7l1u8cBJPBl47_usejWMp-mb6DjZjITdYJct7de5Ckumxh4Wr2RIyk3oiOEitq38K64bMw6-l_LCDRYvLFJqNxCREFk1CU2L67TCWGvJz1-HSc1JQPYXJMaaB86_Vc31RESP1JRlcH-7b5-3pZxwfM4EGQDjl7zNC6_9g2xtMmJJLJkCL9j3F5DTDcFb5RrTtUZDcUIcmBgK4SvlnN4HIm4lKsrmkJ1Y-AVuzzzccRXeDdSLHvVWMb3f5aZKAGMM4ewVRqs7r4MrWuAaarSbtdjf0TcXLsQHNhvrDlYNQGwipmgrTE6uVE_TuDzEz-Njw_zaOEnFVuIgE6cw6aJR3_fAeDyIsfVFS4A1DM8f6r51HSNtqdHT4dmBHsftInQUC1tzvKgHMULbrnejvMrIOuZSU1gNvHCwekur9DjzbDymdqeICV00ck3DWpoHFm3KFBT2Oa9oNZYd59-XP0y1Ow4MwUO27qCrahs7fAH-DFQLRiQ2UWsHnhd-7x3uF8_VbTgjnasp3N1d26ugBInG5R6sQXDmiKbixWGdm82uAI9A73ASpma6HCvI4L7kLAHjo4XpXgRP9cO8JHLwrXDEv9eZsa7g3UMkFtyahXoZtFm-zqDQ44MrZDaPm8kAi2673xIT94etOPqLsgtjaRdvby7NUsm1HStnmICXCBHEp_VxoCCW8cU2tr82IaacQv_GUnOxf9ut-pvsfqPZYoOt83Gd7Dy4EeYzrFigkDxRk2rc85Eclyi1yMmtslPO1fL27saqpsa-UzFr9f2qm4iLIyqksu4GeOyeERdVMsSBfysKzyxThKVX4meFZB1vFp60HvUueW_4'

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Integrity AI", page_icon=":swan:", layout="wide")
    st.header(":swan: Integrity AI")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()
    
    # Create new form to search aitam library vector store.    
    with st.form(key="qa_form", clear_on_submit=False, height=300):
        query = st.text_area("**Ask for guidance on the Model Code of Ethics for Educators:**", height="stretch")
        submit = st.form_submit_button("Send")
        
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("Enter a question for MCEE guidance!")
            st.stop()            
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = INSTRUCTION,
                input = query,
                model = model,
                temperature = 0.6,
                # text={
                #     "verbosity": "low"
                # },
                tools = [{
                            "type": "file_search",
                            "vector_store_ids": [VECTOR_STORE_ID],
                }],
                include=["output[*].file_search_call.search_results"]
            )
        # Write response to the answer column.    
        # with answer_col:
        try:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output_text) #output[1].content[0].text)
        except:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output[1].content[0].text)
        st.write("*The guidance and responses provided by this application are AI-generated and informed by the Model Code of Ethics for Educators and related professional standards. They are intended for informational and educational purposes only and do not constitute legal advice, official policy interpretation, or a substitute for professional judgment. Users should consult their school district policies, state regulations, or legal counsel for authoritative guidance on ethical or compliance matters. This tool is designed to assist, not replace, professional decision-making or formal review processes.*")
        st.markdown("#### Response")
        st.markdown(cleaned_response)

        st.markdown("#### Sources")
        # Extract annotations from the response, and print source files.
        try:
            annotations = response2.output[1].content[0].annotations
            retrieved_files = set([response2.filename for response2 in annotations])
            file_list_str = ", ".join(retrieved_files)
            st.markdown(f"**File(s):** {file_list_str}")
        except (AttributeError, IndexError):
            st.markdown("**File(s): n/a**")

        # st.session_state.ai_response = cleaned_response
        # Write files used to generate the answer.
        # with sources_col:
        #     st.markdown("#### Sources")
        #     # Extract annotations from the response, and print source files.
        #     annotations = response2.output[1].content[0].annotations
        #     retrieved_files = set([response2.filename for response2 in annotations])
        #     file_list_str = ", ".join(retrieved_files)
        #     st.markdown(f"**File(s):** {file_list_str}")

            # st.markdown("#### Token Usage")
            # input_tokens = response2.usage.input_tokens
            # output_tokens = response2.usage.output_tokens
            # total_tokens = input_tokens + output_tokens
            # input_tokens_str = f"{input_tokens:,}"
            # output_tokens_str = f"{output_tokens:,}"
            # total_tokens_str = f"{total_tokens:,}"

            # st.markdown(
            #     f"""
            #     <p style="margin-bottom:0;">Input Tokens: {input_tokens_str}</p>
            #     <p style="margin-bottom:0;">Output Tokens: {output_tokens_str}</p>
            #     """,
            #     unsafe_allow_html=True
            # )
            # st.markdown(f"Total Tokens: {total_tokens_str}")

            # if model == "gpt-4.1-nano":
            #     input_token_cost = .1/1000000
            #     output_token_cost = .4/1000000
            # elif model == "gpt-4o-mini":
            #     input_token_cost = .15/1000000
            #     output_token_cost = .6/1000000
            # elif model == "gpt-4.1":
            #     input_token_cost = 2.00/1000000
            #     output_token_cost = 8.00/1000000
            # elif model == "o4-mini":
            #     input_token_cost = 1.10/1000000
            #     output_token_cost = 4.40/1000000

            # cost = input_tokens*input_token_cost + output_tokens*output_token_cost
            # formatted_cost = "${:,.4f}".format(cost)
            
            # st.markdown(f"**Total Cost:** {formatted_cost}")

    # elif not submit:
    #         st.markdown("#### Response")
    #         st.markdown(st.session_state.ai_response)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
