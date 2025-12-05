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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpMvfcsCZV9EXI2jzvXlX1GDIjymsVi33YANIqFYgSSVgvvw1gvOmIenq3NvXzrfgKZtTjcsNMaUE39sipL-eq0A4RF_8Ak17yvCT6TsdkXbaPZGFJdSt9cduu8rwe7UJ3bBGxVSw9DBW-wNDVlCFYVASExD39TKxKMfQbu5d6rNG-ACLr8vsv-3SmvFN6Iv9C912fVHmX40jmmPkT2sNDPGUk9n9Vy8_jgAHziErz9Ktz6c7YaWQVbZbCb8tntJXhXy6Ec7Qk9yiDTo_0drcnqOveKfAUdlln-k6NEKyx5z2uM-fWzw3f8EonfSqCcBIfuyKkA1cw39gGxDiakw7SgEdA-UgWEAoDWS_g5pPW42r2sXok9IkpY73cWLvAJFZKRALkd0cWHrleyz0PeihgXQf7uu6abXHrdXc8kmUYnBZsIpf-0fmRD5n7PU--wOlHveCs83sZQ5369y47VL_Gf8CFBeSWJ_6edmAwzwuFR50vgG2o3BK_RPSiJ6og5okIyWjBgFf0AJhBmoLaMbfrkTs9GpxiPJmJ_vX7fyV21ML2_vMJv6kJqPuBZD69hiGxPk-LOVqws3TQ2O68hQNAAIjw3VcP4vT5Gk9k97wfwAeUdHUi4RMJavxNEm_7FDiIW36lP5UKj4-vZrX6qKiQ67SYG19Oss8PTZD7cW-5K2GhMlkzNtdptp5mfZAhvWQYl1WalIzuBd1FLzGfvUBHe0Sot6n7AbStiMYG7GznJrCESL-Fqq8cMYT08RFOSTp_7ExBoyVClOk4gWzh5d7dsLhFri9KbaALJgNnMPBrxuxv5gWnlpwtbhJLI0TArFianbBj1_36Kmj2W8CZpi7BhU-9Cq3xgwAy_5YZ7MULMLfWLMBzExdCfRdO9hdCGtR3609kesuhfS_tlhh_hRsa4NNeZcN0oAIFe7XCs4IqmqZ3z49ZSuXOOE4fS8XF2c_BMfaoWMloQEkjHoTjr6CgDqnerhbJbY8MoS_mWvU1GoxjFIvPN_R-xN-DIlNh09rd1Pt9vEu-i-BppcunvZ18Q2J1qEXL1-S9sZ-rQSIEPJbQhVzetNmgeaXoKNKo41ZFW_OEtZgPkNTkMkpQi3aYS2RWCiHb9R7ZR4i7n5d32DaBCNugzroR5lMn4MgR3SfMHziKH0iT6WnajWKbfS75GJOFyAoTFzytjzgLU_fBdVAaOhbhigE8mbFC0aYnAH3VKDZ71-DbXMISXFbii9EyMJQY4_DdgVzkHqiK41Bo0S0InqTmp-OYsD4frQAEfd_srWHZ7gvmyLWdxOjy79sfdhM3QsVepeoA2oiy3HDwkEo2a1FlAy3yiSTuIOTvHcIN_Z3aSuPlMwvlrCX7dyZLFecSHizy6JD5ZHoEECJ3PHa-G9RMXndK1oM-dhVy8rzWS4VWedR--RBZ9IMWNLA8aT5B7PAnaNnwMx06-lStmKozwt1mx0nCennHkHMcIUxvEx5sPH1kexyKJPQsFxBFn4nnVAUbMm3em8RHaSKo1Xlqacx8q7m3VtQI6juq96oYq7uvlj3rJq_1WDD3OGeVZSeRZbJQ8JspPjIH1z7VQRASr-SDx9BcDhZWByE13EKUiTb5FGsiKW1YKpyxQRym5EFlJkamSWuil2enTr3OSkC0UcZzb5vFK6dq-mCFTuqqtemagv4poCMbuNYeP_wl-mrJh5CmNiiYNcVTyThYTGQGHLbTLbP0wH7I5Sl9XKjHWyZev5d3tPg6xEWp6yH9UUbSfsy08Py3p7g9dxKHNCsmLPTa-bf-n7C8y50hKJ97UkfL6YeiOGjZFow1DNWhXyuuoi3SFY-0NX7oAeQJqhpg3AiKwFqMhM3QLRACTqWlLNy9hMH9ENVz6NRSrNvo2Zm6Li397Lu44ofXNbL_wLP5MEsXBM7jMYP-DUYuXSMjJVr2dAuCugplzLbkTfFqCOYYgZtoELgKAFW6EYhzHcpnTYzohtP2WPiHTbfskYBGTXsz4ItchlHXD9Z3FgMQnB5darxMQJqrlDZMdsqVRM3_Y2qeJtZYfswUU8kEDl9ia4bGyn5lXc1gfwzHzpWZakmGBpmr3y3Sm_7-nRoaO1L1iumzEUVcSfypV2RIuDwGnbdb0bGfqFEsaA9q6p4HlKBNR0myiyUK0aME0wBdcEpJKQzeV9FnSQtRQD7BsMjX8RX0P0v04G7OjeaBLbb_I55zt5SxrC0KnzS2m_ZdLbhmy39F8rI51o6Cn_7NUwzIY2PwOAepjZ_JZ-wftsDrYX0_dQRXtA3ZjsuwN_Dmd6RLX2Ox-NS_PHX-90TmyiFtmAaNtkvRQfNy3BZqURjHcXKfVdASRLlWL-1vm2hHbeI4zGGQqmsU0IDEstikTBlkwUjVKssTEigtTiIleIF29-j1CIQX5p6OxJkbR6JlutN5_ZWPmzI6aEmoZFPEOYOoTD9e1u0J0Oe4l3YEKt5WtOuM3k3TejgX8Iwy4eemaAefozk8ho_OYrvGUgdWfPPVI7TVvWjiQh8Sj_JNRcw0_L8c0aWQ7dh1ZtT_Lo0-kBiaXvuZNmX0wkIlYFhKDaZuqr3pQuiKKc30uVjWruJQ5o56f4HD-qmFf2-118tTK1Tqea5FzIABxH6G1s4gycGyZVyaMf7W5a51IJ1fXPq_9-cjrn6AT5ChTu39HKZnjZqcgPaHg7_xg2nkzvIi3nWwticF-egaRy5PuoZ1-kj0dIa0tBT2WPqcgHOzjaXmZwpz8i_0JBl1igXNF87qdXnJZacduXrE1bZyADVdzAHXj0prLas6fgMOJ5zDUxoKYtvyXv4LMnj0lCduf3JM716TrraF1mcfkikZPUH8GpXo8ql5uo7oHdvHwS3F2zas0Ho0-8LBsziwYDL810Gk9kN5SDpoGAfSW_uVjmyq5X3aHlui4hOT0-MuQj6j9j-vBWUTiNPpc7lOfY5GUIdYwbwNLnzmlVzzE7XpcY55LsesELPq-EkBTwn3PmO7fLV6NJaOECCynZ9qMCGDxDXvJiidnBuaPd4Jel7ez1Plrvv-EuABCcjylGe_yM3GWm2_5-AS71tpST-qJJnhm7VA7_owHRZwKJWP9C3dBUbQDyTESS8P_6FZz-wBuXP43tVKYvSmMGFuOFdptJWJSNovRt3fbM3J8RQg6ySSYI5GaDx1lh-ffBXinHYAGXDnHbASryJnEm2geG3CWMV9KZufMRKmbgaIF3wIy4sD-BMXtc85GtiOyBrAmS_qm_RXtIdt9IUqyID2kF2Fawjsvy9j75OPM4cNJ8nGFvkS6NZNX3U7zpxF_f28ituhr10iDKM8cTgeiduo_HpMgLlU9rWRb3U57uHmlemEIroKE0G2eyasnFEsVbeW0BbW1sURCJrknA_dwnHqd3W35xbCnJkXMLZVkwC2OqW-qLYAVkdgQIDkyIksf8CHovqrYTi6_lXJlqd66-iB0pZMyvKHRjyAHwWn4VTzyyl-hdLokjx9246xOa-9NhJiXXGTZqdVe9WltXCTDocERYKJQ82LKcR-kZFW7zvi61LJi3qXsTbeOa2cKBqBaIWVxuihZO6Se78okU3tewpUe7DfJQwZcbPQKlUpbcapw_8ZUKQtGosDMaSFjkooZZsH8DYH08lLjRExELMR2o7vFZwAH058a3hQUjbgdbiMSmwgY4nvNha6FAyfBa2wKemVbPYVznrQBxS2Lr0bmAru4cVrJVEbcxz24TYmquNTH2SUFJEnZ3sNF4WSjZa8GDmHkcZy0vciPgeL5VvTy3B-JN2zTu9YwLrYMLuk8LKIrE4L6xkk1JjohyKr7haMf5E7xWdQTOmKia1ibiG8H88hIlVxRLlmUEBBLiOxUFmS-hweWk0agICYLbaZm7CKdk12kOk9ucKgVYXfWwtbgPKpwXaEFnUGoZv7hcf0uhercqoFJqBeF1mP3NAiT3FyF4vB1j0b9f9Cj15TbLf3asg3i2EUpJn8eJAEO9jBeXucISg2N5GoYBq1lLWA9bRXMCjrywmlMyHYnFo2cjkPuq4i7RLjboa1xom3suvitRNBI9EN353Hrv6p6HDHUkNEI32AYb-RmSTx4jigVl8G9-CZCxBqunoVUZ2NdYlGYxd4-cIAktJDOsDTvVExPrO012a6y-96MhXmQ2LWj73YWFZ_qpQq7kz0jfSu-0c5H6RIvoDN13LaorM_D14gluCgrV0Rt8KE869anYciu2RPgtYCmGRAxNEWzQw-pCb0Gpo86r57MyvxfXelR3Sxhfx3UEhirN4VKiVHP5HN5rdkCzY8QqDWFMZtz4JGJ4CLiKp_8VBuVwtpNYu0yGYPJp3no5Su48pt1ihYZQQj1MmNNPhmXLhF6KcFwIqy2Y0oJNo4HMTBLIBRTNrZwy6lUGfjNkt4YvuVXo9J-QndUsqstwoiooJtj95LVjyP9lrwFbS4h3F_AKTTVsX6WV6CRq8K0WAMz1EZHDcsyF7l_2iK1AFnw2sTB6mocxEZNiQJmkn1TL4-dN9fq6F9OLqb2kxHQXGNF5AuqtRFiHJ1wwLH078ZC3K9DodV9qL_vHkRBmQcgOVpJPthO7HxMw2j4ChDo5m-olX7MOg6FNqkREiI175guoSlRRxeN09LTrw48RHvHeFPpa5gmNW0rc2YRfzkOqTk56PU_Xzh9kr2ojgV0jszGOjoAGY83g7pJh39rxpjwtdynCPsRiSSMvCmvoMKMm9Tu8mrN83ZsVie-BYBgjjCFPIXnGpkLeXYdIe8wiIopMeYmtemGoQRaPaaAor9kK3DabuzlR2ywd3p__8_WHesxpG-Va4eW-K6Z1-cMhoNEeuZpjMZBshmk5yOao-QuqwaFwctqXLJOz5I5v-rGk3bHFkLCFCPOMakkmBNI83ktl0Cfr8lsRsoeuUuTPOxDVUslv-83qssw4DwrhBf3w1HxaJqHM1G6tUF3BBwU_Bd5AEf81s-S3rgDK5mGz95TglwUqVFBVvkxbB-z0WHzphAhDSlmciD4MxGEaNnwZJgTisJbVPvCDj3AAfJR3a_D53kid7_KpmCN4TaccneptwGQx0RVEl0FG8F1zdqSe8HUSkYhes36JxZTQ5QB9X4W42rRp42aGc8N23CsahSrcoAp6mVZhqMowkHYXZLNIPk_isHNywCUheQdlvZvLbGWEpXl2dkBG8-is7pOGDdotnLyW3qcCyuTDxtyy8_olg_k_UwLEl_9dckVGXI5HZ8Io0-toVk1CACwjDIEu9i-xx-WuV58wzVNfSs7PIKRGA1kyS7njQi4q-yCPSJz81DNNef7G6Ph6hs1Gx1hurC7czJDnBdiQGwVjKl-kX3cjzIWbXybLPyGGDT4TLTumCETngzYaKz55HV4jpYftOM-O0AxDMNdSuQq0cqflMjK6WMaUyiGRQFkdNS2PNhVMCurs0ZotDoNtOrL-CT_Y-VhZvatpNMUYo66cmjLZ8fcU2Ow7ADzYGrAE1uynzmF2XZlsHOvD51zUZw3GNXd2AcRNzfrTYXCikOwpWG-GuVU-uHY9ZxInxE-25c_XJlsX8UmqTiagxFKgILaL2u6vNmSb4acWxmmaRwXW2aHDBBZFTrqL2qR5gYsibdqiksxpGczISmq2FfcMXwn2RiqgBYEr5ppaldNbT6Cpd_2_hI0iFComdaMmQLZNSFGDGWTupoOPxfkgUoJYMfWsgUCeZgXWmzSzgYPAQgYzEHoOtZJwpRw5JNbK6L1lhUPQ8sWVA2jyemx4H_a5Yb9ftyRcPxM4sBCgBxGM1oUI-DJdWugltBA_3FkMF81T4PEWfuIcoN4y0jpuWcFBbehLuooWPHmGHREgF0jkCyLyvUfrJA7lCdGVdRzxMMbUF24rJjBi6ZFzD9DC9B3ktdGzC4wPJyw8kouOzrHflOFPxvD8RRAmmVy0w5GAFBuor-5ummVcpaH3FZ6P8FViI3SQI5YDcj-0Y='

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
