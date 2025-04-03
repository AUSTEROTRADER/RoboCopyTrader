from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({'status': 'erro', 'mensagem': 'Sem dados no corpo da requisição'})

    # Dados recebidos do alerta do TradingView
    tipo = data.get('tipo')
    direcao = data.get('direcao')
    preco = float(data.get('preco', 0))
    ativo = data.get('ativo')
    hora_alerta = data.get('hora')

    # Validação contra gaps no início ou fim de mercado
    agora = datetime.datetime.utcnow()
    hora_atual_utc = agora.strftime('%H:%M')

    if hora_atual_utc < "00:10" or hora_atual_utc > "23:50":
        print("⚠️ Alerta ignorado por possível gap de mercado.")
        return jsonify({'status': 'ignorado', 'motivo': 'gap de mercado'})

    if tipo == "sinal":
        print(f"📥 Alerta recebido!")
        print(f"📌 Ativo: {ativo}")
        print(f"📈 Direção: {direcao.upper()}")
        print(f"💰 Preço: {preco}")
        print(f"⏰ Hora do alerta: {hora_alerta}")

        # Aqui será onde você enviará a ordem real
        # Exemplo: enviar para API da corretora futuramente

        return jsonify({'status': 'sucesso', 'mensagem': f'Ordem de {direcao} processada para {ativo} a {preco}'})
    else:
        return jsonify({'status': 'ignorado', 'mensagem': 'Tipo de mensagem não é sinal'})

@app.route('/')
def home():
    return 'Robo Copy Trader rodando com sucesso!'

if __name__ == '__main__':
    app.run()

