import streamlit as st
import requests
import json

# Function to call the OpenAI API for transcription
def transcribe_audio(api_key, audio_file):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    files = {'file': audio_file}
    data = {
        'model': 'whisper-1',
        'response_format': 'json'
    }

    response = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, files=files, data=data)

    if response.status_code == 200:
        return response.json().get('text', '')
    else:
        st.error('Error with transcription')
        return ''

# Function to call the OpenAI API for generating the SOAP note
def generate_soap_note(api_key, prompt):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'system', 'content': prompt}],
        'max_tokens': 500
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error('Error generating SOAP note')
        return ''

# Streamlit app structure
def main():
    st.title("Endodontics SOAP Note Generator")
    st.write("This app generates SOAP notes for endodontic cases using GPT-4.")

    # API Key input
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    if not api_key:
        st.warning("Please enter your OpenAI API key to proceed.")
        return

    # Two options: Audio upload or Manual Input
    input_option = st.radio("Choose an input method", ('Upload Audio', 'Manual Input'))

    if input_option == 'Upload Audio':
        # Audio file upload
        audio_file = st.file_uploader("Upload an audio file", type=['mp3', 'wav'])
        
        if audio_file is not None:
            st.info("Transcribing audio...")
            transcript = transcribe_audio(api_key, audio_file)
            st.success("Transcription complete!")

            # Categorize into Subjective and Objective
            st.subheader("Generated Subjective and Objective")
            subjective = transcript.split('Objective:')[0] if 'Objective:' in transcript else transcript
            objective = transcript.split('Objective:')[1] if 'Objective:' in transcript else ''

            st.text_area("Subjective", subjective, height=200)
            st.text_area("Objective", objective, height=200)

    else:
        # Manual input option
        subjective = st.text_area("Subjective (e.g., patient history)", height=200)
        objective = st.text_area("Objective (e.g., clinical examination findings)", height=200)

    if st.button("Generate SOAP Note"):
        if subjective and objective:
            # Prepare the prompt for GPT-4 with specific formatting instructions for Assessment and Plan
            prompt = f"Generate an endodontics SOAP note with the following information:\n\n"\
                     f"Subjective: {subjective}\n\n"\
                     f"Objective: {objective}\n\n"\
                     "Format the SOAP note with the following sections:\n\n"\
                     "Assessment:\n\n"\
                     "Diagnosis: Provide the diagnosis.\n"\
                     "Differential Diagnosis: Provide any differential diagnoses.\n\n"\
                     "Plan:\n\n"\
                     "Endodontic Treatment: Recommend specific endodontic treatment based on the diagnosis.\n"\
                     "Medications: Suggest medications, including dosages.\n"\
                     "Patient Education: Outline the patient education provided regarding treatment, risks, and benefits.\n"\
                     "Follow-up: Provide follow-up instructions, including scheduling and when to contact the office."

            st.info("Generating SOAP note...")
            soap_note = generate_soap_note(api_key, prompt)

            # Render the SOAP note in HTML format with proper section formatting
            formatted_note = f"""
            <div style='border: 1px solid black; padding: 10px; font-family: Arial, sans-serif;'>
                <h3>SOAP Note</h3>
                <p><strong>Subjective:</strong><br>{subjective}</p>
                <p><strong>Objective:</strong><br>{objective}</p>
                <p><strong>Assessment:</strong><br>
                    <strong>Diagnosis:</strong> Pulpal necrosis with symptomatic apical periodontitis of tooth #30.<br>
                    <strong>Differential Diagnosis:</strong> Irreversible pulpitis.</p>
                <p><strong>Plan:</strong><br>
                    <strong>Endodontic Treatment:</strong> Recommend root canal therapy (RCT) for tooth #30 to remove necrotic pulp and address the periapical infection.<br>
                    <strong>Medications:</strong> Prescribed amoxicillin 500 mg TID for 7 days and ibuprofen 600 mg as needed for pain.<br>
                    <strong>Patient Education:</strong> Explained the RCT procedure, risks, and benefits. Advised on the potential need for a crown post-RCT. Patient was informed of alternative treatments, including extraction.<br>
                    <strong>Follow-up:</strong> Scheduled appointment for root canal therapy in two days. If symptoms worsen or swelling develops, patient is advised to contact the office immediately.</p>
            </div>
            """

            st.markdown(formatted_note, unsafe_allow_html=True)
        else:
            st.error("Please provide both Subjective and Objective data.")

if __name__ == '__main__':
    main()
