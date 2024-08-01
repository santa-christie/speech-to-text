from flask import Flask, request, render_template, jsonify
import os
import pandas as pd
import speech_recognition as sr

app = Flask(__name__)

recognizer = sr.Recognizer()

def load_existing_data(csv_file):
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame(columns=["Tree Name", "Status", "Color"])

def update_tree_status(df, tree_name, new_status, new_color):
    if tree_name in df["Tree Name"].values:
        df.loc[df["Tree Name"] == tree_name, ["Status", "Color"]] = new_status, new_color
    else:
        new_row = pd.DataFrame({"Tree Name": [tree_name], "Status": [new_status], "Color": [new_color]})
        df = pd.concat([df, new_row], ignore_index=True)
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    csv_file = "tree_status.csv"
    df = load_existing_data(csv_file)
    
    text = request.form['speech_text']
    trees = process_tree_status(text)
    
    for tree in trees:
        df = update_tree_status(df, tree["Tree Name"], tree["Status"], tree["Color"])
    
    df.to_csv(csv_file, index=False)
    return jsonify(df.to_dict(orient='records'))

def process_tree_status(text):
    trees = []
    if text:
        tree_status_list = text.split(',')
        for tree_status in tree_status_list:
            tree_status = tree_status.strip()
            if "good" in tree_status.lower():
                status = "good"
                color = "green"
            elif "bad" in tree_status.lower():
                status = "bad"
                color = "red"
            else:
                status = "unknown"
                color = "unknown"
            
            tree_name = tree_status.split()[0]
            trees.append({"Tree Name": tree_name, "Status": status, "Color": color})
    
    return trees

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio data provided'}), 400
    
    audio_file = request.files['audio_data']
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio)
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand the audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Error with the recognition service: {e}'}), 500

if __name__ == "__main__":
    app.run(debug=True)
