import pandas as pd
import os


# STANDARD FORMAT FUNCTION

def standardize(df, text_col, label_col):
    df = df[[text_col, label_col]].copy()
    df.columns = ['text', 'label']


    return df


# SMART COLUMN DETECTION

def detect_columns(df):
    cols = df.columns

    text_candidates = ['text', 'email text', 'body', 'message', 'content']
    label_candidates = ['label', 'email type', 'type', 'class']

    text_col = None
    label_col = None

    for col in cols:
        if col in text_candidates:
            text_col = col
        if col in label_candidates:
            label_col = col

    return text_col, label_col



# LOAD INDIVIDUAL DATASETS

def load_all_datasets(base_path):
    datasets = []

    for file in os.listdir(base_path):
        if file.endswith(".csv"):
            path = os.path.join(base_path, file)
            print(f"Loading {file}...")

            df = pd.read_csv(path)

            # Normalize column names
            df.columns = [col.lower() for col in df.columns]
            def convert_label(x):
                x = str(x).lower().strip()

                if x in ["1", "yes", "true"]:
                    return 1
                if x in ["0", "no", "false"]:
                    return 0

                if any(word in x for word in ["phish", "spam", "fraud", "scam", "malicious"]):
                    return 1

                if any(word in x for word in ["ham", "legit", "safe", "normal"]):
                    return 0

                return 1  # fallback

            df['label'] = df['label'].apply(convert_label)
            try:
                # Try common patterns
                # Combine subject + body if both exist
                if 'subject' in df.columns and 'body' in df.columns:
                    df['text'] = df['subject'].fillna('') + " " + df['body'].fillna('')

                    # Detect columns automatically
                    text_col, label_col = detect_columns(df)

                    if text_col and label_col:
                        datasets.append(standardize(df, text_col, label_col))
                    else:
                        print(f"⚠️ Skipping {file} (unknown format)")

            except Exception as e:
                print(f"Error processing {file}: {e}")

    return datasets



# MERGE DATASETS

def merge_datasets(datasets):
    combined_df = pd.concat(datasets, ignore_index=True)

    print("\nFINAL LABEL DISTRIBUTION:")
    print(combined_df['label'].value_counts())

    print("\nNORMALIZED DISTRIBUTION:")
    print(combined_df['label'].value_counts(normalize=True))

    print("Total samples:", len(combined_df))
    print(combined_df['label'].value_counts())

    return combined_df



# SAVE

def save_merged(df, path):
    df.to_csv(path, index=False)
    print(f"Merged dataset saved to {path}")



# MAIN

if __name__ == "__main__":
    base_path = "D:\\Project Masters\\phishing detection system\\data\\raw"
    output_path = "D:\\Project Masters\\phishing detection system\\data\\processed\\merged_emails.csv"

    datasets = load_all_datasets(base_path)
    merged_df = merge_datasets(datasets)
    save_merged(merged_df, output_path)

print(merged_df['label'].value_counts(normalize=True))
