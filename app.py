from flask import Flask, render_template, request
import google.generativeai as genai
import os
import PyPDF2

# App
app = Flask(__name__)

# Set up the Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDKoljgo_VRsuK9ASVf3A8i5jmcbWNJyMQ"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

model = genai.GenerativeModel("gemini-1.5-flash")

def predict_fake_or_real_email_content(text):
    prompt = f"""
    You are an expert in identifying scam messages in text, emails etc. Analyze the given text and specify in terms like

    - **Real/Legitimate** (Authentic safe message)
    - **Scam/Fake** (Phishing, fraud or suspicious message)

    For the following text:
    {text}

    Return a clear message indicating whether this content is real or a scam.
    If it is a scam, mention why it seems fraudulent.
    If it is real, state that it is legitimate.

    Only return the classification message and nothing else.
    NOTE: Don't return empty or null, you only need to return a message for the input text.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

def url_detection(url):
    prompt = f"""
    You are an advanced AI Model specializing in URL security classification. Analyze the given URL and classify it as following:

    1. Safe URL : Safe, trusted, and non-malicious websites such as google.com, wikipedia.org, amazon.com.
    2. Phishing : Fraudulent websites designed to steal personal information. Indicators include misspelled domains (e.g. Gooogle.com, Linkin.com, Utube.com).
    3. Malware : URL that distribute viruses, ransomware, or malicious software. Often includes automatic downloads or links.
    4. Defacement : Hacked or defaced websites that display unauthorized content, usually altered by attackers.

    Examples of URL and Classification:
    - Safe URL : "https://www.microsoft.com/"
    - Phishing : "https://secure-login.paypa1.com"
    - Malware : "https://free-download-software.xyz/"
    - Defacement : "https://hacked-website.com/"

    Input URL: {url}

    Output format:
    - Return only a string class name
    - Example output for a phishing site: phishing

    Analyze the URL and return the correct classification (only name in lowercase such as safeurl, phishing, malware, defacement).
    Note: Don’t return empty or null, at any cost return the correct class.
    """

    response = model.generate_content(prompt)
    return response.text.strip() if response else 'detection failed'

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scam/", methods=['GET', 'POST'])
def detect_scam():
    if 'file' not in request.files or request.files['file'].filename == '':
        return render_template("index.html", message="No file uploaded")

    file = request.files['file']
    extracted_text = ""

    try:
        if file.filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file)
            extracted_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
        elif file.filename.endswith('.txt'):
            extracted_text = file.read().decode("utf-8")
        else:
            return render_template('index.html', message="Unsupported file type. Please upload .pdf or .txt")
    except Exception as e:
        return render_template("index.html", message=f"Error extracting text: {e}")

    print(extracted_text)  # Debugging purpose

    message = predict_fake_or_real_email_content(extracted_text)

    return render_template("index.html", message=message, extracted_text=extracted_text)


@app.route("/predict", methods=['GET', 'POST'])
def url_predict():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()

        if not url.startswith(('https://', "http://")):
            return render_template("index.html", message='Invalid URL')

        classification = url_detection(url)
        return render_template('index.html', input_url=url, predicted_class=classification)

    # For GET or other methods, just render index page or redirect
    return render_template("index.html")


# Main
if __name__ == '__main__':
    app.run(debug=True)
