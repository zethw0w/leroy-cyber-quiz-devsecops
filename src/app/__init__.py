"""Leroy Cyber Quiz: aplicação do Grupo LevelUP (FIAP Challenge 2026)."""

import os

from flask import Flask, jsonify, request, send_from_directory

from .data import CENARIOS, NIVEIS_XP, PERFIL, TRILHAS

# CSP restritiva: sem scripts/estilos inline e sem recursos de terceiros.
CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)

SECURITY_HEADERS = {
    "Content-Security-Policy": CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cache-Control": "no-store",
}

PAGES = {
    "/": "index.html",
    "/dashboard": "dashboard.html",
    "/quiz": "quiz.html",
    "/progresso": "progresso.html",
}


def _cenario_publico(cenario_id: str, cenario: dict) -> dict:
    """Representação do cenário sem revelar pesos nem a resposta correta."""
    return {
        "id": cenario_id,
        "titulo": cenario["titulo"],
        "trilha": cenario["trilha"],
        "nivel": cenario["nivel"],
        "xp_maximo": NIVEIS_XP[cenario["nivel"]],
        "progresso": cenario["progresso"],
        "remetente": cenario["remetente"],
        "horario": cenario["horario"],
        "mensagem": cenario["mensagem"],
        "opcoes": {letra: op["texto"] for letra, op in cenario["opcoes"].items()},
    }


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config["MAX_CONTENT_LENGTH"] = 4096
    app.json.sort_keys = False
    versao = os.environ.get("APP_VERSION", "dev")
    pages_dir = os.path.join(app.root_path, "pages")

    @app.after_request
    def aplicar_cabecalhos(resposta):
        for chave, valor in SECURITY_HEADERS.items():
            resposta.headers[chave] = valor
        return resposta

    def _servir(nome_arquivo):
        def view():
            return send_from_directory(pages_dir, nome_arquivo)

        return view

    for rota, arquivo in PAGES.items():
        app.add_url_rule(rota, endpoint=f"pagina_{arquivo}", view_func=_servir(arquivo))

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok", version=versao)

    @app.get("/api/perfil")
    def perfil():
        return jsonify(PERFIL)

    @app.get("/api/trilhas")
    def trilhas():
        return jsonify(TRILHAS)

    @app.get("/api/cenarios")
    def cenarios():
        return jsonify([_cenario_publico(i, c) for i, c in CENARIOS.items()])

    @app.get("/api/cenarios/<string:cenario_id>")
    def cenario(cenario_id):
        item = CENARIOS.get(cenario_id)
        if item is None:
            return jsonify(erro="Cenário não encontrado."), 404
        return jsonify(_cenario_publico(cenario_id, item))

    @app.post("/api/cenarios/<string:cenario_id>/resposta")
    def responder(cenario_id):
        item = CENARIOS.get(cenario_id)
        if item is None:
            return jsonify(erro="Cenário não encontrado."), 404
        corpo = request.get_json(silent=True)
        if not isinstance(corpo, dict):
            return jsonify(erro="Corpo JSON inválido."), 400
        letra = corpo.get("opcao")
        if not isinstance(letra, str) or letra not in item["opcoes"]:
            return jsonify(erro="Opção inválida."), 400
        escolha = item["opcoes"][letra]
        return jsonify(
            opcao=letra,
            correta=escolha["correta"],
            xp=escolha["xp"],
            titulo=escolha["titulo"],
            consequencia=escolha["consequencia"],
        )

    @app.errorhandler(404)
    def nao_encontrado(_erro):
        return jsonify(erro="Recurso não encontrado."), 404

    @app.errorhandler(405)
    def metodo_invalido(_erro):
        return jsonify(erro="Método não permitido."), 405

    @app.errorhandler(413)
    def corpo_grande(_erro):
        return jsonify(erro="Requisição grande demais."), 413

    return app
