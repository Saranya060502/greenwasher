from flask import Flask, request, jsonify
import os
from openai import OpenAI
import requests, justext
from flask_cors import CORS

YOUR_API_KEY = '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'

client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_carbon_claims(url):
    response = requests.get(url)
    paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
    page_text = ""
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            page_text += paragraph.text + "\n"
    return page_text

@app.route('/analyze-sustainability', methods=['POST'])
def analyze_sustainability():
    # Use the URL from the request
    data = request.json
    url = data.get('pageURL', '').strip()
    
    if not url:
        return jsonify({"error": "URL cannot be empty."}), 400
    
    page_text = extract_carbon_claims(url)
    if not page_text:
        return jsonify({"error": "Failed to extract claims from the website."}), 400
    
    # First message to extract claims
    extract_claims_messages = [
        {
            "role": "system",
            "content": "You are an expert in sustainability and corporate environmental claims analysis."
        },
        {
            "role": "user",
            "content": f"Extract the main sustainability and carbon/energy-related claims from this Amazon webpage text: {page_text[:4000]}"
        }
    ]
    
    claims_response = client.chat.completions.create(
        model="sonar",
        messages=extract_claims_messages,
    )
    
    extracted_claims = claims_response.choices[0].message.content
    
    # Second message to analyze and fact-check the claims
    analyze_claims_messages = [
        {
            "role": "system",
            "content": "You are a fact-checker specializing in corporate sustainability claims. Provide evidence-based analysis."
        },
        {
            "role": "user",
            "content": f"""
            Analyze these sustainability claims from Amazon: {extracted_claims}
            
            For each claim:
            1. Identify the specific percentage or metric Amazon claims
            2. Provide counter-evidence from reliable sources
            3. Calculate an actual percentage based on evidence
            
            Format your response with this EXACT structure:
            
            SUMMARY OF CLAIMS VS REALITY:
            - Claimed: [Overall percentage Amazon claims for sustainability achievement]
            - Actual: [Overall percentage based on evidence]
            
            DETAILED ANALYSIS:
            [Then provide your detailed analysis for each claim]
            
            The SUMMARY section must appear at the very beginning of your response, before any other text.
            Be specific about percentages where possible.
            """
        }
    ]
    
    analysis_response = client.chat.completions.create(
        model="sonar",
        messages=analyze_claims_messages,
    )
    
    analysis_result = analysis_response.choices[0].message.content
    
    return jsonify({
        "analysis": analysis_result
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
