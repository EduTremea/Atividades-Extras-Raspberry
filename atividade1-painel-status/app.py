from flask import Flask, jsonify, render_template

import sistema

app = Flask(__name__)

# historico simples em memoria (some quando reinicia o app)
historico = []
MAX_HISTORICO = 20


@app.route("/")
def pagina_inicial():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    dados = sistema.coletar_status()

    # guarda so o que interessa pro historico
    historico.append({
        "horario": dados["atualizado_em"],
        "cpu": dados["cpu"],
        "temperatura": dados["temperatura"],
        "memoria": dados["memoria"]["percentual"] if dados["memoria"] else None,
    })
    if len(historico) > MAX_HISTORICO:
        historico.pop(0)

    return jsonify(dados)


@app.route("/api/historico")
def api_historico():
    return jsonify(historico)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
