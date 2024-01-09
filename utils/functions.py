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

certif = {
    "type": "service_account",
    "project_id": "vast-service-350313",
    "private_key_id": "af3d82d49f33bd3decadf3b97d3c76282d1aeec4",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtK1Icp0svm5A9\noi5wsercBLab+JWSB0tP1Aq+E8GNtMcLZ3TzJgYTOetq2lZcw5o8NZKt3urj8HvR\nMAJzErWTlJKrFSeNBXkII/sX6uRk0QbO1wmmy0aOxBsFYDW0C5aAeGKqt22ojaCh\nU9SkhlLOWSJxizTD2N1wrc6a15F/qy2cP7aUy3kIiyinytbBTMsCGtDYQJQXKKKP\njAcGJ1FHaVQPsDwGafB6/cMRUXY+c8SFLQg2Db57XVIA0VZ+kZtkMPAR1p7Qar+a\nae8xpfCS4XJ4cs7G9LvBnpPS2AdSbxhzZ/qUL1v18Ob4Bh747B8e4R+e1IJK4jp2\ndRndFNQbAgMBAAECggEAOo5okLndSbbv2neJ/p+bDFUnrqwrX5rJ06+fBlFF5PYZ\nTHjqagIUkdHHEnXMOEgIUo3HELZNdVBvffgfC+xqrAHUareXjS8pkyAfmyHZo2Gv\nTKgYYmdgb4xOms3CuyQj+0M6EgI+uX1SsNrZD91ACPjJFd39tLATiTOspl14nNOl\n4R0D9oiHfvl3v2Qp7HQUOZ/DBYWOJs23zq2VaUho2R/bQs06nSzgGAKvHmo7DVpf\nyW18kcIL+rN+reY70+k+XhXL0oONanKzJA5cCWSrZZJkXO0/QB4kppLiVfCy6E8t\npNyVpgBPvlZcCKUm8LSL4jZ9vad/fnmnlgIwEWBNiQKBgQDdVC5ZKpy/tgaACOW7\nGI8p3BSNgesvSi7nEY5Yj9GJJysUZ0eqe9o8NOe4Dt2PEcLKINP5rmYg59T/uxUS\naXm1F3QfSDU6kcxQOL3zO8xy9J+ZIImWUJcK+a/kqF68VKKSGagI3qBFTiha2Jn2\n6LOW7O+gZQ0woNcuYIq60D1D7QKBgQDIS9LJrBGFQ5UE7tWo3Iz3IdfFYmj9Ssys\nV9eg9a852+ri4KYN2ITamqLwaofY/mXyhwjr+b6440H6WM74tH8FAC6FcWqXLTV9\n0vpW1HHxS54u+TDINYViots7ZUK5T61hsjj6cnpbHZZ0UHse81vW0dD3srBUQ4Hn\nOkWPffQHJwKBgQCQx15CKaO7rGB4JFnSl3Ae273+CvxDRO2FbXCF8h4I77w4bo7s\nsHPDaoAhYGgCDIY1HmBLNY/M+pnUZxaTordghGULiXp4Q6M43sUydO16TRaRXj1i\nPHlxTn+GvbSq0Vo+49WNZ8PDUisHsiSU5QeFNJxTeYa1RqE7zx8wsMNCyQKBgEIr\nooiTuvoOuKV3jciKjFt8p78C4vKDCpkJMChx4iC4QaIQW2uJk2Jw4dGRMC4E5YM5\nDz5+NH76PSrKuh2565ioVbYqIO+utNRLpf6XkskHlUupcW9DFzzd1pWJv4BfDUWQ\nTniW50tAvBrTF8nC1h1jFakvNEeyQbE1NBPSpZLTAoGBALPq5Pgnd4sAXMP1RVDR\n50K5GDvmICvfg1Fhsj8xPJK4PiEuauytD467u4zr/Z5AzpIWoERr/eRon0JZmhTI\nvRXmZMCcufqNYhrUVHzRFiCCEwK/xc3EDEUqijVeSsmJQ7uY/G0fJXSF9CpfrBhl\nyR7wEwIA853WQ7wZBJbsmdb9\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-zs052@vast-service-350313.iam.gserviceaccount.com",
    "client_id": "112956158234051820344",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-zs052%40vast-service-350313.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"   
}


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


client = OpenAI(
    # This is the default and can be omitted
    api_key='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',
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4",
)


#CHATGPT Functions
def get_completion(instructions, prompt, gpt_model="gpt-4-1106-preview"):
    # instructions = """You are an NLP super tool you will recieve a job description and you will process it in order to prepare it to be embedded using all-MiniLM-L6-v2. the goal is to convert the job description embedding with a resume embedding to measure the similarity, in order to do that follow the instructions below:
    #                 1- Analyse the job description deeply
    #                 2- extract only the important information about the job
    #                 3- infer any requirements ,skills or technologies needed for this job
    #                 4- in your result don't use any introductory or decrining speech speech, focus on returning only a text relevant to the job description
    #                 5- the output should be in the same language of the input
    #                 6- return the result as a text and make sure that it is not too long"""
    completion = client.chat.completions.create(
        model = gpt_model,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt}
        ]
    )
    # print(completion.choices[0].message)

    return completion.choices[0].message.content

def process_job_description(message):
    
    instructions = """You are an NLP super tool you will recieve a job description and you will process it in order to prepare it to be embedded using all-MiniLM-L6-v2. the goal is to convert the job description embedding with a resume embedding to measure the similarity, in order to do that follow the instructions below:
                    1- Analyse the job description deeply
                    2- extract only the important information about the job
                    3- infer any requirements ,skills or technologies needed for this job
                    4- in your result don't use any introductory or decrining speech speech, focus on returning only a text relevant to the job description
                    5- the output should be in the same language of the input
                    6- return the result as a text"""
    response = get_completion(instructions, message)
    # print(response)
    return response

def process_resume(message):
    
    instructions = """You are an NLP super tool you will recieve a resume/cv and you will process it in order to prepare it to be embedded using all-MiniLM-L6-v2. the goal is to convert the job description embedding with a resume embedding to measure the similarity, in order to do that follow the instructions below:
                    1- Analyse the resume deeply
                    2- extract only the important information from the resume and include only skills related information and don't mention the previous work places
                    3- infer any experiences ,skills or technologies mentioned explicitly or implicitly
                    4- in your result don't use any introductory or decrining speech speech, focus on returning only a text relevant to the resume
                    5- don't include personal or contact information
                    6- the output should be in the same language of the input
                    7- return the result as a text and make sure that the text is not too much long"""
    response = get_completion(instructions, message)
    # print(response)
    return response

cred = credentials.Certificate(certif)
try:
    # Try to get the existing app
    firebase_app = firebase_admin.get_app()
except ValueError:
    # If it's not initialized, initialize and return the app
    cred = credentials.Certificate(certif)
    firebase_app = firebase_admin.initialize_app(cred)

firestore_client = firestore.client()
collection_ref = firestore_client.collection('candidates')

def get_resumes_from_firestore():
    names = []
    resumes = {}
    for doc in collection_ref.stream():
        data = doc.to_dict()
        if 'full_name' in data.keys():
            names.append(data['full_name'])
            resumes[data['full_name']] = str(data)
            print(data['full_name'])
    return resumes, names

