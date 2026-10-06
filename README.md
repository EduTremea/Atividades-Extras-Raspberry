# Atividades Extras - Raspberry Pi

Atividades extras da disciplina de Nanocomputadores (Atitus - Ciencia da Computacao).
As tres aplicacoes rodam na Raspberry Pi com Python + Flask e sao acessadas pelo navegador de outro computador da mesma rede.

## Integrantes

- Bruno Benetti
- Patrick M.
- Luiz Eduardo Tremea

## Estrutura do repositorio

```
Atividades-Extras-Raspberry/
├── atividade1-painel-status/   -> Painel Web de Status da Raspberry Pi
├── atividade2-monitor-rede/    -> Monitor de Rede Local
└── atividade3-chat/            -> Servico de Mensagens (chat entre Raspberries)
```

Cada pasta e uma aplicacao separada, com seu proprio `app.py` e `requirements.txt`.

---

## Como rodar (vale pras tres)

Na Raspberry, pelo SSH:

```bash
sudo apt-get update
git clone https://github.com/EduTremea/Atividades-Extras-Raspberry.git
cd Atividades-Extras-Raspberry/<pasta-da-atividade>

python -m venv env
source env/bin/activate
pip install -r requirements.txt

# liberar a porta no firewall
sudo ufw allow 22
sudo ufw allow 5000
sudo ufw enable

python app.py
```

Depois e so abrir `http://IP_DA_RASP:5000` em outro computador da rede.
As tres usam a porta 5000, entao roda uma de cada vez (ou muda a porta).

Para sair do ambiente virtual: `deactivate`.

---

## Atividade 1 - Painel Web de Status

Pagina que mostra o estado atual da Raspberry sem precisar entrar por SSH.

### O que aparece no painel

- Nome do equipamento (hostname) e sistema operacional
- IP na rede local
- Tempo ligada desde o ultimo boot
- Uso da CPU
- Temperatura do processador
- Uso da memoria
- Uso do disco
- Data e hora da ultima atualizacao
- Historico das ultimas 20 leituras

### Arquivos

- `sistema.py` -> le as informacoes reais da Raspberry
- `app.py` -> servidor Flask
- `templates/index.html` e `static/` -> pagina

### De onde vem cada informacao

| Informacao | Como pegamos |
|-----------|--------------|
| Hostname | `socket.gethostname()` |
| IP | socket UDP (sem mandar pacote) ou comando `hostname -I` |
| Uptime | `psutil.boot_time()` |
| CPU | `psutil.cpu_percent()` |
| Temperatura | arquivo `/sys/class/thermal/thermal_zone0/temp` ou comando `vcgencmd measure_temp` |
| Memoria | `psutil.virtual_memory()` |
| Disco | `psutil.disk_usage("/")` |

Cada leitura tem seu proprio `try/except`. Se alguma falhar aparece "indisponivel" e o resto do painel continua funcionando.

### Atualizacao e cores

O JavaScript chama `/api/status` a cada 5 segundos (da pra desligar) ou quando clica no botao.

| Item | Amarelo | Vermelho |
|------|---------|----------|
| CPU | 60% | 85% |
| Temperatura | 60 °C | 75 °C |
| Memoria | 70% | 90% |
| Disco | 75% | 90% |

### Rotas

- `/` -> painel
- `/api/status` -> dados em JSON
- `/api/historico` -> ultimas 20 leituras

---

## Atividade 2 - Monitor de Rede Local

Pagina que mostra a configuracao de rede da Raspberry e testa se ela consegue falar com o roteador, com outro equipamento da rede e com a internet.

**Antes de rodar:** abrir o `config.py` e colocar em `DESTINO_LOCAL` o IP de outro equipamento da sala (usamos a Raspberry do professor, final .100).

### O que aparece

- Nome do equipamento
- Interface usada (`wlan0` = Wi-Fi, `eth0` = cabo) e se esta conectada
- IP, mascara e gateway
- Servidores DNS
- Data e hora da verificacao

### Testes

O monitor faz `ping` em:

1. Gateway (roteador), descoberto sozinho
2. Um equipamento da rede local (`DESTINO_LOCAL`)
3. `8.8.8.8` (internet por IP)
4. `google.com` (internet por nome, testa o DNS junto)

Pra cada um mostra o destino, o status, o tempo de resposta, a media das verificacoes anteriores e o horario do teste.

### Arquivos

- `config.py` -> destinos e limites
- `rede.py` -> pega as informacoes de rede e faz os pings
- `app.py` -> servidor Flask
- `templates/` e `static/` -> pagina

### De onde vem cada informacao

| Informacao | Como pegamos |
|-----------|--------------|
| Gateway e interface | comando `ip route show default` |
| IP e mascara | `psutil.net_if_addrs()` |
| Estado da interface | `psutil.net_if_stats()` |
| Nome do Wi-Fi | comando `iwgetid -r` |
| DNS | arquivo `/etc/resolv.conf` |
| Testes | comando `ping -c 3 -W 2 <destino>` |

