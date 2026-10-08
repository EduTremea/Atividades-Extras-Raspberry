# Destinos que o monitor vai testar
# o gateway nao precisa colocar aqui, ele e descoberto sozinho

# outro equipamento da rede local
# colocamos a rasp do professor (final .100 da planilha) -> TROCAR pelo ip certo da sala
DESTINO_LOCAL = "192.168.1.100"

# destinos externos (um por ip e um por nome, assim da pra ver se o DNS ta funcionando)
DESTINOS_EXTERNOS = ["8.8.8.8", "google.com"]

# quantos pings manda pra cada destino
QUANTIDADE_PINGS = 3

# acima disso (em ms) fica amarelo
LIMITE_ATENCAO_MS = 100
