
from flask import Flask, request, jsonify
import os
from openai import OpenAI
import requests, justext

YOUR_API_KEY = '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'

client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

app = Flask(__name__)

AMAZON_URL = "https://sustainability.aboutamazon.com/climate-solutions/carbon-free-energy"

def extract_carbon_claims(url):
    response = requests.get(url)
    paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
    policy_text = ""
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            policy_text += paragraph.text + "\n"
    return policy_text

@app.route('/analyze', methods=['POST'])
def analyze():
    policy_text = extract_carbon_claims(AMAZON_URL)
    if not policy_text:
        return jsonify({"error": "Failed to extract claims from the website."}), 400

    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {   
            "role": "user",
            "content": (
                "Analyze the sustaininbilty part of the Amazon website. "
            ),
        },
    ]
    
    # chat completion without streaming
    response = client.chat.completions.create(
        model="sonar",
        messages=messages,
    )

    # chat completion with streaming
    response_stream = client.chat.completions.create(
        model="sonar",
        messages=messages,
        stream=True,
    )

    print(response.choices[0].message.content)
    
    # result = response.choices[0].message.content.strip()
    # try:
    #     truth_percentage = int(result.split('truth')[1].split(':')[1].split()[0])
    #     lie_percentage = int(result.split('lie')[1].split(':')[1].split()[0])
    # except:
    #     return jsonify({"error": "Invalid response format from AI."}), 500
    
    return jsonify({"truth": 'pass', "lie": 'pass'})

if __name__ == '__main__':
    app.run(debug=True)













