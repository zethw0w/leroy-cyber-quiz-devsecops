"use strict";

(async function () {
  try {
    const [perfil, trilhas] = await Promise.all([
      buscarJson("/api/perfil"),
      buscarJson("/api/trilhas"),
    ]);

    document.getElementById("contexto").textContent = perfil.contexto;
    document.getElementById("saudacao").textContent = perfil.saudacao;
    document.getElementById("m-pontos").textContent = String(perfil.pontos);
    document.getElementById("m-trofeus").textContent = `${perfil.trofeus}/${perfil.trofeus_total}`;
    document.getElementById("m-dias").textContent = String(perfil.streak_dias);
    document.getElementById("m-nivel").textContent = `Vig. ${perfil.nivel_numero}`;
    document.getElementById("continue-titulo").textContent = perfil.continue.titulo;

    const retomar = document.getElementById("continue-link");
    retomar.href = `/quiz?id=${encodeURIComponent(perfil.continue.cenario_id)}`;

    const grid = document.getElementById("trilhas");
    for (const trilha of trilhas) {
      const card = criar("article", "trilha");
      card.append(
        criar("div", "numero", `№ ${trilha.numero}`),
        criar("h3", "", trilha.nome),
        criar("p", "", trilha.descricao),
        criar("div", "eyebrow", `${trilha.salas} salas`)
      );
      grid.append(card);
    }
  } catch (erro) {
    document.getElementById("saudacao").textContent = "Não foi possível carregar o painel.";
  }
})();
