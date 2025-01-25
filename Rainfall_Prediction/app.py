from flask import Flask, render_template, request, jsonify
import requests

# Importing modules required to load model.
from joblib import load
import pandas as pd 
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Loading model
model = load("h2/h1 (1)/h1/Rainfall_Prediction.joblib")

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    if request.method == 'POST':
        try:
            city = request.form['city']
            
            if not city:
                return jsonify({'error': 'Please enter both city and country.'})

            api_key = 'e5dccfe743f53b0389cd37b16b9b07ad'  
            response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}')
            data = response.json()
            # print(data)

            if response.ok:
                temperature_celsius = round(data['main']['temp'] - 273.15)
                weather_details = {
                    "Location" : city,
                    'temperature': temperature_celsius,
                    'feels_like': round(data['main']['feels_like'] - 273.15),
                    'max_temp': round(data['main']['temp_max'] - 273.15),
                    'min_temp': round(data['main']['temp_min'] - 273.15),
                    'humidity': data['main']['humidity'],
                    'visibility': round(data['visibility'] / 1000, 2),
                    'wind_speed': data['wind']['speed'],
                    'gust': data['wind']['gust'],
                    'direction': data['wind']['deg'],
                    'sunrise': data['sys']['sunrise'],
                    'sunset': data['sys']['sunset'],
                    'weather_main': data['weather'][0]['main'],
                    'weather_description': data['weather'][0]['description'],
                    'weather_icon': data['weather'][0]['icon'],
                    'pressure': data['main']['pressure']
                }
                print(weather_details)

                df = pd.DataFrame({
                "Location":[city],
                "MinTemp":[weather_details['min_temp']],
                "MaxTemp":[weather_details['max_temp']],
                "Rainfall":[4.20],
                "WindGustDir":["W"],
                "WindGustSpeed":[31],
                "WindDir9am":["W"],
                "WindDir3pm":["N"],
                "WindSpeed9am":[weather_details['wind_speed']],
                "WindSpeed3pm":[weather_details['wind_speed']],
                "Humidity9am":[weather_details['humidity']],
                "Humidity3pm":[weather_details['humidity']],
                "Pressure9am":[1003],
                "Pressure3pm":[1007],
                "Temp9am":[weather_details['temperature']],
                "Temp3pm":[weather_details['temperature']],
                "RainToday":["Yes"],
                "Day_of_Month":[26],
                "Month":[4]
                })
                
                label_encoder = LabelEncoder()
                df['RainToday'] = df['RainToday'].map({'Yes': 1, 'No': 0})
                df['Location'] = label_encoder.fit_transform(df['Location'])
                df['WindDir9am'] = label_encoder.fit_transform(df['WindDir9am'])
                df['WindDir3pm'] = label_encoder.fit_transform(df['WindDir3pm'])
                df['WindGustDir'] = label_encoder.fit_transform(df['WindGustDir'])

                # Use this predicions variable wherever you want to use it.
                # This is list containing one value 1 or 0 1 means yes and 0 means no.
                predictions = model.predict(df)

                print(predictions)

                if predictions[0] == 1:
                    weather_details["predictions"] = "Yes, tomorrow will rain"
                else:
                    weather_details["predictions"] = "No, tomorrow will not rain"

                return render_template('weather.html', **weather_details)
            else:
                return render_template('home.html', error=data['message'])

        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
