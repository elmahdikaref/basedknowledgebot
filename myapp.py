# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UYZFeBMTfInJPUjPD6pBIeqRwzAbT2t9
"""

from flask import Flask, request, jsonify
import google.generativeai as genai
import clickhouse_connect
import time
import subprocess
#from google.colab import userdata

#API_KEY=userdata.get('API_KEY')
    # Configure Google Generative AI
genai.configure(api_key='AIzaSyC_14koQHhgY0iflcD6vHVTsyGfYiNDkII')
def get_embeddings(text):
        model = 'models/embedding-001'
        embeddingg = genai.embed_content(model=model, content=text, task_type="retrieval_document")
        return embeddingg['embedding']

client = clickhouse_connect.get_client(
    host='msc-36a83f0b.us-east-1.aws.myscale.com',
    port=443,
    username='elmahdi_karef_org_default',
    password='passwd_e5MKRCbKibvXQa'
)

def get_relevant_docs(user_query):
    # Call the get_embeddings function again to convert user query into vector embeddings
    query_embeddings = get_embeddings(user_query)

    # Initialize list to store results
    all_results = []

    # Query each document table and collect results
    for i in range(1, 11):
        table_name = f"default.document_{i}"
        results = client.query(f"""
            SELECT page_content,
            distance(embeddings, {query_embeddings}) as dist FROM {table_name} ORDER BY dist LIMIT 3
        """)
        for row in results.named_results():
            all_results.append({
                'page_content': row['page_content'],
                'dist': row['dist']
            })

    # Sort all results by distance
    all_results.sort(key=lambda x: x['dist'])

    # Extract top results
    relevant_docs = [result['page_content'] for result in all_results[:10]]
    #print(relevant_docs)
    return relevant_docs

def make_rag_prompt(query, relevant_passage):
    relevant_passage = ' '.join(relevant_passage)
    prompt = (
      # f"please answer question that is usually about the context of pثtroleum engineering field'\n"
      # f"if the question is out of the context of petroleum engineering you can also answer it easy\n\n"
       f"and if the help that is below the question doesn't help you to answer or irrelevant to the question context please ignore this help and answer the question provided without using the help.'\n "
      #  f"However, if the help is not helpful or irrelevant, answer the question based on your own knowledge. "
      f"if the question below is about the petroleum engineering field context please response for it in detail, and if it's talk about anothe field you can answer it normally"
      #  f"the user that poses the question is usually a student, engineer or reseacher in the petroleum engineering field "
      #  f"so please respond in detail and don't worry of the user don't uderstand you because he has high level of knowledge in the petroleum engineerig field.\n\n"
        f"if the question is Hi or something like Welcome try response to him simply like: hi, how can I help you. or something like that"
        f"QUESTION: '{query}'\n"
        f"help: '{relevant_passage}'\n\n"
        #f"ANSWER:"
    )
    return prompt
# f"If the passage provided contains relevant information, use it to answer the question. "

import google.generativeai as genai

def generate_response(user_prompt):
    model = genai.GenerativeModel('gemini-pro')
    answer = model.generate_content(user_prompt)
    return answer.text

def generate_answer(query):
    relevant_text = get_relevant_docs(query)
    text = " ".join(relevant_text)
    prompt = make_rag_prompt(query, relevant_passage=relevant_text)
    answer = generate_response(prompt)
    return answer

def fallback_to_gemini_api(query):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(query)
    return response.text


app = Flask(__name__)

@app.route('/query', methods=['POST'])
def _q_ue___er_y_():
    user_query = request.json['query']
    answer = generate_answer(user_query)
    #trimmed_answer = answer.strip()  # Ensure trimming here
    return jsonify({"response": answer})

if __name__ == '__main__':
    # Authenticate ngrok
   # subprocess.run(["ngrok", "authtoken", "2ihyaoXJAvR68SSGxv7M1NYzMQ3_726nCKncYYqecDx17VJo3"])

    # Start ngrok with the specified domain
  #  subprocess.Popen(["ngrok", "http", "--domain=swine-proper-toad.ngrok-free.app", "80"])

    # Pause to ensure ngrok initializes
  #  time.sleep(10)

    # Run the Flask app on port 80
#    app.run(port=80)
    app.run(host='0.0.0.0', port=10000)
