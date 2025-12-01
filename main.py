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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpLOxHatE_PLaWvWcscD97zCd_MumG1sLk_v_yl85T6dW9utyN_U2lx9OkDIgbT79E1mmGThmoanz8_Pe9Rr9d0UaAAXFER9pqYUtHZkrPFdH7-P8oh4BKdgXYSKKpSuyYbpuj_xkF5dCVCGXZf41TbZEmPKJM_RkkUnptVYNj_1GLGuKl0NiOpRrnWLKre83OPE7Cb-lpXK_U4xO6nW5RmQrOEPvC_M43NpK0B66hlPvo6JTf9xMID2UEeItwV0lyG8VYrMMr5PXkW3gnEuYTDfNgKVLiCK1MeXkjwPNHULe80r2coAdSdz0P5-cclGMmlSz1ffIgkqdrWdjcdx6asTgspFTEV0y1PfaAhfTYodFgENEUKX5y6wiQ1zpRnu9isLipTIN2k3Fidga0R-EmWzQ5MCJg3zvj1Ysynh6I3-J_U-p9HhmjJJ1kENplw7U9uOFZEQNI5w4XNO_gTL24239k0ffU5a7aAEHJe_-TEogguFF1GN8xRn5Z96p_EHT2NAO3y_mUWO0NgA9WDYbwgYu9JnXAMBnmB0xJae_VDT0LhK4HQ7HAxB_HP6_GCZOpi24-DFhiZVFIPdr-CtquehPotdUbeY9cOEsqwQOuYQHC03BCJBUBltq2Abnwh6ZjoDLLWc_DvXzHiB4JTYwzzirXyuhljVXZ73SwFuUqVVGLxOys8xDVxSlQio1sYYdwb9sd0vEi3I3ESKzyL2u1nt9-FvrFloNy2Zh9RE8jlkGfISsrm6Q-q0z9wbwESYPQc6yR_qrf8MwI4q0HaslNumw8Pj-zJhpBWk4Y0GdfVmuq76hQIENbSVtx9KBLCu6DMICWu3nEXt_QjhPYzTM0sKvikxBomFXpjYH3ZH4pGuxwRjgYWQZyKVClRQvxc3z5norkLGEHylP1gLf2sgvtkq6xWlaxVz3LZUU_5xK5kHwXsH8paVzkQFDSb4Hr2k8IZKM8q1xvaNzUty882OmbuqYRyVTPuW4TI5jxoQhxLFPHYbnUM3UZqIzuTQ6PonvcS7tc9HwT28-33fZDZRUAyKlR_f4fF5J-7Y3r6CvJYv1sNp5BreaqHzeRIUYbW1B7apW_wwBgdZp1tlSXzXrJ0qS4-qAKL1JuXu69XdxSE13-aelJBWQqXiGR3-O6IQNl7cO5oiAteVnFJEg-42ok4eTCC_MFVC-XUa9ESf-G48YXG5djgzZ3T2KZg6OupZF4DSV0oanZ9suClP2EsFC3uqQIq4nRzlAkYpgiCAMP3KPeu_EfwPclOE7ysMl9fxpbAye3kXzLsDv0PTqbMXYMHjFy2Yr9Z_yhvcoZ1kIbJofBCVGstQ7sx4X83B8AmNQCAs9tJR-fXvukMnfk2HGwgnuQQCkrGQ_8jtqtlwdmACYoAD6lUh6SKRq5_qDwo3KlJcMBpNK52qFmTMu8rUPzDutd1q2ppRYNfKwdDEK0KIqmb_6x9vNb6dgSZfIQf_onzx2mvUHkTMet3U-V-kR4Dg8PhrJL5zSbrkvgsTvFxDDPXYApizywv4ssm6kNddPmIktBn-oSVZ-7jJTvu6x0NG8Ez5KArIKOFiqXubmRqBc2Y04nyKGWSg0I4LBA3QFRhJIcogmk-rAh65grdNKnM9HUK6owus4kmqhd0_CNDMCUXiluE2kfz1gj2NWPZrV1mzeFH6V-OWFkK3cZsPlBpB7fiU7OkjJRnZXKmrw0z6WYKwAKKkSDpUPnJyCmC7mES1QFbgsLkkYsU1wF0JIqMOob9FER1hRmL8-OIPpKVjw3DQmr6L8QZ7wdJZAYzB93VA64U-8EF9nYHRx-e4cfQf0_Lissc9BOqXecfcAFxFdtMV0hxUr-qfv3S-syqU9C3ODI04AgQo1ZVa3y3D0cfkzwA5UHHJAOedsyeZ09a-Uiit0WPE8gsjjCbRIJ6P-zKmKdO0DZ4jrO3KnSAgKVjnu9hnoBLRumt8VXQRSUGbNy6fQIhZHLgeehpL8uszVRFbCUdiBEaUoBplTiyQDGP5QFJos_8b1xTmsz9TxCv9u75Fm5QVXtqIDbN13aHyHqdjf-tjUEzkSrXXGqAfP0u8tA_wVpDKjeczxUjZLbMAcGsXpStQFJ35zT69IVceLVfd__D-6dK2Rm9aLj2eXDFlPvo7YX_E13GgDGz1ryk1Jbq-IrOI3BNXf7swxSGWGzrnrfF534lsA473B8jpVdlEE_Wbq_eDLgIFYGLiocuAqsvpe9vIapwGc4pva_3cCEpDs8ARri8eP6D0l_shSIHXINFVRmNkGIJcs-LbzzhWxS0xjKLYWjqVztwkw9-vMO04BZfuBs7mZOKSCBLfc5FB67mo7XkY2xSDTz8kw-OOTGeVlB0fDs95CMmiFb6mzQrzPJd8C7PrM_eMfIbUJvGpQGfbdAFPuRIBevc7tVQ8aeJ7n9mzT_p6qItyUFPxBVMgFXNW1p7aj-X2N-zA9CaD-JuT74JX9p6LPxj-5KCWRBS5C9huvV_33jm4G1AcNZIvDkx74uYvJrRpAVyyDWYMwqPHjRopp0OyfZ9551vqc_KXvFNTSKWYGpikGCwxN8OQzDiBKyC8Ng_SqLtI8UFnnyFt30DHtHMFogrOT5hQzyMnBTxjsfbUVKAXc5mv4CFJWgprmSUFJXFUf92qUmmrZUFUtUHumbgj1niDF7gZofNsoZclXwX1s2wJcs2yeXagjPiYmhUlUM1xkqfzyTWxu6Itr98Jfj4_NgL5zWrhTxFdvXDAW9Tv_YkgGiSw9nFe8wTf2K4cRKrSkgHt5A2q556GAXV1a48MxgBSvKqm5Vz3PPHZDpkALHmMyj_iXQLza1pIS7Ej_UB8IA2vo36Tqcgf-c3Hjqj3_DtgiXTXECPrPLh3PWfLvEnS3Zui4ID6SXNypMSfqRrAPHUQzmtGUkrueh4FAzN4IdHqMEr9GqtArKMQR7bCEHJs5npD629YmautpEmG24z3YlFOgF3oJ-rlFLOKVKHhv0v9P56o7x5lX4McS4ZtO07lvmk_UJrhIj7yNV0Fave1jZd7jYKYvWUUgDlY1pGogoOrYP3HyE6rKjEyEgCFsB-LtyeDw2qd_yh38vjdWNvNkHV_vGOYfoEeZDRKYRFecWO4VyRQv9dbyWEWFPw-GyQ3cfZckRh2vWYbP_gnsowP_86KPWardlhNT2Yg764bYrwSXB-XmcYK6C3c4QYNz4h-4bEuPBWfegW4jQLJ9j8odhP3Bw93zNA6TMMyyAVUp94AkF_vU8cV29trEMllgd6v8qnq1j6JUrKwA7D6C9OsbXOeACNNRhZlPOh1N3BF4Zyv-EHT9Cvskf6Ks62F0mLDEGNlXYRzH17ELD-lsdAQvx2KFiO2QnXEU2zMf-TA6L5X6VfXzc0NVSd0BNZeLJAiRpiU1PjC9AwUjcyFdwETzzLrq__cxnl6AX9_3P6V4Wxo0-W6ctVS2WroVYwmu4pohsgbLM-BCpVCW4pctZHcBflEstwED6vyzge2QA-cjvHlFe2bEgZBauwjhjrvYf_WAYXOZE95w3dOtJIBU5ZezQg7JbkU1egzS_CoGgvgPaT3_h59A9fwl4ciJVvNQqSIU1oceEskf5lh0BDKnx2jBNOHSZmO3LYeCJ0aYRe0I4kAEHhJlBXoAnrAQMmku5fxht1yK8PbOavUziA03dtuNddBYKUpvInznaxaUR7DvIozrfjF3C01EmKj7eMK86RVrgK9zpj0ZV_pY_iX96fi44W0aE60kSqrPWlCB8Pbe4Xe1tXr6ygz5WFQQzGpgVOoe1qRbm8w8V0tpNoLPxwcWSzk4ZQJcWxyvV8qxKRmE5OM81lea9biNV5rH3cs7rw3me16e9-AffWxM0MqKV1yqIpSVdVM-MYqghk2SZDE5TRlKgUYiipQazXwzlEGZa8OY946KcFV7_xhylYyaVULZHfs9YTC1bpuIKAPhxsu8lX6n5JGLZ7rGIGd_8Ql8l9U6IQwNsH3UMNDGsrG57mpYeRpX2dRcNxJNuL_SjmW6kOiNc6czV3-lBR-0uwOZsvmSNJcBgbVh16PVCk9qFdY3WI5CjbWYSPVlV8UVLIjd9qR9ldFKDBsaRc5ynvNn79d5MiDDG-J9dJTu1TAvM4rvyM5FmpWk2-IWkhbyFxSNR75zEYSVT41tUvUHpu7ryEF8fr-gKmZtsFsXrqNKHZejpdcAA4lmG0_WP-fOhB4idszornJNQbxVBe3tq7H1oPgnJbA6a8nNExAu_Iu309RUsYEgHNpvK3Ju8O29p3CQAXXrhWZz7VmP0L3jKOlRtvZA-5S_ZJl1OjWduisMKOrJ7FtugfKtBU5uU6J0Fnmp1tE81vMdXGACdJhUyxRF_dSRw_LepTLS8'

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
