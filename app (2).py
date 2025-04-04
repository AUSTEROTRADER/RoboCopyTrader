
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Configurações iniciais
STOP_LOSS = 10     # pips
TAKE_PROFIT = 20   # pips
TRAILING_TRIGGER = 10  # pips
TRAILING_STEP = 5      # pips
BREAK_EVEN_TRIGGER = 15  # pips

# Simulação de estado do trade
trades_abertos = {}

@app.route("/sinal", methods=["POST"])
def receber_sinal():
    data = request.json
    tipo = data.get("tipo")
    direcao = data.get("direcao")
    preco = float(data.get("preco"))
    ativo = data.get("ativo")
    hora = data.get("hora")

    if tipo != "sinal":
        return jsonify({"erro": "Tipo inválido"}), 400

    print(f"[✔️ Alerta Recebido] {ativo} | {direcao} | Preço: {preco} | Hora: {hora}")

    # Abrir trade simulado
    trade_id = f"{ativo}_{hora}"
    trades_abertos[trade_id] = {
        "direcao": direcao,
        "preco_entrada": preco,
        "preco_atual": preco,
        "ativo": ativo,
        "hora": hora,
        "stop_loss": preco - STOP_LOSS / 1000 if direcao == "BUY" else preco + STOP_LOSS / 1000,
        "take_profit": preco + TAKE_PROFIT / 1000 if direcao == "BUY" else preco - TAKE_PROFIT / 1000,
        "modo": "normal",
        "break_even_aplicado": False
    }

    return jsonify({"mensagem": f"Trade simulado aberto em {ativo} às {hora}"}), 200

@app.route("/monitorar", methods=["GET"])
def monitorar_trades():
    # Simula monitoramento e aplicação de trailing/break-even
    atualizacoes = []

    for id, trade in trades_abertos.items():
        preco = trade["preco_atual"]
        entrada = trade["preco_entrada"]
        direcao = trade["direcao"]

        ganho_pips = (preco - entrada) * 1000 if direcao == "BUY" else (entrada - preco) * 1000

        if ganho_pips >= BREAK_EVEN_TRIGGER and not trade["break_even_aplicado"]:
            trade["stop_loss"] = entrada  # break-even
            trade["modo"] = "break-even"
            trade["break_even_aplicado"] = True
            atualizacoes.append(f"{id}: break-even ativado")

        if ganho_pips >= TRAILING_TRIGGER:
            if direcao == "BUY":
                novo_sl = preco - TRAILING_STEP / 1000
                if novo_sl > trade["stop_loss"]:
                    trade["stop_loss"] = novo_sl
                    trade["modo"] = "trailing"
                    atualizacoes.append(f"{id}: trailing SL atualizado")
            else:
                novo_sl = preco + TRAILING_STEP / 1000
                if novo_sl < trade["stop_loss"]:
                    trade["stop_loss"] = novo_sl
                    trade["modo"] = "trailing"
                    atualizacoes.append(f"{id}: trailing SL atualizado")

    return jsonify({"atualizacoes": atualizacoes, "trades": trades_abertos})

@app.route("/", methods=["GET"])
def index():
    return "Robô Copy Trader - Online 🚀"

if __name__ == "__main__":
    app.run(debug=True)