### Regra das cores

- **OK (verde)**: respondeu tudo e a media ficou abaixo de 100 ms
- **ATENCAO (amarelo)**: perdeu algum pacote ou passou de 100 ms
- **FALHA (vermelho)**: nao respondeu ou nao conseguiu resolver o nome

Se um destino cair, so ele fica vermelho e o resto continua funcionando.
A aplicacao so testa os destinos configurados, nao faz varredura na rede.

### Rotas

- `/` -> painel
- `/api/verificar` -> faz uma nova verificacao e devolve JSON
- `/api/historico` -> ultimas 30 verificacoes

---

## Atividade 3 - Servico de Mensagens (Chat)

Chat web que roda na Raspberry e troca mensagens com a Raspberry de outro grupo pela rede local, usando HTTP e JSON.

**Grupo parceiro:** (preencher)

### Como funciona

1. Escrevemos a mensagem na pagina e informamos o IP da Raspberry do outro grupo
2. A pagina manda pro nosso back-end (`/api/enviar`)
3. O back-end faz um POST na Raspberry do outro grupo (`/api/mensagens/receber`)
4. A outra Raspberry responde 201 (recebida) ou 400 (rejeitada)
5. A mensagem fica salva como "entregue" ou "falha"

Pra responder, o outro grupo faz o mesmo caminho ao contrario. Na nossa pagina as mensagens recebidas tem um botao "responder" que ja preenche o IP de quem mandou.

### Arquivos

- `config.py` -> nome do grupo, porta e timeout
- `mensagens.py` -> guarda as mensagens enviadas e recebidas (em memoria) e valida o que chega
- `app.py` -> rotas do Flask
- `templates/index.html`, `static/chat.js`, `static/style.css` -> tela do chat

### Rotas

| Metodo | Rota | Quem usa |
|--------|------|----------|
| GET | `/` | navegador |
| POST | `/api/enviar` | nossa pagina |
| GET | `/api/mensagens/enviadas` | nossa pagina |
| GET | `/api/mensagens/recebidas` | nossa pagina |
| POST | `/api/mensagens/receber` | Raspberry dos outros grupos |

### Tratamento de erros

- Mensagem vazia nao e enviada (validado no JS e no Python)
- Se a outra Raspberry estiver desligada ou demorar mais de 5 s, aparece "falha" e o chat continua
- Mensagem recebida sem os campos obrigatorios e rejeitada com 400
- O texto recebido e mostrado com `textContent`, entao ninguem consegue mandar HTML ou script pra rodar na nossa pagina
- Se chegar a mesma mensagem duas vezes (mesmo `id`), a segunda e ignorada

### Rodar com o nome do grupo

```bash
export NOME_GRUPO="Grupo Bruno, Patrick e Luiz"
python app.py
```

Pra testar sozinho da pra abrir dois chats no mesmo computador:

```bash
PORTA=5000 NOME_GRUPO="Teste A" python app.py
PORTA=5001 NOME_GRUPO="Teste B" python app.py   # em outro terminal
```

e mandar de um pro outro usando `127.0.0.1:5001` como destino.

### Contrato de comunicacao

Combinado com o grupo parceiro:

**1. Como localizar o chat do outro grupo:** pelo IP fixo da Raspberry (planilha da turma) na porta `5000`. Ex: `192.168.1.111:5000`

**2. Endereco que recebe as mensagens:**
```
POST http://<ip_da_rasp>:5000/api/mensagens/receber
```

**3. Metodo:** somente `POST`, com `Content-Type: application/json`

**4 e 5. Dados de cada mensagem:**
```json
{
  "id": "6f1c2b9e-3a7d-4c55-9a8e-1d2f3b4c5d6e",
  "remetente": "Grupo Bruno, Patrick e Luiz",
  "ip_remetente": "192.168.1.111:5000",
  "texto": "Oi, tudo certo?",
  "horario": "2026-10-05 19:42:10"
}
```

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | texto (UUID) | sim | identifica a mensagem |
| remetente | texto | sim | nome do grupo que enviou |
| ip_remetente | texto | nao (recomendado) | ip:porta pra poder responder |
| texto | texto | sim | conteudo, maximo 500 caracteres, nao pode ser vazio |
| horario | texto | sim | formato `AAAA-MM-DD HH:MM:SS` |

**6. Resposta do destinatario:**

Recebeu -> `201`
```json
{ "status": "recebida", "id": "<id da mensagem>" }
```

Rejeitou -> `400`
```json
{ "status": "rejeitada", "erro": "motivo" }
```

**7. Identificacao:** cada mensagem tem um `id` unico (UUID v4) gerado por quem envia.

---

## Divisao das tarefas

| Integrante | Responsavel por |
|-----------|-----------------|
| Luiz Eduardo Tremea | Atividade 1 - Painel de Status |
| (preencher) | Atividade 2 - Monitor de Rede |
| (preencher) | Atividade 3 - Chat |
