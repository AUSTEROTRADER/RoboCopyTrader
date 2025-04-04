
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pytz
import threading
import time

app = Flask(__name__)

# Banco de dados temporário em memória para armazenar ordens pendentes
ordens_pendentes = []

# Configurações do robô
MODO_CONSERVADOR = True
TIMEZONE = pytz.timezone("America/Sao_Paulo")
PERIODO_CONFIRMACAO_MINUTOS = 10  # equivalente a 2 velas de 5 minutos

# Simula execução da ordem (futura integração com corretora)
def executar_ordem(ativo, direcao, preco, hora_alerta):
    print(f"[EXECUTADO] Ordem {direcao} para {ativo} ao preço {preco} | Alerta: {hora_alerta}")

# Validação do alerta
def alerta_valido(alerta):
    campos_obrigatorios = ["tipo", "direcao", "preco", "ativo", "hora"]
    for campo in campos_obrigatorios:
        if campo not in alerta:
            return False
    return True

# Verificação de confirmação após 2 velas
def verificador_de_confirmacao():
    while True:
        agora = datetime.now(TIMEZONE)
        for ordem in ordens_pendentes[:]:
            tempo_decorrido = (agora - ordem["hora_recebida"]).total_seconds()
            if tempo_decorrido > PERIODO_CONFIRMACAO_MINUTOS * 60:
                print(f"[CANCELADA] Ordem {ordem['direcao']} para {ordem['ativo']} cancelada por falta de confirmação.")
                ordens_pendentes.remove(ordem)
            elif MODO_CONSERVADOR:
                # Aqui pode-se aplicar critérios como volume, vela seguinte etc.
                # Simulação simples: confirma se o tempo é inferior ao limite
                if tempo_decorrido >= 60:  # simulação de "confirmação"
                    executar_ordem(ordem['ativo'], ordem['direcao'], ordem['preco'], ordem['hora_alerta'])
                    ordens_pendentes.remove(ordem)
        time.sleep(10)

@app.route("/", methods=["GET"])
def home():
    return "Robô Copy Trader está ativo!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not alerta_valido(data):
        return jsonify({"erro": "Formato de alerta inválido"}), 400

    try:
        direcao = data["direcao"].upper()
        preco = float(data["preco"])
        ativo = data["ativo"]
        hora_alerta = datetime.fromtimestamp(int(data["hora"]) / 1000, tz=TIMEZONE)
        hora_recebida = datetime.now(TIMEZONE)

        print(f"📩 Alerta recebido!\n→ Ativo: {ativo}\n→ Direção: {direcao}\n→ Preço: {preco}\n→ Hora do alerta: {hora_alerta.strftime('%H:%M')}")

        if MODO_CONSERVADOR:
            ordens_pendentes.append({
                "ativo": ativo,
                "direcao": direcao,
                "preco": preco,
                "hora_alerta": hora_alerta,
                "hora_recebida": hora_recebida
            })
            print(f"[AGUARDANDO CONFIRMAÇÃO] Ordem {direcao} para {ativo} adicionada à fila de espera.")
            return jsonify({"status": "Ordem recebida e aguardando confirmação"}), 200
        else:
            executar_ordem(ativo, direcao, preco, hora_alerta)
            return jsonify({"status": "Ordem executada diretamente (modo não conservador)"}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao processar o alerta: {str(e)}"}), 500

# Inicia o verificador em background
threading.Thread(target=verificador_de_confirmacao, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
