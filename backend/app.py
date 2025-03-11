import os
import fitz  # PyMuPDF for PDF text extraction
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Load API key
API_KEY = "AIzaSyCb-5dOvkmTDgdUsgNAOQZShVLtzoaDGtw"
genai.configure(api_key=API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Store chat history and extracted PDF text
chat_history = []
extracted_text = ""

GREETINGS = ["hello", "hi", "good morning", "good afternoon", "good evening", "hey", "how are you"]

@app.route("/upload", methods=["POST"])
def upload_pdf():
    global extracted_text
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read PDF content
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        extracted_text = ""
        for page in pdf_document:
            extracted_text += page.get_text("text") + "\n"

        if not extracted_text.strip():
            return jsonify({"error": "Failed to extract text from PDF"}), 400

        return jsonify({"message": "PDF uploaded successfully and text extracted."})
    
    except Exception as e:
        print("PDF Processing Error:", str(e))
        return jsonify({"error": "Error processing PDF"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        global extracted_text
        data = request.get_json()

        if not data or "question" not in data:
            return jsonify({"error": "Invalid request. 'question' field is required."}), 400

        user_input = data["question"].strip().lower()
        print(f"Received question: {user_input}")

        # Check if input is a greeting
        if any(greet in user_input for greet in GREETINGS):
             response_text = "Hello! How can I assist you today?"
        else:
            # Append user input to chat history
            chat_history.append({"role": "user", "parts": [user_input]})

            # Combine extracted text with user query and enhance prompt for intelligent interaction
            context = f"Document Info:\n{extracted_text}\n\nUser Query: {user_input}\n\nPlease respond intelligently to the user, considering the document content. Ensure concise and relevant answers if possible give response in five words. Maintain a natural and engaging conversation. If the user asks which brand it is, provide a suitable answer based on the document content."

            # Generate response with document context
            response = model.generate_content(context)
            response_text = response.text

            # Append AI response to chat history
            chat_history.append({"role": "model", "parts": [response_text]})

        return jsonify({"response": response_text})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
