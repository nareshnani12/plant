import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# --------------------------
# CONFIGURE GEMINI API
# --------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="AI Plant Disease Identifier", page_icon="🌿")
st.title("🌿 AI-Based Plant Disease Identification System")
st.markdown("Upload or capture a leaf image to detect plant disease and get remedies & analysis.")

# --------------------------
# SESSION STATE DEFAULTS
# --------------------------
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

# --------------------------
# IMAGE UPLOAD SECTION
# --------------------------
st.header("📸 Upload or Capture Leaf Image")

uploaded_file = st.file_uploader("Upload an image of the affected leaf", type=["jpg", "jpeg", "png"])
camera_input = st.camera_input("Or capture an image")

# Use whichever input is provided
if camera_input is not None:
    st.session_state.uploaded_image = Image.open(camera_input)
elif uploaded_file is not None:
    st.session_state.uploaded_image = Image.open(uploaded_file)

# --------------------------
# PROCESS IMAGE WITH GEMINI
# --------------------------
if st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Image", use_column_width=True)
    st.success("Image loaded successfully ✅")

    # User input for plant name
    plant_name = st.text_input("🌱 Enter the plant name (e.g., Tomato, Mango, Rose):")

    if st.button("🔍 Identify Disease & Get Analysis"):
        with st.spinner("Analyzing the leaf... Please wait ⏳"):
            try:
                # Convert image to bytes for Gemini API
                img_byte_arr = io.BytesIO()
                st.session_state.uploaded_image.save(img_byte_arr, format="PNG")
                img_bytes = img_byte_arr.getvalue()

                # --------------------------
                # PROMPT TO GEMINI
                # --------------------------
                prompt = f"""
                You are a professional agricultural AI assistant.
                Analyze the given leaf image and identify the disease affecting the plant (if any).
                Plant name: {plant_name if plant_name else 'Unknown'}
                For the detected disease, provide the following in detail:

                1. **Disease Name**  
                2. **Cause/Pathogen**  
                3. **Symptoms**  
                4. **Severity Level (Low/Medium/High)**  
                5. **Precautions to prevent it**  
                6. **Treatment methods (organic and chemical)**  
                7. **Impact on crop yield or quality**  
                8. **Future preventive measures**

                Present it in a structured, readable format.
                """

                model = genai.GenerativeModel("gemini-2.0-pro-vision")
                response = model.generate_content([prompt, {"mime_type": "image/png", "data": img_bytes}])

                st.session_state.analysis_result = response.text
                st.subheader("🌾 Disease Detection & Analysis Report")
                st.markdown(response.text)

                # Download option
                st.download_button(
                    label="📥 Download Report",
                    data=response.text,
                    file_name="plant_disease_analysis.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

# --------------------------
# RESET BUTTON
# --------------------------
def reset_app():
    st.session_state.uploaded_image = None
    st.session_state.analysis_result = ""

st.button("🔄 Reset", on_click=reset_app)
