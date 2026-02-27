#################################################################################
# Copyright (c) 2026 victor256sd
# All rights reserved.
#
# 02.27.2026 - Instructions reverted to 11/30/2025 instruction set, vector store
# reduced to MCEE documents only.
#
#################################################################################
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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpobOjM6FD-rnWfEi83YFBHPO89f4vXM5xTJikeefXRoLEqehrC5vdkMgJId7V1s-gjx9APD13TPhuwDYfoM7EP81jY6shRqUaHDr-o7mDCvZXXgi7TTPMYruioaRnev0TqLxn4Fo534ST6o5IC3OcRz4qGNViu1yQTQ9PE2JMIwFRQjZ50sD_UAOlwWTvzuyYlhAXLGHks5x4i6dTnY6kjBucUGD9uHI7VPL4mZG2Q2ILvQE1SPmgO0WZeGZi2WzFadThc72iIbfi1GB6QondXsg27Ait7gwM-_v34xKHrVNDxxOEG-HyazX98QqPxxukcAN-m7e1bS5QskExoOhX_jz_OHJ5Zjfg3xeDppscC8Pg5-fRlImcx4iVHV16OtiVm8XYSRcv8wB5xxnoI4l4M9rcKn0XcwvRsNadI2gac2nZ5_wRqeuA1cRZg-B4qQByZ6Y-WSz25IU250lW6N3kwqhkmvIESeIvUmliqg94Sjup6tS_1iBz33RAnAJpxlFeJrVmgVKerGm1CrHn-lNBujYvsBCVIROoxxKOQcgGjUr_bIj2brrbpKHkl0_eNnSikRh7UccbyDyOwyznQm9ul8F1W4yBcs9Zua9ax_fRmK-0t5xIOVKWpuya4glIBZ-IbkHMqVeKjqWRKaQwfGSwkLR5e130IsaZBTuayKmUe3CQs3De-f-fjMTqf8P3WbBxgdYPS-wO9aOrFQf5_BGxzQjjlMPTBXH_IrHLHRzXbjEMdN5_8LFuAoAXUP4W-xRd1-qNs3DRMGLiw5NJK_kXlrftwjAi04yQR9y9YGq7IvPtuj8bp5XkTHYmD6BxFwwy1xyOHpgFXOdJYC2jWLqMxqJB00US5RrnEh5MOG_MjQ8PI-osx5owa-5kt0nMbWBY5DSO3fx1G9JnuzxvlxU-Ld7Lxm2ebNOQKH3KmWamk1FGATI04mscqECgT2lWzP094kx_cGfnOqcSxN2QbKZ-0UuflQmZrgtKmJmrbtQVvp3CJT_Nq0wpPFx28VWn_DwHwrcOvBzJXbksq5VK9m8IiVj8R5NFAHq9yQPCVEGkfU95R86GZOPKeWzm-f6EQw-S0krmOyjnKZVP8TbGVnjAe-ybteiY6Nsq6Ihcl5sE6pHXBXkTA6XcuP2dWv4SyLE5RJcV5RrzMTHMrwTcLagQOq0ApjLBDyZaOPpzG7-O0Eu99_eD-gi1EzTKa6WP8O6mCH8esamwT3-QKLO2E6T0Ud0qe3iq7n8iO3-O5doITLAJZ7YpmvOtSm7hmMZTqd56Gx0bsMhrzCUvGdwxkAin6U3CHjMYuZ-umMu4JVLoW1yKupoOXQ1hFd8KbKQJChuOQcn_IuVFPwUdvWxYBXym54l4u9UF6Tyfjcfn2nhu_23r5ZaFoLrYs6fXAno4YjPZHR7_ITPWall0yzgKv0GIeozy1FzP3ef91csLhZP-S2ICUKYL7zK2GCUayTCTIeKB1XX6cOZx02RPN01UUqeWG-NiEbetJLDvQbPpLo-GUFPCAKKATnwQ_nrogRTVOWsiw4EVvArSvT35vYrIMD6cEt_8WO9YS7l-fVFO0Wkvnm-Rw2CtzH2VqWa5BpfZtwbzZHJBmsjZgAH30Dn11Rk0Ok8f45H8G8LyvRSJ0TMOs9YnCic8ZHf1w95RUd5nKeVUOPZvPvf0st1sNEbXXVrudRrvOIsq2FleHFyy_IC9m1QqZAADDSbcQX5O7-VnPbv41TNnL0GYhFEPEfOBYge90yxnUNDNqFDPFjjmieJW-Iee7VL_PYK8U_n6_DnpvJlTJXqyN15EIG4hydCA_8sLP1NO-upiDaNJzngNSL-DpZCDVwXJW0BEUBb85UbJVIWGGpAV_ofs6ewUfRs2xcKx_pYJsVPdd9qvzGxY-xYqEUNAMQ3NgBCmTHeKay7m2Xqoimd0GrpZ_eW4njtyXTCOFXzj4MAGQmvBgNFNDmCfpMlA7sOlDhkfYE1qB9gOMeAI3MoirZt5vQBzXTaAJU4K4Z-Kr8ramg9Km4JLDt0sCn8HxbFFezSgx-kmBMa8XhQGTGaCXmiFFWs9LT18cLyyTUvtkPfTEVNgGe8X6kXpPiVxzpnyZWDqMIRby7Ha0kfwRl3SlmOvgH-pRoSECgjhZDaUIv-108YRQ4V1RJMB3Ye3rn0XecZyZDtkBV3OCrVRrcG3K9bBhPzWcxVaLwfaqL_SNVBsu38JRtV4m0CKj1n83evFDjrCVWTEs18CQLQSXEWaocGCFVuMkPmBS5lWOU3bVKqcyU5lKF_dtovZ-nEuvSv5Rldb-oG7cHuOn8RkcE-ZbIkaN3-_HoljEc3iX6UjiSjnVEuW6opXjuMYtvC9EY2biaWMCiT1uCmuSQPqQbNQ7cVzxgofZO4ObF91fdF28bdND1Rtyqtxo8nNxaYIrJgTrX6rxSlP706OawXymP9-e8lINCE_be-XhhbitMuOIFuZrVUKtIDiZ-OzfwrnSCSEwcVJO6OLdEoEMiyFnCbR9y_PZMatfxWzqCwFrAwRNyQNPocz6JnxjS0KAJpOtrJF30EhAsP_yN6nkk3nqgd7hkEYOpdarW0mUNgeVTnkV8QuHbIW8_G40ScbTTjoXyiH_DT937DnRzJ4z1hxMxyIoJ43qRj4NjIF60fD-DwnewmQttFas2CFR3sVIKNXdWlM2J26GpTAiF9PPTm291cVi-ec0twLkFZntMIDyy-gVPgcF3ZHRqzFape-Uk3wMTQJqHbB_TkBwwOCrv9BKxfV53kU1EX066C9ohrTM1CyCM0KwJReuooDkRnRVbz7KjsUcY2Ric3nJ62hhReOnRFlrym2p_dUN1owlEFEQ3cQyBWLyAlgY3diwjINZlMB6hEhpl7FhjYmVyDeN0VhYv9m_iJB0bd9We_1sW6y5ONbpwNZsdcY-VlNSC_gmsf8SES51UOV_Y_uKfhT3D2Wsgd1BHe_OPYbYF1T_0Ocrdr8gc6tavpfZ_2AWUCTgtb9UaBSW4ZB59wppM-iZ6CwAEXr5ImDoacrFhqYQyqmB6_dZ7fqQIFMNbUfmrbN91eQ-8rR0wQl3cQ_wA0nmyOs1da4BE6QvYY-n5eAysWDl_izsMQuQQzOv3DkmlJngeL5-JKPklsCR4DCtNP6usCHZ_8EvpKfXmUbZ4LP-lEmWVGizhVSh3XZr7lCWu0_6C9Aq06_qUINgV9a9DrFWY2NpT5p5kwBoU5mSqN3iOSUNzIbxJcraFH9rxcCqM1hwd9ktIfYo0QOohGThhfdDDl_njX2G72IuzztNR7KlATQw7Jw7svBvQ0dvvPCcfzTM1uCq6pouBjWrHrIp_4azQinplvoUkvrZcQ7mLj1fD7hqG2Z-4CmIj6rYmgB7nTmeD9nNFT6_KJKwOg68NNn6X3VyBcCSzheIv_TJdneyzH1EZhDAgFt3jgpL1m9Q9U3ao8YTz966tRBml-en8NfCgxQiGo4sXl1_pBnEDx8ZlIoq3K_ux6_ISXNcGhQY-8LYZtohfARdrkza8y0N8Vz02g0rlTXWimYC1s03SmDVVqBppvyL_8Ma5ATMrtmPnSfDGvPtmFnFIwLwybnb2r04jR3rOqsuKKWacmgF081Ygi96Wz0AxcCPXAYqQhnzyadaly1fH2odxf5zDa09_Cu2DLVLU3z75Cn8HkmbCO1W4Kay5wzD2ITVm10E0UOcp2bwW5jV03LkXXb1vOQdRpRu6oaACvdeJMlLrA3jBuUL6hfvF_e5NZ29AbS7a6WC8ShxL0-Ew14dRJN1t9Pj6-bMa7f76pSJD9BEogL3nmNCP9Dnk_krtNP14mMxprF4saRjrPtEwOzSTcNDO7k4grfRmwd_Y0UY4ltCkCW-Pqbxf62I8u1iX0FVIngck4I0pPH_iTUqtJWfvvJh1fooXfYqqvzfshY3859Jj4S-y8RXJiSyGekZbU5AzKVhld34IF-yyZ7RtI28W5fwX0Q5Tdf4E0mwQflZedtndjt-ipWyQWtIxvVpEMNTfSRzZmsJ56fQ8O7uZGp7GC5mKMqa9fSWoJkrci3nh91MBTOF5hB0-56Dac9CgqUiRDp27kionqr6jkjEaEI-cSF-ZOkTeaNawCYT80HVq8w3Q2DYCZukVodH6oEYZvHf_Gl4AzrnXNExgRsVih9VFBUCAoVTCyzQZ-1Q-pc2Y_RvVoVG3HCFskGfqTisvUSc96XdHiZxz1nXZG0GSvLWDO_pGXMAppsbO0hrjMWVsL-IzTXXLohfYLO-PHLbAmc5Ho-3nrSUYENBb67e9NY2Yc4au9FCWVsJvQIh7MbkLByCf9Nt4ToFS5CP662yMd4ao6izVc3A_7ZacF5Bmrcl3_9cZe4UklZsjqpQb-c'

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Integrity AI", page_icon=":butterfly:", layout="wide")
    st.header(":butterfly: Integrity AI")
    st.markdown("###### Advancing dialogue on ethics for educators.")
    # st.markdown("###### Your starting point for educator ethics")
    st.markdown("*The purpose of the educational information in the responses that are generated is to foster discussions between **people**. It is these conversations that help with the evolution and implementation of best practices.*")
    
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
        query = st.text_area("**What would you like to discuss?**", height="stretch")
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
            st.markdown("For additional information and resources, please visit [www.educatorethics.org](http://www.educatorethics.org).")
        except (AttributeError, IndexError):
            st.markdown("**File(s): n/a**")
            st.markdown("For additional information and resources, please visit [www.educatorethics.org](http://www.educatorethics.org).")

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
