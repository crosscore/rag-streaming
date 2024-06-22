from flask import Flask, send_file, request, abort
import os

app = Flask(__name__)

@app.route('/pdf/<path:filename>')
def serve_pdf(filename):
    file_path = os.path.join('/data/pdf', filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_file(file_path, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
