# Local imports
import datetime
import logging
import pickle
import psycopg2
# Third part imports
from flask import render_template
from flask import Flask
from flask import request
from flask import jsonify
import pandas as pd
import joblib
import gzip
import json
from sklearn.preprocessing import StandardScaler
import os
import joblib
import numpy as np
import random


from modules.functions import get_model_response


conn = psycopg2.connect(
    dbname="internetOfThings",
    user="admin",
    password="admin",
    host="postgres",
    port="5432"
)


app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    majority_vote = 0
    feature_dict = request.get_json()
    if not feature_dict:
        return {
            'error': 'Body is empty.'
        }, 500

    try:
        # Caminho hardcoded para o StandardScaler
        scaler_path = './scaler/standard_scaler.pkl'
        if not os.path.exists(scaler_path):
            return {'error': 'StandardScaler not found at the specified path.'}, 500
        

        scaler = pickle.load(open('./scaler/standard_scaler.pkl', 'rb')) 

       
        # Extrair e transformar os dados
        raw_data = [feature_dict[i] for i in feature_dict.keys()]
        data = scaler.transform([raw_data])
        

        # Caminho para os modelos
        model_dir = './model'
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.dat.gz')]
        if not model_files:
            return {'error': 'No models found in the directory.'}, 500


                # Coletar previsões de todos os modelos
        predictions = []
        for model_file in model_files:
            model_path = os.path.join(model_dir, model_file)
            model = joblib.load(model_path)
            response = get_model_response(data, model)
            if(response['status'] == 200):
                predictions.append(response['prediction'])  
        
        
        print(predictions)

        # Aplicar votação por maioria
        if(np.sum(predictions)/len(predictions) > 0.5):
          majority_vote = 1

    except Exception as e:
        return {'error': str(e)}, 500

    meters_per_second = get_user_info("meters_per_second")
    height = get_user_info("height")
    weight = get_user_info("weight")
        
    insert_activity(majority_vote,weight,height,meters_per_second)



@app.route('/health', methods=['GET'])
def health():
    """Return service health"""
    return 'ok'

@app.route('/menu', methods=['GET', 'POST'])
def menuPage():
    return render_template('menu.html')

@app.route('/updateUser', methods=['GET', 'POST'])
def updateUserPage():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        age = request.form.get('age', type=int)
        gender = request.form.get('gender')
        weight = request.form.get('weight', type=float)
        height = request.form.get('height', type=float)
        meters_per_second = get_meters_per_second(age, gender)

        try:
            with conn.cursor() as cursor:
                
                cursor.execute("DELETE FROM user_info")

                cursor.execute(
                    """
                    INSERT INTO user_info (first_name, last_name, age, gender, weight, height, meters_per_second)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (first_name, last_name, age, gender, weight, height, meters_per_second)
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            return {'error': str(e)}, 500

        # Confirm successful insertion
        return render_template('updateUserSuccesfull.html')

    # For GET requests, render the HTML form
    return render_template('updateUser.html')


    

def get_meters_per_second(age: int, gender: str) -> float:
   
    gender = gender.lower()

    if 20 <= age <= 29:
        return 1.36 if gender == "male" else 1.34
    elif 30 <= age <= 39:
        return 1.43 if gender == "male" else 1.34
    elif 40 <= age <= 49:
        return 1.43 if gender == "male" else 1.39
    elif 50 <= age <= 59:
        return 1.43 if gender == "male" else 1.31
    elif 60 <= age <= 69:
        return 1.34 if gender == "male" else 1.24
    elif 70 <= age <= 79:
        return 1.26 if gender == "male" else 1.13
    elif 80 <= age <= 89:
        return 0.97 if gender == "male" else 0.94
    else:
        raise ValueError("Age out of supported range (20-89)")
    

def insert_activity(prediction: int, weight: float, height: float, meters_per_second: float):
    try:
        # If prediction is 1, double the meters_per_second
        if prediction == 1:
            meters_per_second *= 2

        with conn.cursor() as cursor:
            # Insert data into the activity_table
            cursor.execute(
                """
                INSERT INTO activity_table (activity_time, activity_status, weight, height, meters_per_second)
                VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s)
                """,
                (prediction, weight, height, meters_per_second)
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error inserting activity: {str(e)}")


def get_user_info(data):
    try:
        with conn.cursor() as cursor:
            # Retrieve the most recent meters_per_second from the user_info table
            cursor.execute(
                """SELECT """  + data +
            """ FROM 
                user_info
            ORDER BY 
                id DESC  
            LIMIT 1; """
            )
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error retrieving meters_per_second: {str(e)}")
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, ssl_context=('/certs/server.crt', '/certs/server.key'))
