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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpM7X5QwuFzJHLiZrLzWfgPd_o81aIwiKF4GwEJyxObpbMSXRfosC4_pfuO83p4qc5nZzyhzF_d6Sk3_o_oWOwGy1esbDWprMIcpVPa0nTGO2aFTGWplZFAD0Le3i4y-04YN9VL1Pwa_EOfwEnx-gyVGRht8ZgNk6FJwIPguC5kJloIbzjQhDOe1aTmvuV9XZZTDSMB-GB4aR4V5_66aa_0RBJGSCl0QCkTgnhl1kAI6kL_qTERfYi-_zY4Y-D0fKJJydU4BeM6Lt1V9-5Vv_oNABEhTe6EXMr3tl5T7pgzNfKACIM9FBDIPCx1k1Eb9WMFb8Y1buSp3nzSre0wWuTx4xInhg3bFTdlB-fiApMvy7TwY_zjv26ZuiSmrMTM94qJAQE-Ci4yY9EAyGxGuEey_96KjBJ3EtXI-LJN7ZCcv8F2kw_mxefY23pNdBT1Uu4sNpvy2HneZQ6P44pc6zA8Hub5G9hBSEZUusn56Jy8WQUk6gptN2CxWi8MNmEQM2te-OJ7SsTdItUGcVoRqF8Q1hZ9cwIwSdvvw6d1g0JnR9gaMniVP17aMz0yae05R3NgUdm91YTRxFXhQ_ACtY4mtFSmYAnSb3UW_12O9c6Dge9bFOSuOPGoYrl6-z0uHrgIUk1UHU4kMXYJB4U6nU9ksgK6CpjB-MSdSl7IYRkY4lub0NX7FEMS6_q37FdNZ5TVRJ0r-Fg0xf4U2vynQhO3RWa8d2elOHQh-09XiIHWDDi-53ywvml2_YRsAMZ7p5tf1TrJnby-IyhBo8Ejn6kiSdFP0dOfMQb3G2h7mHDaoyvwwzZZod-WQ4Q8Tii6gkDD4UHdC6y9MLMfAxVKPg8ECMRrftFJYu3YsTkxEzcXEry4wAbwf7PzPKPUeGelCIb0ZzhcE-tpxYewMs5STwQk0xe56UfF8Jbrh4p8n_835WVH1MgIdX14lHmFibfXJplJOAToR1dOzbexK8679PE3FfF9wcEgyc2Mt1X93bWKwAoe-1YAogNgiLoF4AJBrhBsO2KqcGweUMJJXWDGl2UaDZNOLUNhUCekBLK1naCXghDxqp864VGtuh1_va0rqbSXejo5KpE4-j3MOngWvrcsLyp9Q5EspqdvnT05u5wWeixjhplaBFRMVvkBCX6c5iFYwRxO79CB9ky5gUCYuseK1Bgb_vLYqHLcmOfSSzQv1aXPeN5x4zFb_CzLEyL78oWRO--8e3WDoFEGiLpplx4wyx665wnrHNqLBbd-UNcWPEMo4AlxWMkXsUGbrNg_BB8WVym-3RFAwPcMHkF8M2Dz3m6uoVmPrqPYEhQYnHFG9an-HDlZ4HINb0vCinpvHiB9SlJ1CADVcJ67C3VkdBLFdYW3QIXPIW3_UIkNfAWXuh8q3h1OfDCzQgkYF_gHXrtgsZt1iWLr3DWoWu3l4X7mXPXxAmAfI_o1m5AB1CI13MygUcnxvQkuTylzAtVfKRq46dkQKrzXHHhtNLlCDXg3IAitU6ZiuHZepFjcjTD9TBS-rh5OIqV5MdOEzF909DC3oBtjzOkaWH4IGf6JYGKrxDd8frVtNMwD8gTc-cSqhpC8T41nR5g93nRm7FMXPPGw1qN4vrX9rQt50rISlX9tY_cjOtSx03CE6NDsQlfQOd8XBZ_1iH74jB38UMtrES81zyX2BUMSgEWcY1eM3KbXMnA3Yrv3s8nFCV4NlnEhtThBbVH9u5adhcj6zo9cMHHLxawothpMC7wzH0k9AB9u0v9NVyYoZnwId78iMDExj2Na3A7xNEZLd5G1FjFzWClXDQ4PhI9ENvpOWQt0Cx3J_wyDiumoQSniETN5yGdTancBwi2jWMzpTIpvIrH9wFYQD__UEiq2Cy2Kplzf5LlYQUUntGK8V69-u0nS6tDHUbWlV9_IcUvSQKdvAObArqCatkrvVKKPAl0mrcJHnviL656C9romTaNp_NZ3a_V4jYgnzKz9p-u0gIU420T44xkjcNbr4vh_9Rn0jGVpPn6TcStwQNFwTu3sfk03M9WSrPYsK0AJ0_2m7ueXMXlG7Pj9G2rcb4Vsr6PCw_xu4cFDlQCiLHCjk8Ix1cREIyljj2ty8aGDaehBRrvMAvI_IEEAK9yzLTIIq_HKHc9iF1AoeQDqmhdeBZpRCavvUiwlqlc8hAoHK-ehXAGsdIV8bKp06fXDG457nz7P_7osc0VVbY8Rxk8VEOfohIYNrsYmJTcF_7alLKNyhg6ST_pF_RgAwqD33ZAFyPA56Ssys-B8-bMlg0Sjs9NcxhawM55bkvs8VGmjhnqoo9IQ9paaonpj3jXgJGV2IDvcmE1HnlkACaW9i5UX-MT4eTnO5ALKIWR-LFADIP4WwJTYOShHYYeLwXXhoADBgJN-gMQA1ve7UfJbg8t18BqhEh4sJDfpVqxi3iEDIMsfmSAF5iCTVGKwrVSHgg5kG9_ez0h5vAoXx5-A1KHEr9RP9TGwi0rDr-eh0Xbkw4c_2esgQyIUP2GJP9O8jDJv3sqrR35YuuIFd51abLrmP6CE-V0heWBIFgRGxupZmrLUVmacPZFWAlChcmMhWtFwcbthkBiKgwNf-uh91OkSBpSfwBx7Oom_If4wHHG0sHBZviIYx6igva7MAfn1Qe0nsR5CDOXhS1ubOgFxUzoHFrMJX4palMFbXZPlOKGAGY1NbGU76lxmyvehHGUyF7DrLiECN2n2zJpxfzYlUQLiH96d8Wlf47CuJPZxP-ZtDOju7q4u4Kfg0kt3kPWM14LoRbCqBkLbp2vwc-ZGCyLM5O89S6pTc_WEWQKCX58Cxa4I-Sit2jWMquZljZx1yXbH6gly53UEbgcswdJ9Pn_KLGKxlGVsGpyh6XDVoV4FnCyE17_Zv5w_jVobNsc661FdpZ68Gl1dz7Jr8OzKOi8YzFJFkkGJ6k_TeMGEZnQi74y6wtYAO94G-1vQCQr4Qq3qZFJjP__m8T-QV9UthTgac_CVlSnkVK1uBi_CF1xj8K2PgZedPCRpzHihEvoSojpaajYee5IZHNU3N0CPUMlOC8dudc1j17E5kXmk-teGV44ssqvfWIBpUNIwH7Zpo5DIxzq4hHoRZa-h_Dz9kJMfc-1YBFxBGTOloJpYo8l7dZxop-bY0TbQEXsnIYeTCVe4zz3wqBLlhLIwv9gVV8nJyDjJKFh7-ab6LlxdSV7h_9wsHS1USp0ER0ZPbeow9ngFZ0C0DrQIIO-Ztb1sSPgLYM-uCk_AMa1tqJLpuVr2I4_Dj2N5i4MUrnS1UhblAOJJVLPlu9ajULEQ3J05ZuGj6bg8S6SCvVzRqEDaqFKQ2CxX-vp38OgL5T57qIRZP0kL1vlv7WcayJb7cskNdjQdlvb_OBBETZ-cq3YuxTNTnYzudnXfLXuP4HC9XW9ckEEZjkbIg87J6XRpd3KJPY_Mh5zb25glCX_-1awuY_b9b5Vs-ZnXoqFE69zcBoRCr7yfICh-PZcg9Hwu6W_0dyDN65x0opROlY6SVfkdWXUhAmD1e3V0bb7mOkbyK26UcFPJhaMBIaCMXxYk3PUPouRqwTVo4RkfIWZqVf7tm9Gq2RwBDpTFvzKV05jaoDy1srJyYqTDe1hsppXrD1RGc1_Blwgm38XiXT6Cc4_8LQazR2R8dUcFdDCca8E7UeN4Jr05WOl8FllbMCXOxVZw2t4nMwgCRKmM97onYL8O9sIDbDp-LPlG6pRfCQoUFFJsaa4NuuLx0xjDJXSotuSUeKjDxZdGdKppaAAHiX696ZFnS0ZUnFqeDcz2YNML9NT24mVbsUj_ICtiZOQ-FRzlFWXkuUw0go9baY1hqm-rm9iu18bCr_js33TzTJJs_ytsJlqhb6moZEkUikB_E0EZp-wUMi4HhrvblB2bVd9CdYiFHY9Ek8LnRfaEVRXvtaw4jnTLUAGoutWhqWiNMCSJIK0nfuT5lZHoL98cNjZ4vkFHY_Tnka6F-VO5wTv44rQGeRluSxaq-ZI33J1rKekd64hAmJ_b8FJF2cYiBEl-450di_gcT3LOURjPOGo4e7z7MKkmwRmB6TTpLCPQdPMC61iMQmkOZdshdKONPSdw_V1TStAI7kaavxu1XfiKNOPrglkZKaAPV9Qf_NnEC541bs12I_Hy-KOa19HJFzGDLGuYx3-uoCmrD8EmFeKoolKeEpbBx1t23rq0tEShwNpLNO7gVz4qufHy76Xkcst4olRACxiGKfAS5CJE0Rj1J5mUC8x5P6hcXd07GGUm85YtnVWhc3BoNyiXiaK6h86aTLq-jSxNf84UnJhi1wvdus8qgwKn3QfhGD3YSu0_dJTYJZe4BObsd5J4n53N9cL1jU0_is8RzofSlH42D90NsX61mPk3mq3xQ4tgZE2Y6uBBbib4fRqbWFeMgPYKOSBcpzzB-d5z5mH5sgcivdt3X43TezwMxuWL_8sX5C5Hq67ususaPBTkYL05IQxuNz6MW9jbsxponJeO7RupjMaLaTgakKvOHCEIaj7k9fq2Rd2PaY4W4S-QYEsmLyF7qrtEmxdXumwIEHAXEqXoleMUASP5ha3r65PHbPDJecW23mtWABoLNEZPfnuXVthkYLu_RNoVU-w2BaIlHRF5vRSWNTRyLWrTxMbnrEYJFT8YrSOYXZOnOHwgmg6-PJBJV4chny2tiXGaDxlG6jBi1d4qHOQUu5AHEww4XSLv5uxfh6qrD3J9-5wCdRiHX8MdjT9V_eFBjjQw9sHWnbk2CowcSj4ogYaIj2e4i6gfSpxoRa4cH09wrCYREQkfpFdlUELBjs4zCrDaiyHO4fJv_CifZ2raqDog3wU8AEtSJzzf9efqb0e586KENbue2h4kjJs-UzFDTO0FYGoSqtsE0aUW_XP18XnGXaXu5zW5YEjScDZgZG_HqsjSy2O-LJDubqtYHnc4H97QUe_pE6Vn0ECWU7dF0YPSgPeXbqbA554MBW-BNIOVuHYilqcXTtAs5oPTQBgr6XwsN7vj7Mp_B4cooJ1UoUOEmP8_AxbzYfq8C9cV7s2WY7C56tc12UD4khVQ9TVCXP34iDLs7wr2vWk8JFSH5jNdXULxG4sxSmGNCEz63Dg8qNTabJeeTXlYPa0NXMIRQpbC2AHifEZ7LYxfV-NO_x7jUHaGkVxkxxTEzLbGejaTjoLwsdMGZmVlas7gPZUGgl1byB7J9R5uRmUoV6NdyiBVcCuxiAoDYUGMJ0bW37R3OoYqct58Nu_0lKZchO52K-mZu2G9xJB4cerylSSZLqJWbCnnGukHbikT__qRmDvJytH90tetG8GZSyS4FZHxlJVF-84PTrY8qN2UsvZ_kNSqONRffZlE_l7uk-ddA99CnesAY0XgEJIIcvJjTdbo1WsPB9o7oxpJgX8LX7Ic6RBnLvcnkXzJGFDDoanH_qYTNroJeiVGnK6YWwfqMbZiP5B6qgX6_CU_FKFJoUz40LaoO3v-zmp35i90-_ttAPizfk56wYeb8kCYnWHbdcvtLRb4xWtEoL2xzsS_jvRdVpJQd3jtT4puKS6WC-6gMqNC9txq1JK5aqiSyGDqvGuH_wbdJyhyfuq9bwE6Q1TH8wrORBHCoGOB9pCDZF7n2Qsl0hXCFFhEu6VdoY59NA38XJ3AVIETeHZjhd1SiYhdkWjfgiJv53-t86iCAV7kPncizgr-lTAPrzP_IvblkTVTroLKxTdozh-5bU4eAl3pAVtJefgTRgecUGhlSMJGnkqsQ-VrpLMO1eIROsY2CFARddWcFYTTaQoafrLgAZU8B5cVpYePsHpIi1UJL9OpzDAWFicqfhLRKn4Y302ZoypxlNlRHSrTMioaMCCLN0B9T_KfQT6o-sJ8uQXn0hUIzwEKXG2ktt1pjNWwkc-OUPJ1sDTCyj0_TBEuTOfHaVIjVkODqdjxG4cOUrnYHKpFHDQJ2ja0F0Qct5WRUbDR3a6yLpwMiPHE6f4tbo-v6_MqSVYMJ7w84Kl4drCAaE-PAPsIkUX8x2HFKU4FityYYHVCvuRlNQGrv00JtS3UFQ-dnD1DobwbaFTsKG9gxyujWLW0GM9GORJolg0hpTgIyLiZmMQrXOJqLSn2xk1IeiMKknUYA00XKNgjnX7Y29Y318u_5ZVfo9W1tIeDeUi7k_oVufnhEIJ4OLYUu1X3gaSAAVqJ17vBpy3EslvnP2gjQ=='

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
