import joblib 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import scipy.sparse as sp 

model=joblib.load("C:\Users\Ethel\Desktop\Shecodes\British-Airways\models\final_model.pkl")
tfid=joblib.load("C:\Users\Ethel\Desktop\Shecodes\British-Airways\models\tfidf_vectorizer.pkl")

analyzer = SentimentIntensityAnalyzer()

