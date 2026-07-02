import pandas as pd
import re
import nltk
import spacy
from nltk.corpus import stopwords

nltk.download('stopwords')

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))



# CLEAN TEXT FUNCTION

def clean_text(text):
    text = str(text).lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    return text



# APPLY TO DATASET

def preprocess_dataset(input_path, output_path):
    df = pd.read_csv(input_path)

    print("Cleaning dataset...")

    df['text'] = df['text'].apply(clean_text)

    df = df[df['text'].str.strip() != ""]

    df.to_csv(output_path, index=False)

    print(f"Saved cleaned dataset to {output_path}")



# MAIN

if __name__ == "__main__":
    input_path = "data/processed/merged_emails.csv"
    output_path = "data/processed/cleaned_emails.csv"

    preprocess_dataset(input_path, output_path)