from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data is None:
        return jsonify({'erro': 'Dados ausentes ou mal formatados'}), 400
    print("⚠️ Alerta recebido:", data)
    return jsonify({'status': 'Alerta recebido com sucesso!'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
