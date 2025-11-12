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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpDr6pr5lcuhllqSzfFrrlNpRvcPOBMEXgk1YP4DoQKIIdTMh3KToBCvPDXtI8840ZQB6VehKeuyuZ640-wSeM5nJp_X_zmkAKUVKIX0tOsCl_nDyTOkg4XY_FfAHdiCTjAllLR94lr5s9-RThsXFwa87RjTXnqPT2mThrPendHmCwJxF_UF8W6GhPXuJH2payqrATRYd0WsEz5g-TTkvNeVaylRYuy8fMkJjJdn8KRoy6F3JfKgIaIERs9uQcOeh4Vz8aakbHl3w0WIhP2X_Z2n3pRUL9WoPAu-wDMoYp7WeItOwW50r16qCJqdnrOlNpwju_P9WWaJVFJNuP7TY5_ju6ZAYiV0fGislODphLO6PpU1uc_oASQ78vrsqxogXrugZ7_A6yge16HToMDoZDyPEDTAwxEiXYCqbq143aQXyYJWvSNyUFw85ws0D229IBvRlsyL9c1g_Wxyr-NfpjiK3UTZxvS4parZ97XGFDWpjZf6xIQFpWlmdmbQwTtxx9jiUXeWDQa8_EZlyooAqCRT6wVXetXnZTRIUHYfl9q-bg3rRkc91rQl2PWkrryl4jpdtjIjP8x70At73RNnye8tcJSKO5JFI-dMXb4vetlwGSXTWp25XQOV6a8WHz0h42ql0OWiUMRs6m0KX3lcROwb1zBe_4BxFK6cVsxt9TfvZ5UJyPvbM7B-EfMy7H8PQOru3jo9wvca3J8JtlrNQR-cB0YPSG5QXDl5S0XTWMmIZtZT9JAZBO9BFQa9Y9V5wcecR3b_7rX_s-jCAOnz-xCR6hKnv0b5j_7V38vDFUA6iKqQpj7xcvOTsuP-alEEGdXjMx7kLpJ_yYIZ2sUBIL_sL-vhxMUutAiqIfKWP_650B1GmpnSqyrs0SGRj4jPpxH8o1xHK7jDfz-1EYkSBRSIIkkZZoskvKGVt6GxazXZ4iHO5lELeJNAQEKgvF2VJLJlUO4mTeC9zC0nsVwGxKG0yNYPbaa2-lLSS6f5HqOc2IMi3LEbVkEae-vHQVHbv63l7ArHnDsn1Z2j_njrbVqvK29c-M4j4NQqSI6kNSzrzhrIBZOE1GZ67vgodDXWHlaAJ1TOa1fYFzxv2YhS0vw_Y4LXRNeGS70GNVKYQRQdt3IsBJZ7OEeuK0xkSvFJlI_U9wJjx9loDSNuQ7fVxnPa7Zt8raXeLRzD3lYeSZnS_CwZRGywUjTsv1WyXB5jvCOU5Si_1FO4o4P4gFkr2Ib_Zs9q9w06W0Kjj1PkGvCo4zJjWoBTVHaKFD62pjNHSGg2eX7wwF4QzeEDXss2ToObbeUJTKC_TKRyYP5pmAJWffmUZr775YbA33tnIbUEO9ZzORTVePUGLB8RFV28gqalKaMmdRYK8mDHkWeXCj9TJVwzmU6mQ1EaqvWr02lIJFICLw6GcBsbxjgJdYS_TKWUfZZjVnyRKatae0T2Id16LrmpBhFWKGUCUnNnuaQJFyLGLsyJq414fe1ANTFB5APy8q4NV363jpo7TAfILSgU5n-Np9bggoXwsT2SVTG2LmCAMDffVY-b3_ejxx0LpTPMUUb28-XSMxFPi5EVZ_cDsEpqVweEUfwPaIQa6_4cMv5yYdzQldWn8-tmrYLycoa2s_6pH3Z6KfdrBTF_PDLkk9f8VDb2UMRH3pld13CVR8MDB4OkVSPmJCYxf6kZ8mJxhhFJBWkj7xe10CyupVYak3R3wOp1H3N1tqEg7OSuoUMbjRTB3zJ6RA_2P5SpcDjsUNk7If-YePXu37E3Q-jlphSysR6r1KPee5RZtU8jsFSltJiQUWumjAccfLsFNltIc284qKXzTls6E_gkof2Z8YUku1oFsJJUMugKOPX-zPzWv0m9E3IQterFSTJy2PWJxeaEPJqbrWfEWeV3DODqerWYS9Fs9cpj36zE-Gt8qAVgDTqZailHq2R3BlzX9rVOSRuIKvv_c60d1EXoWafSHxaCdPfotoGI7YyIqLRjDSAQA0Kd9BLkpzrdEu0iYwzGBvbEQgTzcEZtUPH_sPz5pCd9y2HJr6BBw8wwM9LbU1NdyxhBErM5ljqBPdeyobymIhA5QOfBZkSjaSE21A7kWZr8rTZhMTQGm5U9Z6JbZGe6F-JckMTwktVDcIUWPrPPMgBa6b-fihJ7tJBZo6Ds93eLCE_0P2Z0ck4wxGmQ81kNuqlKUQ-dh6vldU_Mdfc6h62FbNwhm8flX5U6HbTtxgmprlumET_wwK9nNUyOkTK4CP4k2uAX9u-tbTULyxIXQE13ztaamf8S3pOi4VykGN-ivqqcHo8fmcIawAZXGEKmohnV-Dk9nXJ0x_ZAQbH3F7VmVkTXJaV6nW7iBlGy6oTzwFJWQTUic7atzg7BlawM5b2TssHsBil5X-lMPARMmLL-9e9st7FmNksM7Ep9sKAZrfV3-c8n6zQL0tXGv_BMh1F4Jqn65Z6Xg1xrpb8z1EpYJRKl3x_KuF8pGgUuPbv4OXoBT7kObgnyX7br53cEeM7KhU-eleWPxueoi5KorIvKpH2mI_IUv1NvVV81JLr3nRU7i_QeigelLfxXkjwE-Nm6RCnceb10jSG5Y3MFmWCJof6WJA9SgfH9o-KD_r0BFTLJd-OhvFGxtDVxUApDOLDvbR7aiiey3FviQg_rZgVQGx2nIbBhROmH1YRYE-qCoZVaVCWnxXhbv2zBQGTc-Xi701BVuAux42AqUWKsHQLV0W5x73b0VkPnvhGAGJZjgSbgOFhtu6vILLcbOVZoC3xFq7MitrxuyyjZfogrqz4taRso_T8WFg1MuHW8CVhMy1U6sm627lJNVdb9skFetrjQ_BGb5BdjK_9oMFZLk-lxZvE_OS5tbXdgAEOIkOJvsxQs2d4ItWeRuHrwfxsFlgewKpfSolAWiDDhwD04IeX3tbORVUKPNRYwsMfg0OkXQCg9g0p8pazEvC8OaEVmrFSrSgMEmxQPqVWNdNHQ3eJ618cKOUHtqFeDrP0tm9SIzsE_WiA5rtwTrB5SyIKPI1P13-k4XGD9Sc_UQDn4OMTbb0624saDyS4-1XQb8sp5ikCXTNvK6Fzqd6Q3atDt_XVU4mT0uhTIBvHvMg7nXWks-17Nw4QpuCTm1KIQoJn5xRzLdcYAmWY4PJCSyb1xqbEk0GjWVOpbpOQQp0RnvIlzRMctWhjU8dxwo2HoQ9aQxFAHuICkMfmLSuKLLlbxrM4EkFsZCGMpg9ZCtd-5b3jGCJyAipFHumjAUjc9qjSmGm1f7CLc0P4yNKiJ_mokkM3nmCrkaUI2cIcVkSCWlPq4hRFXaLWFWJ-M1KsaTNW9GlgRmurkJNxZHHO8ckRVfDcOIz0ydGL64sU0l9ZF0Ayp6gJyp2c_UhXPIko-hjZD0='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Bridge AI", page_icon=":bridge_at_night:", layout="wide")
    st.header(":bridge_at_night: Bridge AI")
    
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
        query = st.text_area("**Ask for mental health guidance:**", height="stretch")
        submit = st.form_submit_button("Send")
        
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("Enter a question for mental health guidance!")
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
        st.write("*The guidance and responses provided by this application are AI-generated and informed by general psychological principles and mental health best practices. They are intended solely for informational and supportive purposes and do not constitute professional psychological diagnosis, therapeutic advice, or crisis intervention. Users should consult licensed mental health professionals, medical providers, or emergency services for any concerns requiring clinical evaluation, treatment, or urgent care. This tool is designed to assist, no replace, qualified mental health expertise or professional judgment.*")
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
