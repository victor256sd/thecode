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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpMvcVk2X6crbgSAUEpnvY2jtNOzWj25LNMVTC3-JnGO0F1lM841IhpTmS5ayaL940XHrIKOh95oC1UXJRErTj2jowfjLOGOsWVbJiEMCCchc30KL0obxDoFUsoj_q6j3sqLXeZ9tZ2TmluFCoOOQYiE_x9h8nQ93KLOIOO4mYTAA19FbpGHavuqHX067uI13MEOFSH3uFfxYNnzHcQyCbi3kv7jYLcAN_WCC0efrBzp8ouKCyYuQE2WH7dfcrT08j14ImQW_eXXaP2NZhR7M_VFoWnpUMd7pfRG7M73hAeF-z-JdGGc6JOC-zjAe8LnVra15JHtpapGu-YWstaJUoh92fUqVZAugJjPvOssHi6boxq4JDmousfoah4CgWiYqIMIN3kn-dhFONdsOaCTCIcVD5QJua9ULsGrn278s7eC1POyeiIxksAutNnWmzO7zkPZj7oeui343F-3yb0gRURKWyTgLsapBYy2rz5s5Hs8MiqA7tg0B63-FDepc3EWkOJ6LznvRP5Lvexg8sRY5-oHRaAPPiBQiUy-RkIHhtZOXvJlZESeKvaPBgpBQVQMNYRcOS8EXZaY-42-ZfwwpjIRM1PgDTKan1onrKjbl7ygKXltZ61CYON14BvMaemwTFblhS9U__wJYrSr_EgobJXzuroLdLTnZ-DRH0nHafBVRQa6QWOc_PYKl4Zr-oWw5WKAjdEPukzsuQoZlMLzZlP_99bH2L6BaR_IW6hA7nREfTWrfWnsU9GdgZZuKvy5hc5GCpQX4WomlzKcgctaa5tkUegFuwc9epGGxb1wctR1W_wXM-gunwLwH_TEx-kaVRn6YXygcodk5WksAlnS6rFkk1JXE50mI3utoGGHSNvc9krjgZ_Sb_FlKLwDDYPWv_M6JfXUIvPYu47QsBcFSniInwiewEkF5NXzCfmqL27XFBxdL8s8vs-k3xDhgWob_9rozVDqncN5k2ZpUjBsqV1co8m2lP985r0PqdcAl77DhViopHiID84biNk0i-merIKZppJASyamQWGbZjJu6pBleV8QQ3hE9PGXI40dMSF_XGDrfo0gTXb3-Q_5qTrHBSjg1k2dE6uuRHv_F8EXUGzsOFfzY2nAP6YOAszsMnfnIPRw2GGFm_vB_C0uLuJjqhKX-YUQrl7C-ryRFj48isdy2leC4_3-GNSHqANGLLaFNi3jsIaaVHHvqhU5VAfLSsvszFlNPd82XTJNObkMO-rO71KJGmN4TyYFB8Jlq98pp3w_2zGix9x7H_zR9NcV7RRxTE11Dfxcaoe4exA7mOIr1OTO4xboBjatwxO8MlEQHi3FZO0rhQTohjcs-PoeapDaIKfU3oXps1odyqT1UYo4HB3_WNk-r4euwBpHAgS9f02KhJ5N2BmC6i0EJSqjAb_VTyF-T_RNx_ztJX221cVnFO8QFsfGTtkNDC0cYjWoBa1jSq7PgeWMtEv4QTxwF1eKejG-5PHuePmbf1iy4-8Lr5_ngR9xRy5OdnZktc2WEBO2f1RNLWH9YJHNakh6iC-jL_weBEfF3RsL4mYsE2PNgQzkS8MZHSlH9MH-pZ_zcu7STOBar53JSskpmiY3KEstjkqJodgLwlZvwQHgusxSZgqOH--K8_PJ9xLlatmA4EBGeIqV6jpo9i4Na5XthtLK9AT26RwCg9zIuvno7CAl-xnb0Y78Mxk8C5zpvq14tIUCw_AMUU8jIGvMNmjFmm06x4Q2v8eysKktMDZAAnJI_uzJ_4n5PFPvBlFpBzg24VSYnBxrPffu2ydoIHF-d1theDbPal8Y-RCNmcrpYFNb87pEFulSVTmkTlCrx-GtUJ-nS-NoEUu8C62YslxncIvgp5v9dLH7QYunZN2g_oaduEhpqprJk1ZKsggiYUQL92U71U1yXxB4t9KkW2eitouzbIS70CHL9dixz56CMN9-Ag_k1SPGa-v0kiJlrUuQ0OS-eV5LIr03pomsRPwH-xIOw6WaAjwsIYz-eunPr9PZVyyo3VFe4n4Mjq9oORzVyFIFRF3FUmgfbN3HnHO_mChvIudTllGdArjlOHbqp-Q20ht2PgxdeHtANriuJ11hlUbkodScfbgyNYewywlLYFi9d2rGeJDnTxTxXrgq1LRj-JEVLdfjGiEgqNM0PFJi_SzNdERDSLNW-aaoKXQFXoFmdFLDo4cghL7E8Ii5M8DTYUPqDtAu41_RA6Kiks85d63z6Obqxpdr7UFZLZGJW9nTaV1coyAfMXrjWJLhwmDB6DABaiO1gS5grrr0y5-Bw1_PN_YvB-3fllUPhaYVNXN4-r79k_efG5kFhPlYZxl1xd-O8bNdbdx3Zze5QhTdS3gOBlrIiipYzRy_ZQgJKfRNUeoIXcLzShSADWESKGKe2zWiHT1TtFf7056gnohYedPooFQiACDcZGDTpOwyUb1vO-PKDpnFKg9DGax4GfLAdGz0X8-Ay_oFzdbP4iyCbiP9G57_xLYi_pduz-aHPrboQsoxqUoVBvOq6k4I5U2auYBZp6lHf6MQt9fk3H11q31iTss3QaOShw9c6Wi76Y1V-Qp1UIRNo_VuUj_MN0X6hBg0ncgHfH57PpWrsyh0CB8DvclfyR7Gfb7iLhyjdF8j60mKvh4tAuayk0x360Pt7nDfoEqAi8Wxldyx4o8XKKDJaLPaqNoy0W6coe5uzYaxOE52DNWOe0F9_KFa01qp-sBiQXPcuQe8YMCfRPlvUO8-u47axiXQg6C3CMH5c0lxEbb0PSR_HrwMWRxDxL-1MPTxG8cR8yrCJGiXmpqOFYSjX4zy2RhabZuNt81yFKjEPNNafYpjkV3lG6hHMrAe4drP0o56mbFE-Z2FZz5UkY_DEwv4ZUNznA8eIwmO1JJ-bVBURFsNDYjGhUUP_F6mZwBlGw_RLKp2Dn1utReYt1O7PTVDJx_89FWo3aOjYqUOkHc3632O5a_L_oWmVrIB9cBLAYmBZLPg7gHsXf54nwIjVJ4OWptTmNTGa9KTYdfA1e5Wp_arZcRR2TYcWNAZ6-GssVFPVOCEGOW5ypzgAKoAneJPYUAJlGyjE7PXK9EGYHzE6bDLYXFLdPDjijfnF_I2e4BEJkccN2wdUfThf4DArU5il3ZzcsO8ZEZHjogu1E0G15n3NbaQoZuV8sKuHlhp-Ibtk2M8tBfLq5XtfJd7WUcr1FBjdz7LvUJdj6IeqU-IrXKeXFTDrAAE7lnY4xSoF5JSqhsm8uxnaTCuwIDLs7EpdktvDYp20eLV-zjClBI6jgwWl-VCJ_QDISwMtY-TKvUehuLapMB-Xq3FIKJ4aDZhaH9dUt1gaGmrSyIBSvlLJhpoC0NsT-T6N8hPj0QfoG45KyN3i7HXYRcw8Ng5aDwb6sHfsdYgYJhYLs0zucrR_iWMl7QbIoqka7nzqipK3yHV2-atGGmS0BKy0pgyo_0wxX37x6LBilU8hK6v2ZB7dPEndaScLL1DmrlH4v1lieklPVGY96wAoWiKCvJuTMpvmUtcfVJt51vHPUY2FI-27rGYG1ic3WLwD54b6hgiiYUzuhgoccJLGQ5Fj-qWwVGeOKKA_RrRxe377c5bRUbe8T19HSnKfAU8Tyqq4PV7ynNzXQnPmCM3Dx8bJucVeifBMvgSLXmh7nZwKHVveJ-00NuD1bWPyIikFmkRRMiyE4z-FppztXBMQFw8eC8X-ezUsW7FsWkEUjmri0IEnUWOIlJnRwHQtUAUxS31oRmeRO879TPMZn6RrKE1ZPHJgjS7N6oOZpqci7r-Aiv2YAzrNdGKhXqlbJtWpNfKHZY4Lgbmrq3a1FLQsPmcLqSRe5EYbKl1i4cpDoQI2yqZPvtoFyEGaNeU_6AXjvZoprUo3D5QHfakdH6Z3UMtRMcOurWeePE4DyLsMmUaEqZWCH5autPs4w8OCC78vd6ttO7IHP6Jl90AffLR4hXaxSgJItRrBlkhN86V6oI85Bom9GMPC2PwMn-VWkiqxdgrLerE5m7IYENHKfNrsnkqDfhKVjJ2ul0P66ea6x6gLWzxxFVBRp9xWTmeo5f6ciCB1cz9Ba49F4Xg1rrL3ixlifB0cKCy5VUp0BbWupiDp_3MVcpZDFE8UB84VpdJr_AAEjzHJtKuWnMPNVdJ-K5LIu6Dn1ocejxPu7yafpQEtEHC0OyqQH_XtCFZOXlLB96U9eJle1OHBj4-ZE7azLRpiYr2XGZ_Ap3GbFst0lMHU5pDRix4Fs4dbI8Lwf385NhEr3gZ8iz_De08GAGHL-qbAqUU_zCj-coqgvsmj5I0TMGK8SopwubHv4C5LKrw_q_gOsrtRtInUtQEZ4X2Ez6BHsOjZ_jRbgOWFiQKPwnBc3XBqNHlMqnc1wMp4c1CcsejMZ8wqXBPrQRjc_uhDQWftHjmC1IcFakgG7nplW1Z8sA1JT1DKYVFVQx9qy9Jk_kzQdZpAsEVQOZVanORBvHX78c9Sltz-cEqhtczgEG24cdaiZlgrxPVkAvL4l4mepN3j6KAJSTy606hsTxU3-5c6vqNlcCpaSMZ3EE0BDjDtvCrBQI2E8f1J2tbVoQK2eBAkHEu60olQZ95XW-Y78SXgWhb7Bh46elZjfWVrsmJJZGtt3QpIsAjPPf0TDzAlUQ69-VZeSut6EKzWgLWoWwFVgz92JLKau4uAcNW9itK8x8JKMbZuirmuEDeP3A3CDRTnP3QGrM_0iR9zph5--legoqsPzcEjky39vejEOivv1prrvSrzX2U7liKV33KvzhsiS3NpNbwLg_iTBUxxA9n1eMBbNlnTsJtX77RwI4oCb88dqWSCZfohHiHax-5AfPAi1MpVkRSmRzzUXnGPoLpylJ7MH5zbhgMDnQZiIi8rPdxPjpsz629l-MXy3HV_Avt66guyC-3IggtfQDcjzZd-CYpqWQya2rqxXzh_zo7nbPbREWhGOHdqm-tnorZcm3YwTPdWk1e5LG9R2Ke7mbn-5rJ493WKG0taVyR3B9og46wTo-OTNw5xIy7GzZh1w1wisSOypRt5BkLKPUl4lJpkIsJbr1rBOD09021QFFm1-n9c54sbUogqsY91ELNJPOqb13H55o2oD2r9zve0JGk4HJuUQDupfSF8rBCFf22m104JTK_dXmZWjncAimLMgCRZDM3VoQeMQRCDVt6JogScyV-SC8VokPYXxpoOq8NxZ4HQpfLrk8HkPbAG6wu7wJoV57BAwOT7FBZRCrSpdkE16cZoi07PcnpTDcaCsjKPL5IynUsNUBP-PxRY3r4k9coQ-z3lj1oza8jSsCdGHY-FBnl4XZuwVMnvV5X_F_a6_xhYJOP1cu_bv-eiaS6bPrhkq_ViyxRtlnf5A2lSjOgDfb9fWVK3f8SWps1Tyvr2DHF_Q7x5_0wzhC2RasgVCgpZHABsNBS4ff0AfYDUKRazjUXmA39nF0cH84-MCrGoiWtcm7KALYsoE6sw9Pqw8zSahsrFz8OF87wPjeHnsCO5TyB8v8HktSgRBNhggq8D9GoTtI1mepVoCOoXp_ezFc7QZdrSllNGCMRZ3KTU-NkOia6M4LlyY7pk23o8cXbrqMa4uVLevKMRSchB6Bc6bBU5pTXOJoAvRrtcjeD_Jc8XABQgPJzLcvmS3t562m39g1I-o1qsSQihWoFs-KgBJTC2sN3qWpwUwqO98AHp3zWSsx6G_bcNORnmizCvB98BpbWysBDxA3NRcyK67kWjk7OR8WrVETyC6XQ_if8S9iF80ncaZc5Kgh242wD6HqSWyk2gncMZpcm-oKWmx8kp5eeYg-w=='

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
