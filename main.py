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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpOsMl4t8KKJdxHadJGUqRCiAzrPWgQ_g62Wfu1PXPA-Or2FpVKuGNZS500tLYch4N36rmtoEbG80rkUkfvXqAi25pk-AosStIyCs7qELBkYGPAAJgKAWU8B7BH65vI6l55aTV17RNrLH7CR3_WHy52sMWjRo8EcWswzwcViXpaONmn2wAZV06FmNlDyRBsajDSeGNWo4tbF67FYMGkxmskm6_gl34xzhqO9MVgGJ_Ap8KeL7_SD2jk_n60KhDJkelNp0tmr09-JfnoNwPxVDUAzuDS7QaqbIIZ4ypinFVk_nSPPcC_ChNsr68cwXMWxg9eYKdcKVWOLwSuwF7DvXKUP04w9vn1ZA5O58VFljxYYViYlJwpvQvtNvMAtSple8tWVVOCCy30aF9TCxmm1wL9nJypC-wLbcaci_RgdxbqfXj4OE63aARiDjYxKEnJgpudSfqVHIhoiHkx1nay_i9pthnE00_UTqOvv3N6R85VFJ8yIKymRVRvHB4OcOByzeIvJT-oavazZRw7_znirZ_NWAftavbxY2MF5LjydHWTtrDup0d5iFomzra8RrTWKgdgGJcBsHvS1H0-ymC0LUqB_K7TpQDca9y7tkU_xh5_rVlaTfh_FmifDjTOGS95WUd2YhL-kmCRkH5fkgLqAp2xTQkEFvnzaGiJi6VTkiOE0fYMi7yVxiAUODbJOQfcKKr95iGRqim3kKUbkTM6PqMwqMsrA5b-Y2PMrpqdgmtdT-6nizmHRA9mZlMmO57bE6SnG8AbODmqYeMpDvmndr93-2N6OrJ76HldXRaDsJe5qtFGL_YXlv2qfb4JhpA-9sk0LrQnl1r_fBATsc5IlwVGrOOy9FieT6_jz3Kg7yKBawafbxSCfWviCbP9m5h7MsE_9fM0FJYDt07Oywj407QLtdy0UhHl8qB9DaGqVnTMm6YV3piajIgystLOm6PMXrUTh8ERDcwpNDA0MvedTOp6rworbGRPxqZ8g0coq0_gIeZ8_IGVNrPNb1rCepcbE3EjwQ5Lxeld-T5CJOT186yrHetjffeV37YR-yPxe9sdB-etadck0Mw7uBHfxg4USchYnuH5nPnpSXshbKb9ikSRkfPrfY4P2vQQ1ev0tuLyrhmKp1mrCafZcEuFLK_bnj-b-GCNmCsfxH4Ldn2BRD1nFDvZoCNP8aKTvXecmCzL8NCbxglkhtbDbNqOWtlvlls-rtQM-xcwZf6opKpArHNhcnGOnzpUcFZME8dv7D_n4l9_Jit3f4USXiDUvgOTW0xCwxEOWNUKs0OIH7XhKq9wovXq-BC5LLkJQxtE23DCsjJExMlS5bCOr3R-z7jNGT-8L1w_j4PBF_zP5T2TigZye0ujherSw3o74NlkjEQSoOUOGhWISFvc6PnfIkxk6RrkTqJ6X2VkiBoDEE0u-IttCOJo6Pi4znIQ8B07FPuaBM4wC2V_Ww1WeYOOyUnwAL5iuQFSABxa1-cMGnvwOT2xFQw_xh-rm8WSOGaCWElvilSsDAL35NheIFXkTA8IXACws5f3M6kA4BFbFuzX-FLEPMdNTRGAHDBQuQnG97_VPfD7oOCeNXelMil-DP7btdlcrBZ1KoOI2J8UwQgRa6YfiDlgXa6zRykwhhP9SzYl2SkQZHSqGv-zpZfyV4R8z65QJC2R4QSkOiHwKdEESOTTHrINRBmKu2_35Lyp5pTFCiSK9ySnO_Ib8x3OpY39w_SQBmK3cQiuG0JWfBwBySjIwEq3uKG3GHI9rzlWcPJYtYFajy4rtWRUfOwVJTJG-wq0AZMzz_UI54dKMaImR-uExbO_gvtgoo1puswbS-c1vhk8DdZC_M6EoVetjWTYfgO5_Zc9v0iQJ5VUxTFkmV95H288qQxhU7ewd3CoAzm8Du9vk0kS9Gq2u9PiMqyUunNClv2hqvNrUflyZD5lzjTTClGVwsu3APrw-Q2BsnthF9rhKDTqlqKyQ497TAByLFK5nr6xbgZ6qcqDbds-K9tvXWvzf2-dF39OPSj2BTMishe-hT4WZUve_wUAY9EibL7ghFbSUs-A6Z_775b7eTzUvCwP6LhkNgEb-NFFc1nr8IaH1PI3u5bYWQkC_H_EBrqn_7FihCK_uLVm2vLM-uTlNNAtPPEThZsqT_4g1LGdIxahNhrFPncZuuPXP766MvqfjxZnkGAKMLnGIoWahoylDrMdgcOPVVo_JxZJ3m5QT8GyfNpy81gaPFB_6uV7mawyr3mDXeH5vlUpNbybbA19LL-9fuKif3c7nXpSikxM-Dg7iZkZ_6f5mwLYvuHnQdjpNu6AesBkD8XfZqnbfpoJRXG6e6wWoOKiCqyyBWR-7HBK2p4OJg0gbf2xR8LVumTY-kCBMFZH9JAzEkDomGl3R-DZkFy7OVk_0tnNI6ncYeWBr3zhtzZ74ZqkzSzClGInyOtNLHw8RF-XJ6rM4AglK6hdiI_VwuzsmFXO-kdYDWxPFfm0XioS0hCit8rwsw5jpBJnu9Vh9IjDDcnyw8n3zhT_wtT0HQ2qzngBki_Z6qvhtSuDYfwstPn_I6zWUEfoBV9fGAavW5WnJ0Wwiqrwrgt4JgiynKgX8V4QEtOCEnbFvRmh-Nb7u_uqZo9Ou-Q3BvG-2husYT9NygeRBvwfomyvBiPZRZlpqSZrIJxfEGLJG-0lsZK-s-aYP8apG2Cwaj4g0KEaPtbWb4hrnzJuKoTrY9TW3Zl0-TNmkhBUYwE0tJg3f7XOg52nzDgsIw2BD4HgmJtQbWn8XT0ShHN_wBH__kHzjkS86MM0teLhCbe6ZjzBszUt-3KNkTDuWrLFXS0_5ID1QSMtCmnNlid-ke91Ff_CIyXKmltCU7ei41M_AuOQ9ZIFJxFj78zQIZy_2mvEPjHyPDeMEeVsom28Tl6TWu1sg8yukZql4PdZgKu9hXcnFt5K_IRRuL_fqsUO18JRjy2PwoXsuMZ5siakhAz99pqaCAUnDUDDJzGi_k8sY1-UwFH5MUguRLOYU5tQba17RDP5tZmzSxORVyTCax8rhKlDwxriPJpLlG6VtV9VVPrMETAlszslMCSyDCEmoqz67YtGF-_YZsbF6WbK72Kohg3BUirO5x4q8BIWAmp-2vJ1L22eK87C-NFrpowRszW0nfjYD15hXPNI9cDY5jHMoWukDFCi1be-yZNUOK70AL--_w9FDGNv4SdIBKl29FVgtfS4BxsmtrpNlbHpO4iKBoJCjY3zMkdMv824106D3H0AdMS1wOcmOB90O7gERn5r5dpcOYHyKSdBOihKhgjUbvYW-GqiSg9N6-hFs1Wt4o_oDT2DP-Eej3UGmaYHPrT5U7Ro5kii8MbwU6dZRk55K3Fcqr-fpfzSeSkMqL5pFQU5uvfpVwAnT79jNT31XApcVdlFFrlWbFkQa9G2b0n_19aG2YPy6txPpv6-HUDMwI3lguQP0-DCgNKB_JwNEM7gPi4peNM0a2908Qr_PwhlYaNi3MW7iGKZSIob1JJajGnCHPUBu-E1QZVutYz51rB8uRnBYc5fK6d9xdQMjvG08GGKEwRY9Oaej_mtrhVwq5kTqEIOt17sNEaeI0oWtpsPqvoJffg7Qk_gbI5kLdMJY8IaAT6DcPa9ZGuxAc6mpQSRJadjcXX85f9tjM8DdUJrahSfYBdAeBgbE7JlDjC4vF0W6qKqd3GjQrR1ortKmJEorkZvnSGHT0mvnsy47l7wcFU9CFinj8R-yDVJ7ASb0HPK-wX2qiWLqPkbNakKwikSWG9cqJkezr1e8i4MiOutp2EmsWJBaJjTVP9gMQUGJn83MTE__ij2lQcne-ueW1BU7Fg1n57ky1M4MrcJAIVLW52lSc30Uai-cnDnz2QIsFBygsGedJPbG5N9eB3hdXNMFHKPharE5t6oiXxM8ejnpw3vglDio3_MLk-3-aYKZRuLzjmLv62BmOxq4QbkwH2YpQ6HwmHmCmPmNZH0h33qD0ZtgXDBknusHebSqLwbqmKgkMsRUAW5NW_t1oF8Y2yXdxlqNM9a-4NM_aerPnX14-pJ9QdwJ4W2hakgJKseqsRgDHf2VIUwJKurO-8fr0rIrgAVoxRSmVPM6vIKGrpz-ke8_5tu_eCFli4w6dK0ltcV1K7WuKwfmNepSf60h4SSy5pfw27PrssXQqJP-bBzrWjtYinjMuIdXmr_h9ayEnyU-npSM7rM0Gc1lVpjEnKbTy11u2g7n5ug4NWy5t988r43-qpgzysdirPS6UsQ-3EqZAL2_Ud2j63GqaDzUeqfaNFdfEKOXpdbCFYteJBdNHLusfPR--YA9bcJNL1CtbACKiYs_va7BGZURyb5sLpma-49wDWYwsXF-UVz83pYjqy1QaXdS5w8vzbU_KQfaQJtjhohjgWfhIFIGnFUvV4Zqjh63spbKp1VmWQ9K72nfYC4PGJb74D5LUGQcCgkLcZo-HyTZi8T5unyAjGbbrPjQc0XpKjp2Vdeg3-eEqAQs6n3_Vsj6DibquG-EbIOlrcaQBLZ_8-nMpQJvaUjOybVRRAGR0bmMDEnHl5L7FC1LKMRv2_VZZN4fooeV-6gzujlGx4ZTCZUUhVKS5DtuZ_iUsRw4zNMjIrcHkJdp2HS9fzOogxjyPndcgyH95O2ljbthy_rId0DkGgovIkHAsCoDz9OtCoug61Z1oGGBocZfNDQl2bS5z4MjyUNuR_ZbHySm-vvc45oiQsDC2u0awRwa7C-3TzLu6Cc1MrElW7Depm2EFlBXWkHSYmGL0xQZ1VkclpKK2BQxA5QbJjjdtzJW4sKoDzGlVIWqyyyMuS0ou5jTHImZXzddTG7WJDjCJoAhwRbN8FICHb8Pu7KrMz3K_FdCCX0u3Crtb7-AuVER6DTQ2mRvuTB4VyXvhDf4QiJHU3II0u7BGD0B3XXV5Wr7cgpRsCo6Y-uvhlW-PZfcWxlHDGFzepE8vbNmjDjoX5pw9cN5PnGtsk5lqQZsOA3oFKyrQdA49vuqsspk9rkPrsloE7TrsrqZKD-VlyGjxlhepTdTPh_iSzL-KYksfmU4QWToBBdj9yLpd-xnRrKnCRA16bOjEXzPzxxFNybBzLq3gWpIYAWwjrUwBM1RHDXQOu4AsLQZpDrMhr03ywDgj9TVKFHGiv15KqC8_rQAsAysjEd4m7lScMhK-GE_ygLQr6vwEK43bYdpQOt9j20ItLsoHRlbLAqPUevcGxV0yzQvP7do2arruU2Jo_zBlnP0Fy3B1NBge_Ls8ZzcZAY_eCgwR_vZy_EYKxJn2EVdHWZ0xdQGYL1cj7Uja7wMurUYj5IfE2q6RneP8OZ7PJt26GgwVbERh_hr_gV_ufYyZN-AA3kzmu4D4J2LzfRhbaiVhxPMuheQFzcN42i0j-Z3R-a9oraWfn4XSkrn0pNnF9lj6RQ0cPYv9W_21BL1ImhaQKLQspjqwZv97cMZQwh6u_d1zO3E2fdl11IpKXd6wsY2cswozJXMZk9dJOBefT5mjUZf42R_59600Sxr-dSBS-luWRzPsgzi7cKnzChHGtdGeNGkc1aSC6PsNLm8IZRoiFbJVYlYbVbSthKZPNdyJ-s7HGyXvub9_CRaG4nBg0zD3yBLzY7NoCxmVaEBiNjjAA4cGbduDqo9TfVcfmjgCSRP24Np9i1vC0hL8GIJ43GdOWkH9ESL41uu1TA-6A6OWXsWKHuJp0W_brhheEVbS6O0m4Dvl3whkwjv56AaolcynGNm2fOhhFni00enU6VFVo6cJL-BW_3iqK4sdCbXYRkhLOiJIkt0yyppIcUxs1YeS-G8WFAzSj2l-dJI63hudOI5GfTnH8zZOUYHAU3zawpMAea1jx-dLupa2xLrOkvzjzcaNdtZAYhFHcvn8fSZs6iFSVrkAu_mZ2wEKzEqw3wNKbeMxWocWQBLYJVN2Uyt7VH2-Oe-xkK2fYvPZrDFnTkashjxgFCzVadsaq8yry172vCPde3sam1sB_L2r7b0ff2U4lhKw7rGJwmDcFB6M4Z8nSbuHVf1odxc9raMuDu3pApdsyvRsGO0L7VMg8-Nj0GPaLpW9gv2mxXl4HrGzdSo5B-c4QWouBgHxIdDOz5o7U5IyRqUYCMNwJfhAqTN6al-lYbG92_dh3aweZiDRpXMcf4MXvWkzCbn9YLj1kziQ3loJFyI9sJSLVyb62SaFtipfbH4PUK9bacjc='

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
