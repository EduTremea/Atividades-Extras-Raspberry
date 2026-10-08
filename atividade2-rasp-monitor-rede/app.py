from flask import Flask, jsonify, render_template

import rede

app = Flask(__name__)

# guarda as ultimas verificacoes pra calcular a media
historico = []
MAX_HISTORICO = 30


def calcular_medias():
    medias = {}
    for verificacao in historico:
        for teste in verificacao["testes"]:
            if teste["tempo_ms"] is not None:
                medias.setdefault(teste["destino"], []).append(teste["tempo_ms"])

    return {destino: round(sum(tempos) / len(tempos), 1) for destino, tempos in medias.items()}


@app.route("/")
def pagina_inicial():
    return render_template("index.html")


@app.route("/api/verificar")
def verificar():
    info = rede.info_rede()
    testes = rede.testar_destinos(info["gateway"])

    historico.append({"horario": info["verificado_em"], "testes": testes})
    if len(historico) > MAX_HISTORICO:
        historico.pop(0)

    return jsonify({"rede": info, "testes": testes, "medias": calcular_medias()})


@app.route("/api/historico")
def ver_historico():
    return jsonify(historico)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
