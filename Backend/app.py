from flask import Flask, request, jsonify
import os
from openai import OpenAI
import requests, justext
#from flask_cors import CORS

YOUR_API_KEY = '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'

client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

app = Flask(__name__)
#CORS(app)  # Enable CORS for all routes

def extract_carbon_claims(url):
    response = requests.get(url)
    paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
    page_text = ""
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            page_text += paragraph.text + "\n"
    return page_text

@app.route('/analyze', methods=['POST'])
def analyze_sustainability():
    # Use the URL from the request
    data = request.json
    url = data.get('pageURL', '').strip()
    print('Working ......')
    
    if not url:
        return jsonify({"error": "URL cannot be empty."}), 400
    
    # page_text = extract_carbon_claims(url)
    # if not page_text:
    #     return jsonify({"error": "Failed to extract claims from the website."}), 400
    
    # First message to extract claims
    extract_claims_messages = [
        {
            "role": "system",
            "content": '''You are an expert in sustainability and corporate environmental claims analysis. You have to provide a cumulative score based on following parameters and the list of 20 index and their weightage attached. Make a cumulative score out of 100. You will analyze the website emntioned based on the following parameters - {
                        "Environmental (40-50%)": {
                        "Key Parameters": ["GHG emissions reduction (15-20%)", "Energy efficiency optimization (12-18%)", "Water stewardship programs (10-15%)", "Circular waste management systems (8-12%)", "Biodiversity preservation initiatives (5-8%)"],
                        "Rationale": "Dominant weighting aligns with Paris Agreement targets and Scope 3 emission tracking requirements"
                        },

                        "Social (25-35%)": {
                        "Key Parameters": ["Supply chain labor standards (10-15%)", "Community development investments (8-12%)", "Workforce diversity metrics (7-10%)", "Occupational health/safety protocols (5-8%)", "Stakeholder grievance mechanisms (3-5%)"],
                        "Rationale": "Emphasis on ethical value chains and just transition frameworks per UN SDGs"
                        },

                        "Governance (15-25%)": {
                        "Key Parameters": ["Climate transition planning (6-10%)", "Board ESG oversight structures (5-8%)", "Anti-corruption compliance systems (4-7%)", "Executive incentive alignment (3-5%)", "Sustainability reporting rigor (2-5%)"],
                        "Rationale": "Integrated governance ensures accountability through TCFD/ISSB reporting standards"
                        },

                        "Dynamic Adjustments": {
                        "Industry-Specific Weighting": "+/- 15% variance for material issues (e.g., +20% water metrics for textiles)",
                        "Performance Benchmarking": "Sector-adjusted against DJSI/FTSE4Good indices",
                        "Controversy Deductions": "Up to 30% penalty for greenwashing incidents"
                        }
                        }
                        You will analyze the copamany in the website based on following indexes and their weightage -
                        {
                            "Revised ESG Rating Framework": {
                                "Index Weightages": {
                                "Core Analytical (48%)": {
                                    "Dow Jones Sustainability Index": 14.0,
                                    "MSCI Global Sustainability": 12.0,
                                    "S&P Global ESG": 10.0,
                                    "CDP Climate Leaders": 8.0,
                                    "FTSE4Good": 4.0
                                },
                                "Independent Research (30%)": {
                                    "Peer-Reviewed Articles": 15.0,
                                    "Independent Media Reports": 15.0
                                },
                                "Specialized Metrics (15%)": {
                                    "Sustainalytics ESG Risk": 6.0,
                                    "LSEG Controversy Penalty": 5.0,
                                    "Trucost Carbon": 4.0
                                },
                                "Regional/Niche (7%)": {
                                    "Euronext Vigeo": 2.0,
                                    "JUST Capital": 2.0,
                                    "Corporate Knights": 3.0
                                }
                                },
                                "Methodology Adjustments": {
                                "Greenwashing Detection Enhancements": [
                                    "+25% weight to media analysis tools (Twitter/LSEG NLP detection models) [4][10]",
                                    "+20% penalty threshold for companies with ≥2 whistleblower incidents [2][13]",
                                    "Peer-reviewed validation required for 30% of environmental claims [3][11]"
                                ],
                                "Normalization Formula": 
                                    "Final Score = (Σ(Core Index Scores × 0.48) + Σ(Independent Research × 0.30) + Σ(Specialized × 0.15) + Σ(Regional × 0.07)) × (1 - LSEG Penalty)"
                                },
                                "Cumulative ESG Rating": "84.2/100",
                                "Key Changes vs Prior Model": {
                                "Independent Research Impact": "+18% weight increase",
                                "Greenwashing Safeguards": "Added media sentiment analysis (Bloomberg/FT keyword tracking) [2][12]",
                                "Verification Requirements": "Mandatory third-party audit for 20% of social metrics [3][11]"
                                },
                                "Validation Metrics": {
                                "Media-Driven Adjustments": {
                                    "Print Media Coverage": "12% score variance explained [12]",
                                    "Whistleblower Incidents": "7.3% average score reduction [2][13]",
                                    "NLP Greenwashing Flags": "Detect 42% more risk cases [4][10]"
                                }
                                },
                                "Citations": [
                                "LSEG's controversy penalty formula [6]", 
                                "Schulich-York media NLP tool [4]",
                                "MIT Sloan 0.61 inter-rater correlation [11]",
                                "RepRisk greenwashing frequency data [13]"
                                ]
                            }
                            }


                        '''
        },
        {
            "role": "user",
            "content": f'Extract the main sustainability and carbon/energy-related claims from this companies url - {url}.'+
                          '''response_format={
            "type": "json_schema",
            "schema": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "cumulative_score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "ratings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Rating Name": {"type": "string"},
                                "score": {"type": "integer"}
                            },
                            "required": ["category", "score"]
                        }
                    },
                    "false_claims": {"type": "string"},
                    "references": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": [
                    "cumulative_score",
                    "ratings",
                    "false_claims",
                    "references"
                ]
            }
        }
        Example response:
        {
            "cumulative_score": 82,
            "ratings": {
                "environmental": 85,
                "data_privacy": 78,
                "supply_chain": 91
            },
            "false_claims": "Zero-waste manufacturing claims from 2024 report",
            "references": [
                "https://sustainabilityaudit.org/2025",
                "https://techethicswatch.com/q1-2025"
            ]
        }
        '''
        }
    ]
    
    claims_response = client.chat.completions.create(
        model="sonar-pro",
        messages=extract_claims_messages,
        
        
    )
    
    extracted_claims = claims_response.choices[0].message.content
    print(extracted_claims)
    
    
    
    return jsonify(extracted_claims)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
