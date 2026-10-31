"use strict";

(async function () {
  const params = new URLSearchParams(window.location.search);
  const cenarioId = params.get("id") || "rh-urgente";
  const titulo = document.getElementById("titulo");

  let cenario;
  try {
    cenario = await buscarJson(`/api/cenarios/${encodeURIComponent(cenarioId)}`);
  } catch (erro) {
    titulo.textContent = "Cenário não encontrado.";
    return;
  }

  document.getElementById("trilha").textContent =
    `${cenario.trilha} · ${cenario.nivel} · ${cenario.progresso}`;
  titulo.textContent = cenario.titulo;
  document.getElementById("remetente").textContent = cenario.remetente;
  document.getElementById("horario").textContent = cenario.horario;
  document.getElementById("mensagem").textContent = cenario.mensagem;

  const lista = document.getElementById("opcoes");
  for (const [letra, texto] of Object.entries(cenario.opcoes)) {
    const botao = criar("button", "opcao");
    botao.type = "button";
    botao.append(criar("span", "letra", letra), criar("span", "", texto));
    botao.addEventListener("click", () => responder(letra));
    lista.append(botao);
  }

  async function responder(letra) {
    for (const b of lista.querySelectorAll("button")) b.disabled = true;
    try {
      const resultado = await buscarJson(
        `/api/cenarios/${encodeURIComponent(cenarioId)}/resposta`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ opcao: letra }),
        }
      );
      document.getElementById("c-rotulo").textContent =
        resultado.correta ? "Consequência · Acerto" : "Atenção · Consequência";
      document.getElementById("c-titulo").textContent = resultado.titulo;
      document.getElementById("c-texto").textContent = resultado.consequencia;
      document.getElementById("c-xp").textContent = `+${resultado.xp} XP`;
      document.getElementById("consequencia").classList.remove("oculto");
    } catch (erro) {
      document.getElementById("c-titulo").textContent = "Não foi possível registrar a resposta.";
      document.getElementById("consequencia").classList.remove("oculto");
    }
  }
})();
