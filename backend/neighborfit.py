from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load local preprocessed data (already normalized and structured)
data = pd.read_csv("neighborhood_data.csv")

# Scoring function for matching
def compute_score(user_prefs, row):
    weights = {
        'safety': 0.25,
        'cost': 0.2,
        'nightlife': 0.2,
        'transport': 0.2,
        'education_quality': 0.15
    }
    score = 0
    score += weights['safety'] * (5 - abs(user_prefs['safety'] - row['safety']))
    score += weights['cost'] * (5 - abs(user_prefs['cost'] - row['cost_of_living']))
    score += weights['nightlife'] * (5 - abs(user_prefs['nightlife'] - row['nightlife']))
    score += weights['transport'] * (5 - abs(user_prefs['transport'] - row['public_transport']))
    score += weights['education_quality'] * (5 - abs(3 - row['education_quality']))  # targeting neutral education
    return score

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        user_prefs = request.json
        budget = user_prefs.get("budget")

        filtered_data = data.copy()
        if budget:
            filtered_data = filtered_data[filtered_data["average_cost"] <= int(budget)]

        filtered_data['score'] = filtered_data.apply(lambda row: compute_score(user_prefs, row), axis=1)
        top_matches = filtered_data.sort_values(by='score', ascending=False).head(3)

        result = [
            {
                "name": row['name'],
                "score": round(row['score'], 2),
                "tagline": row.get("tagline", "Lifestyle-friendly choice"),
                "image_url": row.get("image_url", "https://via.placeholder.com/300x200")
            }
            for _, row in top_matches.iterrows()
        ]
        return jsonify({"matches": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/", methods=["GET"])
def home():
    return "✅ NeighborFit API is live. Use POST /recommend to get matched cities."

if __name__ == "__main__":
    app.run(debug=True)
