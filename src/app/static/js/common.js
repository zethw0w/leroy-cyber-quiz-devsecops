"use strict";

// Utilitários compartilhados. Todo conteúdo dinâmico entra via textContent
// (nunca innerHTML), o que evita XSS e atende a CSP sem scripts inline.

async function buscarJson(url, opcoes) {
  const resposta = await fetch(url, opcoes);
  const dados = await resposta.json();
  if (!resposta.ok) {
    throw new Error(dados.erro || "Falha na requisição.");
  }
  return dados;
}

function criar(tag, classe, texto) {
  const no = document.createElement(tag);
  if (classe) no.className = classe;
  if (texto !== undefined) no.textContent = texto;
  return no;
}
