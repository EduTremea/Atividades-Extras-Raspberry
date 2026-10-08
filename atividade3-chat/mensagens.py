# Guarda as mensagens em memoria (listas)
# quando o app reinicia o historico some, o enunciado pede so durante a execucao

import uuid
from datetime import datetime

enviadas = []
recebidas = []


def horario_atual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def nova_mensagem(remetente, texto, ip_remetente):
    # formato combinado no CONTRATO.md
    return {
        "id": str(uuid.uuid4()),
        "remetente": remetente,
        "ip_remetente": ip_remetente,
        "texto": texto,
        "horario": horario_atual(),
    }


def salvar_enviada(mensagem, destino, status, detalhe=""):
    registro = dict(mensagem)
    registro["destino"] = destino
    registro["status"] = status  # "entregue" ou "falha"
    registro["detalhe"] = detalhe
    enviadas.append(registro)
    return registro


def salvar_recebida(mensagem):
    registro = dict(mensagem)
    registro["recebida_em"] = horario_atual()
    recebidas.append(registro)
    return registro


def ja_recebida(id_mensagem):
    # evita salvar a mesma mensagem duas vezes
    for m in recebidas:
        if m["id"] == id_mensagem:
            return True
    return False


def validar_recebida(dados):
    # devolve uma mensagem de erro ou None se estiver tudo certo
    if not isinstance(dados, dict):
        return "Corpo precisa ser um JSON"

    campos = ["id", "remetente", "texto", "horario"]
    for campo in campos:
        if not dados.get(campo):
            return f"Campo '{campo}' faltando"

    if not isinstance(dados["texto"], str) or dados["texto"].strip() == "":
        return "Texto vazio"

    return None
