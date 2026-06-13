import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_gemini(question, data_context=""):
    prompt = f"""You are QueryMy — an expert data analyst assistant built by Ananya Gautam.

Dataset information:
{data_context}

User question: {question}

Answer clearly and concisely like a senior business analyst would.
If numbers are involved, be specific. Keep it under 5 lines."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_sql(question, schema):
    prompt = f"""You are a SQL expert. Generate a SQL query for this question.

Schema:
{schema}

Question: {question}

Rules:
- Table name is always: data
- Return ONLY the SQL query, nothing else
- No markdown, no explanation, just the query"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def auto_insight(data_summary):
    prompt = f"""You are a senior business analyst. A new dataset was just uploaded.

Dataset info:
{data_summary}

Give an executive summary in exactly this format:
📊 OVERVIEW: [1 line about what this dataset is]
🔑 KEY FINDING 1: [most important insight]
🔑 KEY FINDING 2: [second important insight]
🔑 KEY FINDING 3: [third important insight]
⚠️ WATCH OUT: [one risk or anomaly to investigate]
💡 RECOMMENDATION: [one actionable business recommendation]

Be specific with numbers. Sound like a McKinsey analyst."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def self_loop_agent(data_summary, loops=7):
    results = []
    
    # First question is auto-generated from data
    current_question = f"""Looking at this dataset, what is the single most important business question to investigate first?
Dataset: {data_summary}
Return ONLY the question, nothing else."""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": current_question}]
    )
    question = response.choices[0].message.content.strip()
    
    for i in range(loops):
        # Answer the current question
        answer_prompt = f"""You are a senior business analyst.
Dataset: {data_summary}
Question: {question}
Give a sharp, specific answer in 2-3 lines with numbers where possible."""
        
        answer_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": answer_prompt}]
        )
        answer = answer_response.choices[0].message.content.strip()
        results.append({"question": question, "answer": answer})
        
        # Wait to avoid rate limit
        import time
        time.sleep(3)
        
        # Generate next question from previous answer
        if i < loops - 1:
            next_prompt = f"""Based on this finding, what is the single most important follow-up business question?
Finding: {answer}
Return ONLY the next question, nothing else."""
            
            next_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": next_prompt}]
            )
            question = next_response.choices[0].message.content.strip()
    
    return results

def natural_language_filter(question, schema, data_summary):
    prompt = f"""You are a Python/Pandas expert.
    
Dataset schema: {schema}
Dataset info: {data_summary}
User request: {question}

Generate ONLY a pandas query string that can be used with df.query() or df[condition].
Examples:
- "show orders above 500" → df[df['Sales'] > 500]
- "show only Delhi customers" → df[df['City'] == 'Delhi']
- "orders above 500 from New York" → df[(df['Sales'] > 500) & (df['City'] == 'New York')]

Return ONLY the pandas code, nothing else. Start with df["""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def predict_trend(data_summary):
    prompt = f"""You are a senior data scientist and business forecaster.

Dataset: {data_summary}

Based on this data:
1. Identify the main trend (growing/declining/stable)
2. Predict what happens next month with specific numbers
3. Give confidence level (High/Medium/Low)
4. Give 2 actionable recommendations

Format exactly like this:
📈 TREND: [current trend with numbers]
🔮 PREDICTION: [next month forecast with specific numbers]
🎯 CONFIDENCE: [High/Medium/Low — reason why]
💡 ACTION 1: [specific recommendation]
💡 ACTION 2: [specific recommendation]

Be specific with numbers. Sound like a Bloomberg analyst."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{{"role": "user", "content": prompt}}]
    )
    return response.choices[0].message.content.strip()
                

def clean_data_suggestions(data_summary, df_info):
    prompt = f"""You are a data cleaning expert.

Dataset info:
{data_summary}

Column details:
{df_info}

Identify ALL data quality issues and return ONLY a JSON array like this:
[
  {{"issue": "Missing values in Sales column", "fix": "fill_mean", "column": "Sales", "severity": "High"}},
  {{"issue": "Duplicate rows found", "fix": "drop_duplicates", "column": "all", "severity": "Medium"}}
]

fix must be one of: fill_mean, fill_median, fill_zero, fill_unknown, drop_duplicates, drop_negative, strip_whitespace
Return ONLY the JSON array, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def generate_dashboard_config(data_summary, columns):
    prompt = f"""You are a data visualization expert.

Dataset: {data_summary}
Available columns: {columns}

Generate exactly 4 charts that tell the best business story from this data.
Return ONLY a JSON array:
[
  {{"chart_type": "bar", "title": "Sales by Category", "x_col": "Category", "y_col": "Sales"}},
  {{"chart_type": "line", "title": "Revenue Over Time", "x_col": "Date", "y_col": "Revenue"}},
  {{"chart_type": "pie", "title": "Orders by Region", "x_col": "Region", "y_col": "Orders"}},
  {{"chart_type": "bar", "title": "Top Products by Profit", "x_col": "Product", "y_col": "Profit"}}
]

Use ONLY exact column names from the list provided.
Return ONLY the JSON array, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

