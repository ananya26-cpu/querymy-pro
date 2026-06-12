import pandas as pd

def load_file(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file)
    except Exception as e:
        return None

def get_data_summary(df):
    summary = f"Shape: {df.shape}\n\n"
    summary += f"Columns: {list(df.columns)}\n\n"
    summary += f"Data Types:\n{df.dtypes.to_string()}\n\n"
    summary += f"Basic Stats:\n{df.describe().to_string()}"
    return summary

def detect_anomalies(df):
    results = []
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        mean = df[col].mean()
        std = df[col].std()
        outliers = df[(df[col] > mean + 3*std) | (df[col] < mean - 3*std)]
        if len(outliers) > 0:
            results.append(f"Column '{col}': {len(outliers)} unusual values detected (far from average)")
    if not results:
        return "No anomalies detected."
    return "\n".join(results)
