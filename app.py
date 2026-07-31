import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Set page config at the very beginning of the script
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="🧠",
    layout="centered"
)

# Load environment variables
load_dotenv()

# Premium CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #6b7280;
        font-size: 1.15rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .response-card {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 24px;
        border-left: 6px solid #6366f1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-top: 25px;
        font-family: 'Inter', sans-serif;
    }
    /* Dark mode adjustments for card */
    @media (prefers-color-scheme: dark) {
        .response-card {
            background-color: #1e293b;
            border-left: 6px solid #a855f7;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">AI Document Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ask questions and get answers instantly using Google Gemini</p>', unsafe_allow_html=True)

# Fetch the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the key is valid (not empty and not the placeholder string)
is_key_configured = True
if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
    is_key_configured = False

# Comprehensive list of popular Gemini models
POPULAR_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-1.0-pro",
    "gemini-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-lite-preview",
    "gemini-2.0-flash-thinking-exp",
    "gemini-2.0-pro-exp-02-05",
    "gemini-exp-1206",
]

# Function to discover available models for the API key
def get_available_models(key):
    discovered = []
    try:
        genai.configure(api_key=key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace('models/', '')
                discovered.append(name)
    except Exception:
        pass
    
    # Merge discovered models with POPULAR_MODELS without duplicates
    combined = []
    for model in discovered + POPULAR_MODELS:
        if model not in combined:
            combined.append(model)
            
    combined.append("Custom Model Name...")
    return combined

selected_model_name = "gemini-1.5-flash"

# Sidebar config
with st.sidebar:
    st.markdown("## Configuration")
    if not is_key_configured:
        st.warning("⚠️ Google API Key is not configured.")
        input_key = st.text_input("Enter Gemini API Key:", type="password", help="You can find your API key in Google AI Studio")
        if input_key.strip():
            api_key = input_key.strip()
            is_key_configured = True
            st.success("API Key successfully set from input!")
        else:
            st.info("Please set the `GOOGLE_API_KEY` in your `.env` file or enter it here to enable generating answers.")
            st.markdown("[Get a free Gemini API Key](https://aistudio.google.com/)")
    else:
        st.success("🤖 Google API Key is loaded!")
        st.markdown("[Get a free Gemini API Key](https://aistudio.google.com/)")

    if is_key_configured:
        st.markdown("### Model Selection")
        model_options = get_available_models(api_key)
        
        # Default index
        default_idx = model_options.index("gemini-1.5-flash") if "gemini-1.5-flash" in model_options else 0
        choice = st.selectbox("Choose Gemini Model:", model_options, index=default_idx)
        
        if choice == "Custom Model Name...":
            custom_model = st.text_input("Enter custom model identifier:", placeholder="e.g., gemini-1.5-flash-002")
            if custom_model.strip():
                selected_model_name = custom_model.strip()
        else:
            selected_model_name = choice

# Main Area
if is_key_configured:
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    try:
        # Initialize selected Gemini Model
        model = genai.GenerativeModel(selected_model_name)
    except Exception as e:
        st.error(f"Failed to initialize the model '{selected_model_name}': {e}")
        model = None

    if model:
        question = st.text_input("Ask me anything:", placeholder="Type your query here...")
        
        if st.button("Generate Answer", type="primary"):
            if question.strip():
                with st.spinner(f"Thinking with {selected_model_name}..."):
                    try:
                        response = model.generate_content(question)
                        st.markdown('<div class="response-card">', unsafe_allow_html=True)
                        st.markdown(f"### Answer (`{selected_model_name}`)")
                        st.markdown(response.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error during response generation: {e}")
                        st.info("💡 **Tip:** If this model isn't supported on your API key, try selecting a different model from the sidebar dropdown.")
            else:
                st.warning("Please enter a question before generating.")
else:
    st.error("Missing Gemini API Key. Use the sidebar to enter it, or edit the `.env` file in your project directory.")


