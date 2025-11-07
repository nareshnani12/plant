import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# Configure Gemini API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="AI Plant Disease Identifier", page_icon="🌿")
st.title("🌿 AI-Based Plant Disease Identification System")
st.markdown("Upload or capture a leaf image to detect plant disease and get remedies & analysis.")

# SESSION STATE
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

# IMAGE UPLOAD SECTION
st.header("📸 Upload or Capture Leaf Image")

uploaded_file = st.file_uploader("Upload an image of the affected leaf", type=["jpg","jpeg","png"])

# We only show camera_input when user clicks a “Take Photo” button
if st.button("Take Photo"):
    camera_input = st.camera_input("Capture image")
else:
    camera_input = None

if camera_input is not None:
    st.session_state.uploaded_image = Image.open(camera_input)
elif uploaded_file is not None:
    st.session_state.uploaded_image = Image.open(uploaded_file)

if st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Image", use_column_width=True)
    st.success("Image loaded successfully ✅")

    if st.button("🔍 Identify Disease & Get Analysis"):
        with st.spinner("Analyzing the leaf... Please wait ⏳"):
            try:
                img_byte_arr = io.BytesIO()
                st.session_state.uploaded_image.save(img_byte_arr, format="PNG")
                img_bytes = img_byte_arr.getvalue()

                prompt = f"""
You are a professional agricultural AI assistant.
Analyze the given leaf image and identify:
1. The plant name (observed from image).
2. Disease Name.
3. Cause/Pathogen.
4. Symptoms.
5. Severity Level (Low/Medium/High).
6. Precautions to prevent it.
7. Treatment methods (organic and chemical).
8. Impact on crop yield or quality.
9. Future preventive measures.

Present the result in a well-structured readable format.
"""

                model = genai.GenerativeModel("gemini-2.0-flash")   # <- correct model ID
                response = model.generate_content([ prompt,
                                                   {"mime_type": "image/png", "data": img_bytes} ])

                st.session_state.analysis_result = response.text
                st.subheader("🌾 Disease Detection & Analysis Report")
                st.markdown(response.text)

                st.download_button(
                    label="📥 Download Report",
                    data=response.text,
                    file_name="plant_disease_analysis.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

# RESET
def reset_app():
    st.session_state.uploaded_image = None
    st.session_state.analysis_result = ""

st.button("🔄 Reset", on_click=reset_app)
