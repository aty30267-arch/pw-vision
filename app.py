from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/courses")
def courses():
    return jsonify([
        {"title": "Complete Mathematics", "teacher": "PW Vision Faculty", "tag": "POPULAR"},
        {"title": "Physics Foundation", "teacher": "PW Vision Faculty", "tag": "NEW"},
        {"title": "Chemistry Masterclass", "teacher": "PW Vision Faculty", "tag": "TRENDING"},
        {"title": "Biology Complete Course", "teacher": "PW Vision Faculty", "tag": "POPULAR"}
    ])

if __name__ == "__main__":
    app.run(debug=True)
