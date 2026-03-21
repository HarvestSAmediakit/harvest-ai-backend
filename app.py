from flask import Flask, request, jsonify
import PyPDF2
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Harvest AI Backend is LIVE! 🚀 Send PDF to /upload"

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400
    
    # Extract text
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() or ''
    except Exception as e:
        return jsonify({'error': f'PDF error: {str(e)}'}), 500
    
    # Call OpenRouter AI (free/cheap models)
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not set on Render'}), 500
    
    prompt = f"""You are a professional AI host for Harvest SA radio platforms.
Turn this article PDF into a deep, radio-ready discussion:
- 4-5 Key Insights (bullets)
- Contrasting opinions / debates
- 3 audience questions
- Ready-to-record narration script (2-3 minutes, engaging South African voice style)

Article text:
{text[:12000]}

Output in clean markdown."""
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=90
        )
        response.raise_for_status()
        ai_text = response.json()['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({'error': f'AI error: {str(e)}'}), 500
    
    return jsonify({
        'status': 'success',
        'discussion': ai_text,
        'text_length': len(text)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))