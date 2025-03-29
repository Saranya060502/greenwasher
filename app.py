
from Flask import Flask, request, jsonify
import os
from openai import OpenAI
import requests, justext

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

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

@app.route('/analyze', methods=['GET'])
def analyze():
    policy_text = extract_carbon_claims(AMAZON_URL)
    if not policy_text:
        return jsonify({"error": "Failed to extract claims from the website."}), 400

    messages = [
        {"role": "user", "content": policy_text},
        {"role": "user", "content": "Analyze the carbon energy claims in the text and determine the percentage of truth and lies. Provide only numerical values in the response as 'truth': X and 'lie': Y."},
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        model=model_name,
    )
    
    result = response.choices[0].message.content.strip()
    try:
        truth_percentage = int(result.split('truth')[1].split(':')[1].split()[0])
        lie_percentage = int(result.split('lie')[1].split(':')[1].split()[0])
    except:
        return jsonify({"error": "Invalid response format from AI."}), 500
    
    return jsonify({"truth": truth_percentage, "lie": lie_percentage})

if __name__ == '__main__':
    app.run(debug=True)
