import openai
from flask import Flask, render_template, request
import os

# Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Set a basic system message for the chatbot
system_message = """
You are a Japanese language learning assistant designed to help the user study Japanese for travel. You should guide the user through a structured 12-month learning plan focused on essential vocabulary, grammar, and travel phrases. Encourage speaking, listening, and cultural understanding. Make sure to provide examples of sentences and correct any mistakes when the user asks for help.
"""
# @app.route("/")
# def home():
#     return "Hello, Flask is working!"
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get user input from the form
        user_input = request.form["user_input"]

# Ensure you're using the new interface with 'openai.ChatCompletion.create'
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Make sure to use the correct model (gpt-3.5-turbo or gpt-4)
            messages=[
                {"role": "system", "content": system_message},  # System message
                {"role": "user", "content": user_input}        # User input
            ],
            max_tokens=150
        )
        bot_response = response['choices'][0]['message']['content'].strip()


        return render_template("index.html", user_input=user_input, bot_response=bot_response)

    return render_template("index.html", user_input="", bot_response="")

if __name__ == "__main__":
    app.run(debug=True)
