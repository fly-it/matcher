from scipy.spatial.distance import cosine

from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

from sentence_transformers import SentenceTransformer

import openai
from openai import OpenAI
# import environ
import string

from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import random
import firebase_admin
import json
import dateutil




# Try to load stopwords, download if not present
try:
    stopwords.words('french')
except LookupError:
    nltk.download('stopwords')

# Try to load wordnet, download if not present
try:
    wordnet.ensure_loaded()
except LookupError:
    nltk.download('wordnet')

model_miniLM = SentenceTransformer('all-MiniLM-L6-v2')

def embed_with_miniLM(text):
    return model_miniLM.encode(text)

def clean_text(text):
    stopwords_set = set(stopwords.words('french') + list(string.punctuation))
    lemmatizer = WordNetLemmatizer()
    raw_text = text

    tokens = word_tokenize(raw_text.lower())
    tokens = [token for token in tokens if token not in stopwords_set]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    cleaned_text = ' '.join(tokens)
    return cleaned_text


def compare_embeddings(embedding1, embedding2):
    similarity = 1 - cosine(embedding1, embedding2)
    return similarity





###### env variables ######
# env = environ.Env()
# environ.Env.read_env()


# client = OpenAI(
#     # This is the default and can be omitted
#     api_key='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',
# )

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Say this is a test",
#         }
#     ],
#     model="gpt-4",
# )


#CHATGPT Functions
def get_completion(instructions, prompt, api_key, gpt_model="gpt-4-1106-preview"):
    # instructions = """You are an NLP super tool you will recieve a job description and you will process it in order to prepare it to be embedded using all-MiniLM-L6-v2. the goal is to convert the job description embedding with a resume embedding to measure the similarity, in order to do that follow the instructions below:
    #                 1- Analyse the job description deeply
    #                 2- extract only the important information about the job
    #                 3- infer any requirements ,skills or technologies needed for this job
    #                 4- in your result don't use any introductory or decrining speech speech, focus on returning only a text relevant to the job description
    #                 5- the output should be in the same language of the input
    #                 6- return the result as a text and make sure that it is not too long"""

    client = OpenAI(
    # This is the default and can be omitted
        api_key= api_key,
    )

    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": "Say this is a test",
    #         }
    #     ],
    #     model="gpt-4",
    # )
    completion = client.chat.completions.create(
        model = gpt_model,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt}
        ]
    )
    # print(completion.choices[0].message)

    return completion.choices[0].message.content

def process_job_description(message, api_key):
    
    instructions = """You are an NLP super tool you will recieve a job description and you will process it in order to prepare it to be embedded using all-MiniLM-L6-v2. the goal is to convert the job description embedding with a resume embedding to measure the similarity, in order to do that follow the instructions below:
                    1- Analyse the job description deeply
                    2- extract only the important information about the job
                    3- infer any requirements ,skills or technologies needed for this job
                    4- in your result don't use any introductory or decrining speech speech, focus on returning only a text relevant to the job description
                    5- the output should be in the same language of the input
                    6- return the result as a text"""
    response = get_completion(instructions, message, api_key)
    # print(response)
    return response

def process_resume(message, api_key):
    
    instructions = """You are an NLP super tool you will recieve a resume/cv and you will process it in order to prepare it to be embedded using all-MiniLM-L6-v2. the goal is to convert the job description embedding with a resume embedding to measure the similarity, in order to do that follow the instructions below:
                    1- Analyse the resume deeply
                    2- extract only the important information from the resume and include only skills related information and don't mention the previous work places
                    3- infer any experiences ,skills or technologies mentioned explicitly or implicitly
                    4- in your result don't use any introductory or decrining speech speech, focus on returning only a text relevant to the resume
                    5- don't include personal or contact information
                    6- the output should be in the same language of the input
                    7- return the result as a text and make sure that the text is not too much long"""
    response = get_completion(instructions, message, api_key)
    # print(response)
    return response