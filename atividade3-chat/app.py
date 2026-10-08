import socket

import requests
from flask import Flask, jsonify, render_template, request

import config
import mensagens

app = Flask(__name__)


def meu_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def montar_url(destino):
    # aceita "192.168.1.120" ou "192.168.1.120:5000"
    destino = destino.strip().replace("http://", "").rstrip("/")
    if ":" not in destino:
        destino = destino + ":5000"
    return "http://" + destino + "/api/mensagens/receber"


@app.route("/")
def pagina_chat():
    return render_template("index.html", nome_grupo=config.NOME_GRUPO)


# ---------- rota que os OUTROS grupos chamam ----------

@app.route("/api/mensagens/receber", methods=["POST"])
def receber():
    dados = request.get_json(silent=True)
    erro = mensagens.validar_recebida(dados)

    if erro:
        return jsonify({"status": "rejeitada", "erro": erro}), 400

    if len(dados["texto"]) > config.TAMANHO_MAXIMO:
        return jsonify({"status": "rejeitada", "erro": "Mensagem muito grande"}), 400

    if not mensagens.ja_recebida(dados["id"]):
        mensagens.salvar_recebida({
            "id": dados["id"],
            "remetente": dados["remetente"],
            "ip_remetente": dados.get("ip_remetente", request.remote_addr),
            "texto": dados["texto"],
            "horario": dados["horario"],
        })

    return jsonify({"status": "recebida", "id": dados["id"]}), 201


# ---------- rotas usadas pela nossa pagina ----------

@app.route("/api/enviar", methods=["POST"])
def enviar():
    dados = request.get_json(silent=True) or {}
    destino = (dados.get("destino") or "").strip()
    texto = (dados.get("texto") or "").strip()

    if destino == "":
        return jsonify({"ok": False, "erro": "Informe o endereco da Raspberry destino"}), 400
    if texto == "":
        return jsonify({"ok": False, "erro": "Nao da pra enviar mensagem vazia"}), 400
    if len(texto) > config.TAMANHO_MAXIMO:
        return jsonify({"ok": False, "erro": "Mensagem muito grande"}), 400

    meu_endereco = f"{meu_ip()}:{config.PORTA}"
    msg = mensagens.nova_mensagem(config.NOME_GRUPO, texto, meu_endereco)

    try:
        resposta = requests.post(montar_url(destino), json=msg, timeout=config.TIMEOUT_ENVIO)

        if resposta.status_code == 201:
            registro = mensagens.salvar_enviada(msg, destino, "entregue")
            return jsonify({"ok": True, "mensagem": registro}), 200

        # a outra rasp respondeu mas recusou
        try:
            motivo = resposta.json().get("erro", "")
        except ValueError:
            motivo = "resposta invalida"
        registro = mensagens.salvar_enviada(msg, destino, "falha", f"Recusada ({resposta.status_code}) {motivo}")

    except requests.exceptions.Timeout:
        registro = mensagens.salvar_enviada(msg, destino, "falha", "A Raspberry destino demorou demais")
    except requests.exceptions.ConnectionError:
        registro = mensagens.salvar_enviada(msg, destino, "falha", "Nao conseguiu conectar no destino")
    except Exception as erro:
        registro = mensagens.salvar_enviada(msg, destino, "falha", str(erro))

    return jsonify({"ok": False, "erro": registro["detalhe"], "mensagem": registro}), 502


@app.route("/api/mensagens/enviadas")
def listar_enviadas():
    return jsonify(mensagens.enviadas)


@app.route("/api/mensagens/recebidas")
def listar_recebidas():
    return jsonify(mensagens.recebidas)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORTA)
