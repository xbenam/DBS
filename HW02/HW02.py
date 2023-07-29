from flask import Flask


app = Flask(__name__)

@app.route("/v1/health")
def home():
    return "Test for deployment."

if __name__ == "__main__":
    app.run()
