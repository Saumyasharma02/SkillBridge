import re
import spacy
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pdfminer.high_level import extract_text

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")
# Set API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyB8yz43cEf_obsbFcq2QcEFC_kUrluDYvs"

# Initialize Gemini Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

# List available models
'''configure(api_key=os.getenv("GOOGLE_API_KEY"))
models = list_models()
for model in models:
    print(model.name)'''



def extract_name(resume_text):
    """Extracts full name from the resume text using first two lines."""

    # Remove emails to avoid confusion
    cleaned_text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "", resume_text)

    # Split text into lines and clean unnecessary spaces
    lines = cleaned_text.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines

    # Extract the first two lines (name might be on one or two lines)
    potential_name = " ".join(lines[:2])

    # Remove common unwanted words
    potential_name = re.sub(r"\b(Email|Phone|Mobile No|LinkedIn|Github|Leetcode|Contact)\b.*", "", potential_name,
                            flags=re.I)

    # Extract full name using a better regex pattern
    name_pattern = r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)"
    name_match = re.match(name_pattern, potential_name)

    if name_match:
        return name_match.group(1)  # Return the full name

    return "Not Found"

def extract_contact_details(text):
    mobile_pattern = r"\b[6-9]\d{9}\b"
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    mobile_match = re.search(mobile_pattern, text)
    email_match = re.search(email_pattern, text)

    return {
        "Mobile Number": mobile_match.group() if mobile_match else "Mobile number not found",
        "Email": email_match.group() if email_match else "Email not found"
    }



# Function to Extract Social Links
def extract_social_links(text):
    pattern = r"(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.com/[^\s,]+)"
    matches = re.findall(pattern, text)
    return {match.split(".com")[0].capitalize(): f"https://{match}" for match in matches}


def extract_degrees(resume_text):
    prompt = f"""
    Extract **only valid college degrees** (e.g., B.Tech, M.Tech, MSc, MBA) and their **fields of study**.
    Do NOT include school boards (e.g., CBSE, ICSE, High School, Intermediate, etc.).

    Return the result as **valid JSON** in this format:
    {{
        "degrees": [
            {{"degree": "B.Tech", "field": "Computer Science"}},
            {{"degree": "M.Tech", "field": "Artificial Intelligence"}}
        ]
    }}

    Resume Text:
    ```
    {resume_text}
    ```
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    # 🔹 Debugging: Print raw Gemini response
    print("🔹 Raw Response from Gemini:\n", response.content)

    # Ensure the response is properly formatted as JSON
    try:
        # Remove possible Markdown JSON block markers (```json ... ```)
        cleaned_json = response.content.strip().replace("```json", "").replace("```", "")
        extracted_data = json.loads(cleaned_json)
        degrees = extracted_data["degrees"]
        # Merge all degrees into a single string
        merged_degrees = ", ".join(
            [f"{d['degree']} in {d['field']}" for d in degrees if "degree" in d and "field" in d])

        return merged_degrees if merged_degrees else "Not Found"
    except json.JSONDecodeError:
        return "Not Found"


import json
from langchain_core.messages import HumanMessage


def extract_skills(resume_text):
    prompt = f"""
    Extract technical and soft skills from this resume and return the result in **valid JSON format only**.
    Ensure the response strictly follows this format:
    {{"programming_languages": [], "ml_tools": [], "dev_tools": [], "courseworks": [], "soft_skills": []}}

    Do **not** include explanations or extra text. Just return the JSON object.

    Resume Text:
    {resume_text}
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    raw_text = response.content.strip()

    # Remove Markdown-style JSON formatting if present
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]

    # Try parsing JSON, ensuring all keys exist
    try:
        extracted_skills = json.loads(raw_text)

        # Ensure all expected keys exist
        expected_keys = ["programming_languages", "ml_tools", "dev_tools", "courseworks", "soft_skills"]
        for key in expected_keys:
            if key not in extracted_skills:
                extracted_skills[key] = []

    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON. Raw response:", raw_text)
        extracted_skills = {
            "programming_languages": [],
            "ml_tools": [],
            "dev_tools": [],
            "courseworks": [],
            "soft_skills": []
        }

    return extracted_skills

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
   # print("🔹 Extracted PDF Text:\n", text)  # Debugging: See extracted text
    return text

def process_resume(pdf_path):
    resume_text = extract_text_from_pdf(pdf_path)
    return {
        "name": extract_name(resume_text),
        "contact_info": extract_contact_details(resume_text),
        "links": extract_social_links(resume_text),
        "degree": extract_degrees(resume_text),
        "skills": extract_skills(resume_text)
    }
#print(process_resume('uploads/Resume.pdf'))
