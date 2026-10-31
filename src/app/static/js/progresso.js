"use strict";

(async function () {
  try {
    const perfil = await buscarJson("/api/perfil");

    document.getElementById("nome").textContent = perfil.nome;
    document.getElementById("inicial").textContent = perfil.nome.charAt(0);
    document.getElementById("sub").textContent =
      `${perfil.nivel} · Nível ${perfil.nivel_numero} · Membro desde ${perfil.membro_desde}`;
    document.getElementById("p-xp").textContent = String(perfil.pontos);
    document.getElementById("p-missoes").textContent = String(perfil.missoes);
    document.getElementById("p-trofeus").textContent = String(perfil.trofeus);
    document.getElementById("p-streak").textContent = `${perfil.streak_dias}d`;
    document.getElementById("xp-texto").textContent = `${perfil.pontos} / ${perfil.meta_pontos}`;

    const pct = Math.round((perfil.pontos / perfil.meta_pontos) * 100);
    document.getElementById("xp-barra").style.width = `${pct}%`;

    const prateleira = document.getElementById("trofeus");
    for (const tier of perfil.conquistas) {
      prateleira.append(criar("div", tier ? `trofeu ${tier}` : "trofeu", "★"));
    }
  } catch (erro) {
    document.getElementById("nome").textContent = "Não foi possível carregar seu progresso.";
  }
})();
