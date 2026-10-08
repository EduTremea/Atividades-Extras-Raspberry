import os

# nome que aparece como remetente pros outros grupos
NOME_GRUPO = os.environ.get("NOME_GRUPO", "Grupo Bruno, Patrick e Luiz")

PORTA = int(os.environ.get("PORTA", 5000))

# tempo maximo esperando a outra rasp responder (segundos)
TIMEOUT_ENVIO = 5

TAMANHO_MAXIMO = 500
