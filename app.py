from flask import Flask, render_template
from controllers.predict_controller import predict_bp
from controllers.analyze_controller import analyze_bp
from controllers.chat_controller import chat_bp

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(predict_bp)
app.register_blueprint(analyze_bp)
app.register_blueprint(chat_bp)

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)