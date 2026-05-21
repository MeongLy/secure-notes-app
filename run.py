# run.py
from app import create_app

app = create_app()

if __name__ == "__main__":
    # SR-09: Untuk production, gunakan HTTPS dan jangan pakai debug=True
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
