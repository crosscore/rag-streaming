# s3_db/main.py

from flask import Flask, send_file, request, abort
from flask_cors import CORS
import os
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

app = Flask(__name__, static_folder='/app/data')
CORS(app, resources={r"/data/pdf/*": {"origins": "http://localhost:8000"}})

@app.route('/data/pdf/<path:filename>')
def serve_pdf(filename):
    file_path = os.path.join('/app/data/pdf', filename)
    if not os.path.exists(file_path):
        abort(404)

    page = request.args.get('page', type=int)
    if page is None:
        return send_file(file_path, mimetype='application/pdf')

    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()

        if 0 <= page - 1 < len(reader.pages):
            writer.add_page(reader.pages[page - 1])
        else:
            abort(404)

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return send_file(output, mimetype='application/pdf', as_attachment=False)
    except Exception as e:
        print(f"Error processing PDF: {e}")
        abort(500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
