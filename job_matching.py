from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import re
from nltk.tokenize import word_tokenize

# Load SciBERT Model & Tokenizer
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

def preprocess_text(text):
    """Lowercase, remove special characters, and tokenize"""
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
    return " ".join(word_tokenize(text))

def extract_preferred_skills(job_description):
    """Extract preferred skills from job description"""
    match = re.search(r"preferred skills?: (.+)", job_description, re.IGNORECASE)
    if match:
        return [skill.strip().lower() for skill in match.group(1).split(",")]
    return []

def vectorize_text(text):
    """Convert text into SciBERT embeddings"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()  # Mean pooling

def match_resumes(job_description, resumes):
    """Match resumes using SciBERT & Cosine Similarity with Preferred Skills Boost"""
    job_text = preprocess_text(job_description)
    preferred_skills = extract_preferred_skills(job_description)

    # Vectorize job description
    job_vector = vectorize_text(job_text)

    matched_resumes = []
    for resume in resumes:
        resume_text = preprocess_text(
            f"{resume.get('programming_languages', '')} {resume.get('ml_tools', '')} {resume.get('dev_tools', '')} {resume.get('courseworks', '')} {resume.get('soft_skills', '')}"
        )
        resume_vector = vectorize_text(resume_text)

        # Compute Cosine Similarity
        score = cosine_similarity(job_vector, resume_vector)[0][0] * 100

        # ✅ Preferred Skills Bonus: +10 points per matched skill
        resume_skills = set(word_tokenize(resume_text))
        preferred_bonus = sum(1 for skill in preferred_skills if skill in resume_skills) * 10

        # ✅ Final Match Score (Cosine Similarity + Preferred Skills)
        final_score = min(score + preferred_bonus, 100)  # Cap at 100

        matched_resumes.append({
            "name": resume["name"],
            "email": resume["email"],
            "match_score": round(final_score, 2)
        })

    return sorted(matched_resumes, key=lambda x: x["match_score"], reverse=True)