from flask import Flask, request, jsonify, render_template
import requests
import time

app = Flask(__name__)

OPENAI_API_KEY = 'API_KEY'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():

    user_input = request.json.get('message')
    print(f"Recieved message: {user_input}")

    response = get_gpt_response(user_input)
    print(f"GPT-3 response: {response}")

    return jsonify({'response': response})

def get_gpt_response(user_input, retry_count=3):

    headers = {
        'Authorization' : f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model' : 'gpt-3.5-turbo-16k',
        'messages': [{'role': 'user', 'content': user_input}],
        'max_tokens': 300
    }

    for attempt in range(retry_count):
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

        if response.status_code == 200:
            try: 
                return response.json()['choices'][0]['message']['content']
            except (KeyError, IndexError) as e:
                print(f"Error parsing response JSON: {e}")
                print(f"Response JSON: {response.json()}")
                return "An error occured while processing the response from OpenAI."
        elif response.status_code == 429:

            print(f"Request to OpenAI failed with status code:{response.status_code}")
            print(f"Response: {response.text}")
            if attempt < retry_count - 1:
                print("Retrying...")
                time.sleep(2 ** attempt)
            else:
                return "You have exceeded your current quota. Please check your plan and billing "
            
        else: 
            print(f"Request to OpenAI failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return "An error occured while communicating with OpenAI."
        
if __name__ == '__main__':
    app.run(debug=True)
