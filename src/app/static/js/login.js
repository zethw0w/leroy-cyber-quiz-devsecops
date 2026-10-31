"use strict";

// Login de demonstração (mockup): nenhuma credencial é enviada ou armazenada.
document.getElementById("form-login").addEventListener("submit", (evento) => {
  evento.preventDefault();
  window.location.assign("/dashboard");
});
