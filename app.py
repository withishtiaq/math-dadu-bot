import streamlit as st
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
import math
import time

# --- ১. পেজ কনফিগারেশন ---
st.set_page_config(page_title="গণিত দাদুর ক্লাস", page_icon="🧮", layout="centered")

# --- [নতুন] মেনু ও গিটহাব বাটন লুকানোর কোড ---
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;} /* মেনু বাটন লুকাবে */
    footer {visibility: hidden;}    /* নিচের 'Made with Streamlit' লুকাবে */
    header {visibility: hidden;}    /* ওপরের বার (Deploy/Fork) লুকাবে */
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)
# -------------------------------------------

st.title("🧮 গণিত দাদুর ক্লাস")
st.caption("Developed by Ishtiaq Ahmed | Powered by CSE Project Hub BD")

# --- ২. API Key সেটআপ (সিকিউর) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.secrets.get("GEMINI_API_KEY", None)
except FileNotFoundError:
    st.error("API Key পাওয়া যায়নি!")
    st.stop()

if not api_key:
    st.error("API Key সেট করা নেই!")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"API Key সমস্যা: {e}")
    st.stop()

# --- ৩. টুলস (Tools) ---
def web_search(query: str):
    try:
        results = DDGS().text(query, max_results=2)
        return str(results) if results else "No results found."
    except Exception as e:
        return f"Error: {e}"

def add_numbers(a: float, b: float) -> float: return a + b
def subtract_numbers(a: float, b: float) -> float: return a - b
def multiply_numbers(a: float, b: float) -> float: return a * b
def divide_numbers(a: float, b: float) -> float: return "Error" if b == 0 else a / b
def power_numbers(base: float, exponent: float) -> float: return math.pow(base, exponent)
def sqrt_number(x: float) -> float: return math.sqrt(x)
def factorial_number(n: int) -> int: 
    try: return math.factorial(int(n))
    except: return "Error"

all_tools = [web_search, add_numbers, subtract_numbers, multiply_numbers, divide_numbers, power_numbers, sqrt_number, factorial_number]

# --- ৪. সেশন এবং মডেল ---
if "chat_session" not in st.session_state:
    sys_instruction = """
    তুমি একজন রাগী অংকের শিক্ষক। নাম 'গণিত দাদু'।
    ১. তুই ছাত্রকে 'তুই' করে বলবি।
    ২. ইংরেজি শুনলে রেগে গিয়ে বাংলায় বলতে বলবি।
    ৩. অংক ছাড়া ফালতু কথা বললে বকা দিবি।
    ৪. সব উত্তর বাংলায় দিবি।
    """
    model_name = "gemini-flash-latest"

    try:
        st.session_state.chat_session = client.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(
                tools=all_tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
                system_instruction=sys_instruction
            )
        )
    except Exception as e:
        st.error(f"Connection Error: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "কিরে? দেরি করে এলি কেন? কী অংক করবি বল!"}]

# --- ৫. চ্যাট UI ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("প্রশ্ন কর..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        with st.spinner('গণিত দাদু ভাবছেন...'):
            if st.session_state.chat_session:
                response = st.session_state.chat_session.send_message(prompt)
                full_response = ""
                if response.text: full_response = response.text
                elif response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.text: full_response += part.text
                
                if not full_response: full_response = "(হিসাব শেষ।)"

                st.chat_message("assistant").markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        if "429" in str(e):
            limit_msg = "বড্ড বকবক করছিস! আজকের মতো ক্লাস শেষ। যা বাড়ি যা!"
            st.chat_message("assistant").markdown(limit_msg)
            st.session_state.messages.append({"role": "assistant", "content": limit_msg})
        else:
            st.error(f"Error: {e}")
