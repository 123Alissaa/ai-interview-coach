import streamlit as st
from textblob import TextBlob
import nltk
nltk.download('punkt')
nltk.download('brown')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
import csv
import os
import random
from datetime import datetime
#import ollama
import pandas as pd
import matplotlib.pyplot as plt



# Sample behavioral interview questions
sample_questions = [
    "Tell me about a time you faced a conflict at work and how you dealt with it.",
    "Describe a situation where you showed leadership.",
    "Give an example of a goal you set and how you achieved it.",
    "Tell me about a time you made a mistake and how you handled it."
]

st.set_page_config(page_title="AI Interview Coach", page_icon="🧠")
st.title("🧠 AI Interview Coach")
st.write("Practice behavioral interview questions and get instant feedback!")

# Option to select question mode
mode = st.radio("Choose how you want to practice:", ("Get a random question", "Write your own question"))

# Select or input question
if mode == "Get a random question":
    question = random.choice(sample_questions)
else:
    question = st.text_input("Enter your own interview question")

if question:
    st.markdown(f"### 📝 Question: {question}")
    response = st.text_area("Your Response:")
    confidence = st.slider("How confident did you feel answering?", 1, 5, 3)

    if st.button("Analyze"):        
        blob = TextBlob(response)
        polarity = blob.sentiment.polarity
        word_count = len(blob.words)

        # Analyze based on heuristics
        filler_words = ["like", "just", "maybe", "kind of", "sort of", "you know"]
        clarity_score = 5 - sum(word in response.lower() for word in filler_words)
        length_score = 5 if 30 <= word_count <= 80 else 2
        positivity_score = 5 if polarity > 0.2 else 3 if polarity > 0 else 2

        # Display feedback
        st.subheader("📊 Interview Breakdown")
        st.write(f"Confidence: {confidence}/5")
        st.write(f"Clarity: {max(1, clarity_score)}/5 (based on filler words)")
        st.write(f"Length Appropriateness: {length_score}/5 ({word_count} words)")
        st.write(f"Tone Positivity: {positivity_score}/5 (polarity: {polarity:.2f})")

        # Generate feedback from local model via Ollama
        """try:
            gpt_response = ollama.chat(
                model='mistral',
                messages=[
                    {"role": "system", "content": "You are a helpful and supportive interview coach."},
                    {"role": "user", "content": f"Give constructive and encouraging feedback for this interview answer: {response}"}
                ]
            )
            ai_feedback = gpt_response['message']['content']
            st.subheader("🧠 AI Feedback")
            st.write(ai_feedback)
        except Exception as e:
            ai_feedback = "Error fetching feedback."
            st.error(f"❌ Error fetching AI feedback: {e}")
"""
        # Log session
        log_data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Question": question,
            "Response": response,
            "Confidence": confidence,
            "Clarity Score": clarity_score,
            "Length Score": length_score,
            "Positivity Score": positivity_score,
            "Polarity": polarity,
            "Feedback": ai_feedback
        }

        file_exists = os.path.isfile("session_log.csv")
        with open("session_log.csv", mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=log_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_data)

        st.success("✅ Your response was analyzed and saved!")

# View past sessions
st.subheader("📁 View Past Answers")
if os.path.isfile("session_log.csv"):
    df_log = pd.read_csv("session_log.csv")

    # Filter and sort
    sort_by = st.selectbox("Sort by:", df_log.columns, index=0)
    df_log = df_log.sort_values(by=sort_by, ascending=False)

    search_term = st.text_input("Search by keyword (in response or question):")
    if search_term:
        df_log = df_log[df_log['Response'].str.contains(search_term, case=False) |
                        df_log['Question'].str.contains(search_term, case=False)]

    st.dataframe(df_log.reset_index(drop=True))

    # Download CSV
    csv = df_log.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Log as CSV", csv, "interview_log.csv", "text/csv")

    # Visualize average scores
    st.subheader("📈 Score Trends")
    score_data = df_log[["Confidence", "Clarity Score", "Length Score", "Positivity Score"]].mean()
    fig, ax = plt.subplots()
    score_data.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title("Average Scores Across All Sessions")
    ax.set_ylabel("Score (out of 5)")
    st.pyplot(fig)
else:
    st.info("No responses logged yet. Once you answer a question, your feedback will appear here.")
