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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpOsUL5CmveGcg9LjwQH14Ixu_0K5HHvcLcoBiumHcfR1pKGgOodi1NwqEyZcS3CBSiLHjAT8YpLmZkX2a72CCctv5gTrmq6940sudOUp_5-xE_pQBKuR3ps_XkrP8IQLARG5f4pXAaFVg72dZujSzbvaC1GRXLMyyTiLqb0cT2U94CFmdmL4ZPpZYgLJiaYMkcVfGCkgnRvwwcyiKETUeghTSsK51S4qQVsZf5OW4J4bUNLlKTCi_yW8-VbZiXD0L3MZOsroi9C2oFTJANrHocNMMuLOsooql3fup0TVksI5htgPIar2X8cWl2AU5LB1WvYD2iU3TrLU_p2nOEnKqoonawGAMQcdH_sr0Z2Zy-DzUc1p0HJJ1lP-DGb0mKPDVNDVDO7_EYV2rk3VHUSd5mNMM76k-h5fcrdEhBn77Z7WXydog5kOG8COECYcgehg3JDpEIp_IkMm7RAdQk8CERW9hF7mFeJ9mFtyFENQt70Qc4KF-CitmWk7DFpe3f9Afweh-9reELS1VDmAW10_Sj3jC1axsDfuzp1DWxnGCPaitORRXWSyoMQD3nbGefH5nIeWvCFCymwGAr-Rj_eZ7Wy-A3Zva0MK8yH0xYbitJyUEDkMQwjhAEiUJK7QThZslyaJuTtujWyKN1WRs4_ob8meDR84HMIKKnylTwkKovCt-93BjSSc70ggpps2qd1EPmsQMp9R1cjIZErJThCCSUao5rUiTuJYLJBmT_bdU3yxWixShbwhsQ0kahRONJ1nhTbYuDRjeQaUC24jKbiplcIpCdNfrE0ULrVT3rg2U33g7b7q_uBqTGFOX_OtgcVc0hLFG99-B5-WF9piPSEhFmrOi76nBOIveTB4-Fk9-xS_MYRfDqE3EmkF1C0Xu1tusuWxO5crRh55nJmjacZ7Ay4nByg489PsO_u5u_STIEgR3QdbEV30Ec58sp9DBmG3MjSGgtMs8H-YfUOSUshtz5unRzDHNtFG1hbfchOz4ZBv16jo-snNRkiQgGiSE5_xDTXcgOHy6vjmJpL7yyafy1x9K5VaoYUhUDf90CeuwlBrGSR4OKxqYjevSZun0qnyN6eQs_GQQV72u9umPbeRUwluTIqXXet34O1_GbH55tmPUx0pBLgqYXyKxS_PUnrG-3PGpvkAUgYB_N0HkUvlJg5UQbdEpy7R-RDDCz0upMdrOVj4GeZFIth4C4nrwtrexP4fzWMbtd2mStTpWjCMxbE73sdBMK2icHDh4qG9qsdWjIEZYM2fSB9W1Bx_QTRIJerJI6DomLXG1-6CaMXy4Pziapklnuy2dRFOp0yqY9Rx59t4wEpZx8MnNXl_VI2uUIUG7fxiVn4FvFmXZkHLyJH0JHIKshRMcTZDf9qkygp4wO33Va9c_SAc02OjcsOkHlDS5cclumRf4wF7Lk78E5y-o5Rxgf78a-ZsLC_xPjlu2L5fI6FhRgiv2GBXimWexr4chY_nYksRx0au6v8J_TIBOlaeyFZ1bG0epFydWy1x5TMsIXd_4xrV_kkHcSFv-yrryTWuYe9HcH_EzHbjUYgDxhOyt0skUpy7doacZrNnG04CYJCc3_duxHTeI6V-NDFrVD8EYi2tP5vayktcAu7vNhWWBkgRq2-gkHSOo7WBwNy38Hut2g2h1-EBkHpjxC7c1MhTlxcd2E0UXY8csvglLkUx1jhtHHBD2Eu3O7rABcXDNA6icNmStHksFb1NRZgnkK-hpKmAF0Hc17aXieg17oYzmq5So73s6Jlq-Kv1OenFj4mgf7mHAYuDsEulG-Y0aoefVCUXL5rF1lu9RkwNXphdUt3rIqqRC0XKN_NWTNgmfA9EbnYYuQbL68-7pGhLCnUnK8fqpz8YpVKuWbRcRT-TObl6K_qR_MWAxerHpilezH9ARKOS7E3Gxb9sOI82g9yTtTmij7e9-XAyhRHktJgGQhZmKLfjBaYE84aERHrK2kxgc_8no9erLedKYDuMcYXLTdi3tMFTbQHvp4ehKrZ5r9iq3f6NBot5DHYGtLoYXHxoFKF9-EtWx0QOt0GTRDDPc0OLAUNKvncTJR4uZVSzopBkCEIOx5px3A-xfATEX_vv2L9-zzZ-2LtYDmeeznRizqi84dhU6GxXKslgcuArtl-hxET7Hc1J7dfGt9MN7CLu7LcDuTmzHb2GJU225YzaXIxxG0QEAcrOkpBPo067QA6DV7ZBNOr9eL-9OnmZqw4QTdVbFj8iKzsuevedX0Gp0-jrsnYbUswcOSGQp9m0SUt59VrHR9YydRAke1HmYJgK0X6hChQUurPu3QA9W7NnouyN3_e9lD3X9rAdv12QDMQfeGK3inpyJf1Cz93Ym6iZWTDTMMw8laoY_2ksoMTjCmJm5wT5GAswSP7xonClAuxbbSd3vdqQWO45ChsgOOnakdh1jYAwKxdwbcgmoz4gTQCMLn6mlOA3IO2_fETNz3B7b_kfWIVy139jHz5Z2XW2ROOUfIoSOrazQ8Tdncr0PdT41KZ6B7FUilC6ze-fLYO6YAIHR9XFwJeOCgzknQNscIQVapHTfAV5K2QT2NMCEyKM5cQqdLiz89fZ1YrQY8Fv2agCDlY0mzlCwzbp1GdUOJyQOOOiTshGvXYNC5696by9Z9nqHPTBiRfNSXc-eVwFaOSJHEgi1LrXcX04_hnusTT7SqgKa_oG2lnKzjtSArTPPGnm4MyPHNirnP-svwiyF3Cs-7xxBQRL457eGe9DxsO6ZJk4yiw1TjhSwqzsvm-GQ9vCPnTv6Y1iJ7X6VaMu-O8Zmn0FVnRuLy3Wg9HQPX5FDWtGL9fkXBic-mpwiO1YngTGyD6yzsFO1vbiLz_2qGz7_hMRb2oU5kltMjctu-NLU2zoEW6r8t5LyT8ydaxFYPH9hb0D2_0ZpG_yGa9LnMB_Auh0KwtKRBrsx6H6SW0UZcvDBtgGpDGMUnyxIm-KCSduSnTSWPO_VdfYyyWcsCycnVD1DE_8EMmld1UU02HdqcowTADftMoGFIirCUkOS1SZmFnXSRi0FRv9CZoY5XAlk3JX4sAyLYsfJPSpsGjW9cQOu2Rxorhjaq3FuAriknw3xczvspZnVQnQDcFuhoJnIZO39Z7UyiycBLSmoja7x4XSdmpFT28QlQRqMQi5jHO62VCZzs27rTrRK_AaxnGa48zJILpJVY010WYVvVEW65fEo9g-ZtHcHdkcfWzghclwjbBKInO8RrOEltwGMbkkefi1iV7PBhsquPFaRuwKqF9QH5kVI-TjBrsriCYAMOtlns_6otstnKJu_bNyAct7OvSzvPgJqdjQp9j_fOOpRREsDkf-AVYleWOD5AzRf0eiGgtbCfqNdLzQjM0WCDxEhwg5hgAcf99ZTlQe5VBzW1lDvTgj-xpJPvXrcjTqLOFz7c-8vZWZD1Y4Mi1fTUxRIRS5EqAsVeX-OMmgpYKFiNOSb3iN11SXagWgJIVrT9lclMb4HWSl4QDmkMWPgCnCx_M7DKn6okfzyqzlYPcxq1MIjJ5sHD5TXHW9gQTTq56bzE2u1bvCH6-EHWYnbU2lXdkf_Yk22U1zr-Y5clsT79LYPjNJRHwN6YzjCmyjl8cRnVX74Ra054EUgekEQS3pJ0dUXIe14uswB-H6yc1HTrBwuod_6F6EKr2vVqeIle3mX75ScQzoXeYhcT3D1a5RGXTUE7IQO0j7j9wonI5C6vo-HhfCWy5guQjuatmjN7FfYKOTGROm8cMeMagzF-NH_dNzJxOFqOY8sr2tQLvjJzMHTnrWGuG_25nNioIdmrOOW63p8PIY0eQPpVWDosXSK7goBeJiKZMp8loS_UPn3kXlRrdUDqh5OEAakZYl4zwRsW4CL0Kj_SDVDtxeFzosQuTd14TN4syla9Ix_KLjL9eO9e8sAcYtwNxJc9eKRtIWaZFfwTGM6d_84KxC5dJHqaq5l-XdIKHgXw64TCHO8wYaU2g0vAS_ePAAiBrRH_LqCIEHcd2I6EKZBFy9e5qF5OO0yTBGKs-n2FzHOgqulx3SxURELc43LUZYueEVeYRdrPuJEN-XsUW-vOf2MvFvww8qWsNNCk-8F4FFiULGdhR18dFOwUjpNzKtHr2WbrfZv-XTW2X1cCzs2jnRlokaQEavQQC7PHrcQmRohqI9SnNJHSrnI80sC76eq7jQG55yXO8BemtOyCdnQesfitJ8ENtHdz_Dp9rjBpfdU1DFrn5JMxbKOVYWXmvDg4OQE1cKQgCHhwgeN2f9LKxflBclJgAj4srEJHYxQGPlnzjXj4IKwTXRJt3fhXxoyi7_gEtOr3e-n1dGxl-D2HokwC2-mSq7MOCm-Jr2HWG2cipHSPBbYSl6vUN7QEtrfrFDm5E_3z2enryPk3DitT1WhndgCbZVNPleIhU4aZeMO7G7MG86mfwAG-402D9VpmMn3MQeP5wBDwVSOsVaP9SBTymTCqEVi7oOZc6xODg_YQf-xsGr4cHlUL10AbuZ8djb7Uw1mo3Ps4z86CRFniHgFpMgyhNqN_Pnb9nmGsKU5PNkdg8kQg6VGbxa_HBGK4ej2nDwbZeZkC1h1kERGv2j3FmldX9culXDMs1QuFUlUIr_svM6wn9f7FsblKaGUrJFNtNEBtrQgKOQjlEWMjMN-P-BAE_J2PoWLVOA-9wMKe1RqSuwjL2wwrN-JQ8K5gz63EX7lK_Y8AAdIJsL9_Q0dJdnezVAhW1EwSM6SFkxiZPIoEO-8c4_52HxhsZwEltNP14S29JllSmDkjt4qEUSpKhu-ZOmBRVVG3dxIamrpCF4RkYrAP92BtmZlBVRQgCIVq0GOvi9hwS7ECyzl7MH42KZixLKRWBgyCIFpm_PrQi5idPWTCg4XD1ftN54dQ_M7-ZYp0vnnhesWi2lKiC89Z33VqrvXT_upQoQsTSGQb_B93R_dewz4fh33kZYWfol3g_YCuo3SGJSXQpA3JTE9PXKpMpmgKFXfy4wIgLunXHSegnldip5mIPNxcwmpWo0FFMOjxeSzxL0-U7w1nXTf7-bWcSH8BRi8fg3OsyXp9Q_oLRdNzG4mTBGwWlyTcDlaHGDPxDHAqbonTX9SXdSGYsWrw41e9ned3Oz2iyl8_A50vW7uSB8UgcUHcO_j7Nkd-7Xvv3i9xR_Zjg9pgbqaeyKZ4Jm7HF9Oly4JtmrQdShztRVJwWm20S8B79tSt1JqdidRnn4oazayWE01GALqS-Uh15YAp1Fk6fYVrOsI9SMXAASFQBx5KUQ9UU4eQZ9iqwPyIAw5PM1pc65T6rCU6aJydh9XmqVqkvr_rOx0MmlvC2PIRAucMdRqpzVrdwz7xXKNDa3JBJctF_kHo89EqiFOv-sLBQKjMnx-fqQ3IX79G75YbC7QVRPwu3G9wabIopkXDPUp7E8i7VRvrPWFCFOJIYZja79wzbRJgpkSt7exhDoM3o-qWxFl6mPHZMTq1FxlQEFZZp7jYYadFQrpPrkszNMlemAX5jdVLtGgMT6GiHyx3hW6k6cRltxZ_yCvN6AFg2DHoO_PbNG1wrfbYCB5sKVG4ohZn5jXcU5b46SV3wuAjCiKJPqxfQ4DqkMrjUuQNFkA1hN3AG2qDzqxuK1SM-nUC6so25WeEpw5C60Eh9SH_8ihz56cYdyqAAbiwekrDWwKdIkdPWZH-TI5wn6j4DdEPrwusPX32X1mA0JFWLds-uWAEf054-zPT-pLY0pO8zHk2ZcjvvL7B0nNEloYaifVflZc1kZW40NJLVh7eWpqRQWVZq-kGBTdIOeFIDsl907sLDlyWQDdefs5c1M_my9GRzQ1vnOE0Q9h2WElOKZ2eT0Ns9orLabxxx6-n6nzj5q6v9PQiJWnGpCb29gQFCbzZv47nd1I-OGd-AFyuGjZf37ZSbbfwXzGjkIJZV9l9aSGB9I45nY3jTqG6sLDSyDfIKz8R1eZA89hzYeiJkSijMhHOEXC1TPmymD_CvZ3GkojAjVNDvEp-bsy9V8-YGHLkgJdCixDe6xz2yeBZzbYxhO0T2wJYnaVuWWbWm90b2AFGkgdQy50gOvKP4cMA0C0LDkknnZEwiIoddjw0UIE33BeErwMg4NPIlA4a-tvpcXmQMKV_4Gw7NXxeZIDS42CFK2kVTzAe1Tz8oVFQ5TytUXjh9wIV1ZG2gREegIfdg96NjzRcrCTumk-368q6tj-f-o6evDfXzwefR5wD6gBXoA3tnZQxP13CoqG-jEynDq6TVE8-fo3A8wQC8wy5HcbVpLYFQgoZKoNOXpTvypRbT2FmVWucYXBG7pyGtYH5BdplpRLf23dx0CWHmoagtym9zrPXacYASobKXMVuSgwcr0Ux82o59ScCpOlgOb565dIFumT8VT0hYnhzw3sYXYSaoLTTCQ='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Integrity AI", page_icon=":butterfly:", layout="wide")
    st.header(":butterfly: Integrity AI")
    st.markdown("**The purpose of the educational information in the responses that are generated is to foster discussions between people. It is these conversations that help with the evolution and implementation of best practices.**")
    
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
