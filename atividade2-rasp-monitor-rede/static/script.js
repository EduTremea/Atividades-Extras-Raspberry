let timer = null;

function texto(id, valor) {
    document.getElementById(id).textContent = valor ? valor : "indisponivel";
}

async function verificar() {
    const botao = document.getElementById("btn-verificar");
    botao.disabled = true;
    document.getElementById("carregando").textContent = "testando... (pode levar alguns segundos)";

    try {
        const resposta = await fetch("/api/verificar");
        const dados = await resposta.json();
        const r = dados.rede;

        texto("hostname", r.hostname);
        texto("interface", r.interface);
        texto("tipo", r.tipo ? r.tipo + (r.wifi ? " (" + r.wifi + ")" : "") + " - " + r.estado : null);
        texto("ip", r.ip);
        texto("mascara", r.mascara);
        texto("gateway", r.gateway);
        texto("dns", r.dns.length > 0 ? r.dns.join(", ") : null);
        texto("verificado", r.verificado_em);

        const tbody = document.getElementById("tabela-testes");
        tbody.innerHTML = "";

        dados.testes.forEach(t => {
            const tempo = t.tempo_ms !== null ? t.tempo_ms + " ms" : "-";
            const media = dados.medias[t.destino] !== undefined ? dados.medias[t.destino] + " ms" : "-";

            const linha = document.createElement("tr");
            linha.innerHTML =
                "<td>" + (t.destino || "-") + "</td>" +
                "<td>" + t.descricao + "</td>" +
                "<td><span class='status " + t.status + "'>" + t.status.toUpperCase() + "</span> " + t.mensagem + "</td>" +
                "<td>" + tempo + "</td>" +
                "<td>" + media + "</td>" +
                "<td>" + t.testado_em + "</td>";
            tbody.appendChild(linha);
        });

        document.getElementById("carregando").textContent = "";
    } catch (e) {
        document.getElementById("carregando").textContent = "Erro ao falar com o servidor da Raspberry";
    }

    botao.disabled = false;
}

document.getElementById("btn-verificar").addEventListener("click", verificar);

document.getElementById("auto").addEventListener("change", function () {
    if (this.checked) {
        timer = setInterval(verificar, 30000);
    } else {
        clearInterval(timer);
    }
});

verificar();
