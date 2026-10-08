# Contrato de comunicacao do chat

Combinado com o grupo parceiro: ________________________ (preencher)

## 1. Como localizar o chat do outro grupo

Pelo IP fixo da Raspberry (planilha da turma) na porta **5000**.
Exemplo: `192.168.1.111:5000`

## 2. Endereco que recebe as mensagens

```
POST http://<ip_da_rasp>:5000/api/mensagens/receber
```

## 3. Metodo

Somente **POST**, com `Content-Type: application/json`.

## 4 e 5. Dados de cada mensagem

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

## 6. Resposta do destinatario

Recebeu certo -> **201**
```json
{ "status": "recebida", "id": "<id da mensagem>" }
```

Rejeitou -> **400**
```json
{ "status": "rejeitada", "erro": "motivo" }
```

## 7. Identificacao

Cada mensagem tem um `id` unico (UUID v4) gerado por quem envia.
Se chegar o mesmo `id` duas vezes, a segunda e ignorada mas responde 201 do mesmo jeito.
