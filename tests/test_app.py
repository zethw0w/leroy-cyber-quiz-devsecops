import pytest

PAGINAS = ["/", "/dashboard", "/quiz", "/progresso"]


def test_healthz_informa_versao(client, monkeypatch):
    resposta = client.get("/healthz")
    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "ok"
    assert "version" in resposta.get_json()


@pytest.mark.parametrize("rota", PAGINAS)
def test_paginas_html_carregam(client, rota):
    resposta = client.get(rota)
    assert resposta.status_code == 200
    assert "text/html" in resposta.content_type


@pytest.mark.parametrize("rota", PAGINAS + ["/healthz", "/api/trilhas"])
def test_cabecalhos_de_seguranca(client, rota):
    h = client.get(rota).headers
    assert "default-src 'self'" in h["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in h["Content-Security-Policy"]
    assert "'unsafe-inline'" not in h["Content-Security-Policy"]
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY"
    assert h["Referrer-Policy"] == "no-referrer"
    assert h["Cache-Control"] == "no-store"


def test_paginas_nao_usam_script_ou_estilo_inline(client):
    for rota in PAGINAS:
        html = client.get(rota).get_data(as_text=True)
        assert "<style" not in html
        assert " style=" not in html
        assert " onclick=" not in html
        # todo <script> deve apontar para arquivo próprio
        for trecho in html.split("<script")[1:]:
            assert trecho.lstrip().startswith("src=")


def test_nenhum_cookie_e_definido(client):
    for rota in PAGINAS:
        assert "Set-Cookie" not in client.get(rota).headers


def test_trilhas_seguem_o_deck(client):
    trilhas = client.get("/api/trilhas").get_json()
    assert [t["nome"] for t in trilhas] == [
        "Phishing", "Senhas Seguras", "Engenharia Social", "LGPD", "E-commerce", "IA & Riscos",
    ]
    assert [t["salas"] for t in trilhas] == [12, 8, 10, 9, 11, 10]


def test_perfil_da_marina(client):
    perfil = client.get("/api/perfil").get_json()
    assert perfil["saudacao"] == "Olá, Marina."
    assert perfil["pontos"] == 1240
    assert perfil["meta_pontos"] == 1500


def test_cenario_nao_vaza_resposta_correta(client):
    cenario = client.get("/api/cenarios/rh-urgente").get_json()
    assert set(cenario["opcoes"]) == {"A", "B", "C", "D"}
    assert "correta" not in str(cenario)
    assert "xp" not in cenario["opcoes"]


def test_cenario_inexistente_retorna_404(client):
    assert client.get("/api/cenarios/nao-existe").status_code == 404


@pytest.mark.parametrize(
    "opcao,xp,correta",
    [("A", 0, False), ("B", 8, False), ("C", 20, True), ("D", 10, False)],
)
def test_pesos_do_cenario_do_rh(client, opcao, xp, correta):
    resposta = client.post("/api/cenarios/rh-urgente/resposta", json={"opcao": opcao})
    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo["xp"] == xp
    assert corpo["correta"] is correta
    assert corpo["consequencia"]


@pytest.mark.parametrize("corpo", [{"opcao": "Z"}, {"opcao": 1}, {}, {"opcao": None}])
def test_resposta_invalida_retorna_400(client, corpo):
    assert client.post("/api/cenarios/rh-urgente/resposta", json=corpo).status_code == 400


def test_corpo_nao_json_retorna_400(client):
    resposta = client.post(
        "/api/cenarios/rh-urgente/resposta", data="isso nao e json", content_type="text/plain"
    )
    assert resposta.status_code == 400


def test_metodo_nao_permitido(client):
    assert client.get("/api/cenarios/rh-urgente/resposta").status_code == 405


def test_corpo_grande_demais_retorna_413(client):
    resposta = client.post("/api/cenarios/rh-urgente/resposta", data="x" * 10000, content_type="application/json")
    assert resposta.status_code == 413


def test_rota_inexistente_retorna_json(client):
    resposta = client.get("/nao-existe")
    assert resposta.status_code == 404
    assert resposta.get_json()["erro"]
