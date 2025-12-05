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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpMvZC7xCAkXH3ufzfGq7q_FWPmzRgqLIcTpK95Qv-Vsenb65HGZnPffsHpe7fgeldXuhP61KXVy0JPYOZLT_cZ5fuCPSTT1yX5dqxhy9iGpowtlWCXx2jXjTa01VXDTS8-8uITd0OgaNGcVZ2giZwMaM4GlQDqNBzEZqtgLEd0AEfPx8a23GzlDQQC_PO08HMlNfVfSWw6R_4DHiYU4AktIV_lE5e-hGmGbzzgHaTzijObWXod4RXPp6835hgCtNc67JxBJeqwnw3xtdF3PbFPZ7UZq9Mvs7jlQSWoG3utAGPtw2sAB26WaTl2SUenHIjwH90Wt7nT8ntzNlhJkR2p5-aeuxwHg8MCSzWegKPSk5Fl0e7fpudJ9rvkh95SPfNbn_9lVNyztEkER8t9dMK-oC2RfLffTTvUgmF6bHpl7O7gMfdPdMDabD8lan_t_tUpgoUjWBQXsKT5haZyWStjjWmTgohUyILJ78h9t9HVH1mSDo5fIBbPPrkoKMREixC26d_gvaHeThyUoow9YSZVZNZn9GxuxfVJMyqsPGAsDXT0t8N10aYZqus_d2zE5w7-Z9QTKYo_6hHK_Rt8rUv9AkzmcRsiDE4zhWMVQirvrxESNHQXuoNbAIuEeEFq64WbQgPBDWhkkpo81jDCIKTGm6UvPviBnG7BwLrFTEeOKnly3Dua1oqJw1mc89kJjC0prJBXV7QAfBQR8Fqh7BxTMP7LS7a_QNKF8kKQ2_5Pw1fv3wMIh6Ul5G6ACDihwPu8O8uEbhA4GpPZ8pYlmGpC8TfmPm0i1ZezpwYuJMNI_K2QhziJ-NZVTD5_t3Zys62YKk_9q4X4Y_Fw5ZW4X0Gx3nwovoECmzefqKA7qTpl91ype9L6hnJrY7FspAMnUT0A5i6Vjn2d5wxW6h68JKqekeg21UhpVTVMWUQNNUAtFmkL-MuMVbV5_qzNMEyhXcyQg1N25lFdbmjNo3XES3cT1-yM0iHHBzu3GIrhn8TysnLkLk66CVw4T3draS1e-Gi6ERpmQGJrLBRb2i_XjseXSbvxOC0N_Jfk5Q2817GlXGliH9KmTn6-sR5igm3-vsgIaaf4iXg3XZ-hZYzWnPI7AixEQw-CrXZuSnTkI2oMftc_EfK7psshpRNMJERjWQbvg9moILfIk0TJOYUybvIw-a4U0llzJW03FUJx7CPdAcFcSzSNjrd8EELmWJBbqxJdVJ5EMpgfvIZ_dLIDe7DnjlcRDdqokq2Govszz3jBZCClFMQziglzXyxhWd-vdbDZHdJAjzHi5vXdcpxC5-YZNGfTzoka0mvZt5_dveMxsLqQJF1bAdNqyEVtxzUB6nRI-RIzFfOwgtPTpSvHga85Ok9lW25ZNXzJ7SMssw-HjjEYsaUfWr4x2h3cJr3r4xdGyjxT0Jy8fsWcN4F-75HZoEQP2EDS-NmeHHm-AIN612G4hkoGWubT3dzkGGBhQtUSjLJeZK-r1edzpL7mDRnmtMVnE51lcJmhtuGvTX3fqLDQxmDQKQy9VLccN1nh019zqG4tUSRKBZiw7bWXrN8l4UT6nYD5P-3qyC9ABGacIN1r0VDGf60QHzIM_27M7POUiYRjQZzFzPF8ls0b6MAgJRID-C-wdtidVVtG9njXaKdGSrWVFJa2STLjG1sxKjVVQDHhFxyUft5jmTY4O-ktyEq5eJ7EKmjZRq8OSXwx3Kd89MDSlaG14Uluk1dsrlkWW1Nrz9sN8IIIUHLAFr4ID7XKrdVz_AdGzZZAwxFcOJWouhltxjTXArGP9jIXuUt8dMqlDSAmidEwr9gRpRmGVxTN1jl06fDcXkvwhmhl0SvwPP2UjnBc742eaGYeGR1l-jertweMZE5Kp6uMoP0hhYIYRid-LoyPE4okWrDTP_wzEg18HSqsRXcupVVmxdmgvPQtW7FejVEwF-BrbRkNQZrobmv2aDv4cc0LdBc3lneCElymW3MGoN2uUavbyfBqvWaaDxQLzgURSctQenqRjsieKj-hey94uzLTZeDQFwnuUhz0ZLIJlN7c5DOFKBsiGdNzq0gQkwxhUMdeb4YmwfiUyYEvcYPGPvilkztN_fTji9oYp9gCKQ0yLOZtigmHcNTHp094JCU2-d8CiXsWmuI3iyJnZI0Wgyf-LHCwB-nS3KDoBVS2fR2683m5KDfeWI2PtJTPdonNUw4yanQJY_Nj1n8lMRhjYzA6glpYgMgjQij_-7Vo2B-gb4prjndj2nMWj6rSOM0pCtoZSYjGTPJo3IQruhE0-4_mMvNUWJLBvTGnm8QXSukwAHJIzYIUl_d2TjYK9aP4OCutRrn53lUUeeSKHxhvIc0vDR49Y9gazQhNEmNXTqI4DwOZYXSyqRcNBoF1FqQaGiOVoS8j6xiog1gw7AP4Kn8dF5MJ2hVYY0miKRtkBbNB77egxfU5X-4j5fQbm485MXlwYZJu3beOU63tQjFzZY7HrhVm8Eb1jLti_59BiVE4duOdL0o0pZMYA47ertrXE1FGnCYvBUvLtF2mzAcixA9N2qUbbUEelTzgtHWwNSym23KUnxgkC0xzkB4BSXNpTrZ7awxUz5hn6TFmmdO1Ubwi9yD7IwPFrNqkMtWnAwzrGdw-HywMh0XxeXJoiZqqOif66wPnDV9z6JwQLhyTSgSAkdTpoG2rjPYuUrMi9SuPLOcoeRLL-nTIL8HwZ45INF-jyToNW59ht11NdMdxOeI7Q2NOxUXZog4uJJldahLvWDgWgg9lfRPi2XXj5Hdm89tCMa6bQpPE399h7LAPZWnogkkrFSqESkrWR-2wMIenOXZxAm3qm7CAsh3b4WfXQqOf9lUyv-T9hoUFNkX29G5HUgHGtQJeTGJT7xsjEmAbVIBHTs8hBYCvyUo7nDJwWFpgab028AOwwIsksj4hKIVpVRzc3yab8lYif2ZwH3fu1o0b30RXcfgsK64395XebpAVXg118mlQlmqjuuBpjAswnAm46V-xnraWmvTqGgsdd16WLTru6N7HgXQLYqFG0GI0WrXQKATT6twWd-wS4A0XKNgTkwb3YXS7aGaDBMFKzJBYUDW9q4zbwYwrt4duiim6qfC1JYsk_qDJimExVey13HpY9Gf76u25HeBfh5bkoyNIQ9DZ4dorRv9XYie6dOwmmLWil3-TyOzkWVzfMFWlHlziKBIV91afMl-k6Bt4YsLOXR9NjJfSyGf8re66Lk6o9kBFTrAVS2smATWDuS2YqOiapnKp9RqS6ffqdlugUmWXF3IGVWLho9Ly7fJ4gKuAy0xk3hdwK013jauxeqJmts0QxTWyECo9AZlnPMo4E-eRZVnB0JLAkRdnHkLWIYffRDUmqgYwoPo3PJYEO9sWCd66qkjWAVjkN3Qt2LDditOdHUm3X7C1fNXWtkAdUW94odYi3Jr59ZumdretY1bZPjk-zlN1VjdbOw0ncCcdM96ccQHw31uCiZQ-4ARj79Btf_0SmXWOAfBcGwIlX_vJEvgdi3TOdn-LsFe-am2u41hXeZDnHpMze1li7USzWnkj9czwi2jISxmxL-YR3sJdNRAAf4K60of_8TRvRBtPZptJQMPFGRFsY1c9lCXTWdWf8OHM8gLDt-XVCalp9PH5quexBZzXZ3XaTSjrGyD2h993OrnqrWHp78GnUq46KTTUS6rdDtxWsV5GHztFBW6jaahjSoBPHoKheg4yOzbAlYjSDwFod350ByoHs26hTRSAPIUojj9TaZogqsr5TjM4XCIYqYLgYx35Xv8FlBOsaPe79oLyJEYMQDRl6PDUIJDg_S1tYBbpW9s3j904X9-9ub4cXn3ncJw_4eR5qipwiIR-Dj0hr2dmJWhQzGrbZOvrJLECWN4-vM2enX4axf_sUeRTHF7dHN-Jxy5k1AFB5sVtvLxKpmWOoniic97dkvOmQ4DsMfMrtQv72t0yDRi-v80RRfHdd_4Px_jnJI_GL3JGa6-YEDqNkjHfWeJpRkL4x4W7xqbFsyMc2NXo3pxqEGuEHvALwRHWPKpGDbaWsbR9128P-217_nBod0X_nXQBoD-m1-QDZ8gFbxtC1aKEvvMjZvKbr8LmatmOO7ZhoJ1REqhPM_uoLAPz9-b3lEdJ3DfoKHI8oWdQxnrclWZgnQUR88aFKNaUPz4SfUTNw_mxbyUotbiBjUO5z20eAYyBGUhDuJFgA5K-VuxcstIz4EDhkOVX-V0RBDG55TsZqR3bfz2CFsYRZE7hrTpjJtvb4NibrDJR4EP8gEj_0ldhfJ0soiRs-K2bD1WilwFSaOetzHY6VNG0C6lYr3qC0iQa0ohT8AxJ-YAzdkRMgHJoudz3N9D_R9Tfv5ate26H9mK_Jvc0mJmGiICK3kzHaO2DR-x-OL_gi3yq4FzHxcH77_tomX8iUGNz2wF6YITx-y-O9fjCCHaEcN8_-Rupi_w-I6d1GjEWw7ZAaHtfcmCoCldXtrG9DxWPHLfEMvXshdsCrljD4m6w4E1yoB2GcTDgzKPiHv7111-4qCT4iSey6girpAn-V_L0zJtDng86TdnNcHqERR65vkvuJ7bTK_s0jtaply9X_PH2XD7-zf-grbXGhrblkUFCvuRP558Zdj_v0U9NLqlkULeF8oDmOPB0D9R3wwe085s-8Ggt6ujTiP_RhK7Pwl2Yq5ULQtF7M6A3ot2ip8LFjcaJ3BV0ygmdYjBd-XzXTXzpx5g-w7w6m63WZAf-b83o4nWNDzwCYsD6n6m4u1hlSPbD7_WZMixluGhaAu17iNulTkvy5JQ8Cj67PgOHflJdK3A-sRx8tqwgi69VFYwnQ3RoU03raLY0y_NhCNEC_c2bDA3XodLCXHUmyjUm90BZC2cbeIdYMx3UVUMTFaOCZecj7TgUxpV3pMplfMjYTXYCbT9O53_dLjxVY1IKOpns9iDQnnRqb90XZu9mZtZELMWUhAaGylrEu5qGvd10MdAyzG-77M4HEK02qPVC66NPraAn1HOAfvrHr4o3X76FkMSsYKOk_ihIYm8pu4mP-V3s5BcFMq8lW5Abez2FXAS0UkRd7kcM4g6nlawXW2SJjo3wPZC8EX259DDderfcY3mCyUP7h0M5DdkHLuh5W0swmjmIm2ypVUCkxC2NkBJ5Cq4N5Kgynv0yJ6Uubyv9ohtmaA2sLSIhQrEqcj-XZnemkqJXBf9mQUWfPUIQ584NxBRf1vWyVXOcOeY9vEAMKRFzBbjV_bdLpB-t6eux7JpR2-Xfe684PLlpOec9z9SKEOlpKzMAICey7UNAi_59rol5ofDKFZribRz6NL8z3X1InJS7k8G02m6Y7daqv1YRZtdhDb8lDzhDYzTF7BaZxhd8ADKeOuj09N6x1m13VdNKvJi6wABsKKB117-4luRe95Eg-x5RoiVSTVgyeflq72Fjq39jnCh1S9-V5mEwVVTB6V7UcZN2PO3WYHtW3FTMpDQSCBHLphuq9T9AiSY1KLqsLbnvIMySgtHxWtpVhq4gENEgIAL_0J7HYJnsHiD8HJQ-k4OVc02-UAy0VcVWAGdtGOG8jaARV6FcRVgx9UfeZCiRDEZ3ZQE3kO5Vro2L5nE8j7PC49Z7EbH-NapxiocvSoic3_v-u6EgV3wHZZtPB-Jm-I1CPoIRATruJm4DdD_iD-MWMjTeOx4I_8gQ7XKbZvjmuQfSEnw0eRviWQQK9jMrnifn2zdwwZuG990U-H-swALWt4qfyBXyqqS_fOXFb7KK_rFUl1sjggbnlDzvXKxapVQvv9mOBnbXy3R'

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Integrity AI", page_icon=":butterfly:", layout="wide")
    st.header(":butterfly: Integrity AI")
    
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
