import joblib 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import scipy.sparse as sp 
from pathlib import Path

MODEL_PATH=Path("models/final_model.pkl")
VECTORIZER_PATH=Path("models/tfidf_vectorizer.pkl")
model=joblib.load(MODEL_PATH)
tfidf=joblib.load(VECTORIZER_PATH)

analyzer = SentimentIntensityAnalyzer()

def predict_recommendation(review_text:str): 
    ### performing vectorization on the reviews
    tfidf_features = tfidf.transform([review_text])
    scores = analyzer.polarity_scores(review_text)
    vader_features = np.array([[
        scores['neg'],
        scores['neu'],
        scores['pos'],
        scores['compound']
    ]])

    ####combining those polarity scores to the review 
    combined=sp.hstack([tfidf_features, vader_features])
    prediction = model.predict(combined)[0]
    probabilities = model.predict_proba(combined)[0]
    confidence = float(max(probabilities))

    is_likely = bool(prediction == 1)
    label = "Likely to Recommend" if is_likely else "Not Likely to Recommend"

    return {
        "is_likely": is_likely,
        "label": label,
        "confidence": confidence
    }