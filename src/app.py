from flask import Flask, render_template
import os

app = Flask(__name__)
BASE_PATH = os.getenv("BASE_PATH", "").rstrip("/")


@app.route(BASE_PATH + "/")
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5000)
