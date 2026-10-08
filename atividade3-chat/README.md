# Chat Local entre Raspberries

Atividade extra 3 de Nanocomputadores (Atitus - CC).
Chat web que roda na Raspberry e troca mensagens com a Raspberry de outro grupo pela rede local, usando HTTP + JSON.

## Integrantes

- Bruno Benetti
- Patrick M.
- Luiz Eduardo Tremea

## Grupo parceiro

- (preencher com o grupo que testamos)

## Como funciona

1. A gente escreve a mensagem na pagina e coloca o IP da rasp do outro grupo
2. A nossa pagina manda pro nosso back-end (`/api/enviar`)
3. O nosso back-end faz um POST na rasp do outro grupo (`/api/mensagens/receber`)
4. A outra rasp responde 201 se recebeu ou 400 se rejeitou
5. A mensagem fica salva como "entregue" ou "falha"

Pra responder, o outro grupo faz o mesmo caminho ao contrario. Na nossa pagina tem um botao "responder" que ja preenche o IP de quem mandou.

O formato das mensagens esta no [CONTRATO.md](CONTRATO.md).

## Arquivos

- `app.py` -> rotas do Flask (enviar, receber, listar)
- `mensagens.py` -> guarda as mensagens enviadas e recebidas (em memoria) e valida o que chega
- `config.py` -> nome do grupo, porta, timeout
- `templates/index.html`, `static/chat.js`, `static/style.css` -> tela do chat

## Rotas

| Metodo | Rota | Quem usa |
|--------|------|----------|
| GET | `/` | navegador (tela do chat) |
| POST | `/api/enviar` | nossa pagina |
| GET | `/api/mensagens/enviadas` | nossa pagina |
| GET | `/api/mensagens/recebidas` | nossa pagina |
| POST | `/api/mensagens/receber` | rasp dos outros grupos |

## Tratamento de erros

- Mensagem vazia nao e enviada (validado no JS e no Python)
- Se a outra rasp estiver desligada ou demorar mais de 5s, aparece "falha" e o chat continua funcionando
- Mensagens recebidas sem os campos obrigatorios sao rejeitadas com 400
- O texto recebido e mostrado com `textContent`, entao ninguem consegue mandar html/script pra rodar na nossa pagina

## Como rodar

```bash
git clone <link do repositorio>
cd rasp-chat-local
python -m venv env
source env/bin/activate
pip install -r requirements.txt

sudo ufw allow 5000
export NOME_GRUPO="Grupo Bruno, Patrick e Luiz"
python app.py
```

Abrir `http://IP_DA_RASP:5000` no navegador.

### Testar sozinho (sem outro grupo)

Da pra abrir dois chats no mesmo computador em portas diferentes:

```bash
PORTA=5000 NOME_GRUPO="Teste A" python app.py
PORTA=5001 NOME_GRUPO="Teste B" python app.py   # em outro terminal
```

E mandar de um pro outro usando `127.0.0.1:5001` como destino.
