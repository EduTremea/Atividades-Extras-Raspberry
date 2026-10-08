let abaAtual = "todas";

function aviso(texto, deuCerto) {
    const p = document.getElementById("aviso");
    p.textContent = texto;
    p.className = deuCerto ? "aviso-ok" : "aviso-erro";
}

async function enviar() {
    const destino = document.getElementById("destino").value.trim();
    const texto = document.getElementById("texto").value.trim();

    // valida antes de mandar pro back
    if (destino === "") {
        aviso("Informe o IP da Raspberry destino", false);
        return;
    }
    if (texto === "") {
        aviso("Nao da pra enviar mensagem vazia", false);
        return;
    }

    try {
        const resposta = await fetch("/api/enviar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ destino: destino, texto: texto })
        });
        const dados = await resposta.json();

        if (dados.ok) {
            aviso("Mensagem entregue!", true);
            document.getElementById("texto").value = "";
        } else {
            aviso("Falha no envio: " + dados.erro, false);
        }
    } catch (e) {
        aviso("Erro ao falar com o nosso servidor", false);
    }

    carregar();
}

// cria o balao da mensagem
// usamos textContent em vez de innerHTML pro texto dos outros grupos nao rodar html/script
function criarBalao(m, minha) {
    const div = document.createElement("div");
    div.className = minha ? "msg minha" : "msg";

    const quem = document.createElement("div");
    quem.className = "quem";
    quem.textContent = minha ? "Voce -> " + m.destino : m.remetente + " (" + m.ip_remetente + ")";

    const texto = document.createElement("div");
    texto.textContent = m.texto;

    const info = document.createElement("div");
    info.className = "info";
    info.textContent = m.horario;

    if (minha) {
        const st = document.createElement("span");
        st.textContent = m.status === "entregue" ? "  ✓ entregue" : "  ✗ " + m.detalhe;
        if (m.status !== "entregue") st.className = "falhou";
        info.appendChild(st);
    } else {
        // botao pra responder ja preenchendo o ip de quem mandou
        const btn = document.createElement("button");
        btn.className = "responder";
        btn.textContent = "responder";
        btn.onclick = function () {
            document.getElementById("destino").value = m.ip_remetente;
            document.getElementById("texto").focus();
        };
        info.appendChild(btn);
    }

    div.appendChild(quem);
    div.appendChild(texto);
    div.appendChild(info);
    return div;
}

async function carregar() {
    try {
        const [r1, r2] = await Promise.all([
            fetch("/api/mensagens/enviadas"),
            fetch("/api/mensagens/recebidas")
        ]);
        const enviadas = (await r1.json()).map(m => ({ ...m, minha: true }));
        const recebidas = (await r2.json()).map(m => ({ ...m, minha: false }));

        let lista = [];
        if (abaAtual === "enviadas") lista = enviadas;
        else if (abaAtual === "recebidas") lista = recebidas;
        else lista = enviadas.concat(recebidas);

        // ordena pelo horario (formato AAAA-MM-DD HH:MM:SS ordena certo como texto)
        lista.sort((a, b) => a.horario.localeCompare(b.horario));

        const div = document.getElementById("lista");
        div.innerHTML = "";

        if (lista.length === 0) {
            div.innerHTML = "<p class='vazio'>Nenhuma mensagem ainda</p>";
            return;
        }

        lista.forEach(m => div.appendChild(criarBalao(m, m.minha)));
    } catch (e) {
        console.log("erro ao carregar mensagens", e);
    }
}

document.getElementById("btn-enviar").addEventListener("click", enviar);

// enter envia, shift+enter pula linha
document.getElementById("texto").addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        enviar();
    }
});

document.querySelectorAll(".aba").forEach(botao => {
    botao.addEventListener("click", function () {
        document.querySelectorAll(".aba").forEach(b => b.classList.remove("ativa"));
        this.classList.add("ativa");
        abaAtual = this.dataset.aba;
        carregar();
    });
});

// busca mensagens novas a cada 3 segundos
setInterval(carregar, 3000);
carregar();
