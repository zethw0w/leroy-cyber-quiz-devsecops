# Leroy Cyber Quiz · Esteira DevSecOps

[![DevSecOps Pipeline](https://github.com/zethw0w/leroy-cyber-quiz-devsecops/actions/workflows/devsecops.yml/badge.svg)](https://github.com/zethw0w/leroy-cyber-quiz-devsecops/actions/workflows/devsecops.yml)

Plataforma educacional de cibersegurança do **Grupo LevelUP** (FIAP Challenge 2026) para os colaboradores da Leroy Merlin Brasil: cenários reais, decisão entre quatro caminhos e consequência narrada, sem ranking e sem pódio. Este repositório leva a aplicação até produção por uma esteira DevSecOps de 8 etapas no GitHub Actions (CP 03 · DevSecOps).

## Integrantes

| Nome | RM |
|------|----|
| Eric Kinoshita | RM559216 |
| João Jucá | RM559003 |

Turma 2TDCPG · Defesa Cibernética · DevSecOps.

## A aplicação

Mockup funcional do Leroy Cyber Quiz, com quatro telas apresentadas no deck do Challenge: **Login**, **Painel pessoal** (Marina Costa, 1240 pontos, 6 trilhas), **Quiz narrativo** ("O pedido urgente do RH", mais dois cenários) e **Meu progresso** (XP, troféus e streak).

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.13 · Flask 3.1 · Gunicorn |
| Frontend | HTML/CSS/JS estáticos servidos pelo Flask (sem inline script/style) |
| Segurança por design | CSP restritiva, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, COOP/COEP/CORP, `Cache-Control: no-store`, sem cookies, DOM atualizado só com `textContent` |

**Adaptação de stack (etapa 3).** O deck descreve Flask + MongoDB + React/TypeScript como visão do produto completo. Para a esteira, o repositório contém o backend Flask e um frontend estático em memória, sem banco externo, mantendo o ambiente reproduzível e a superfície de teste do ZAP enxuta. Como a stack é Python, os comandos Node do anexo de referência foram trocados por: `pip install -r requirements.txt` (versões fixadas), `pipdeptree` (árvore de dependências), `pip-audit` (auditoria nativa) e `pytest` (testes).

### Executar localmente

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest                              # 29 testes
cd src && gunicorn --bind 127.0.0.1:8080 wsgi:app
# http://localhost:8080
```

### Executar via Docker

```bash
docker compose up --build        # http://localhost:8080
# ou
docker build --build-arg GIT_SHA=local -t leroy-cyber-quiz:local .
docker run --rm -p 8080:8080 leroy-cyber-quiz:local
```

A imagem é multi-stage, baseada em `python:3.13-alpine`, roda com usuário não-root (UID 10001), sem segredos em `ENV`/`ARG`, com `HEALTHCHECK` e pip removido do runtime. O endpoint `/healthz` devolve o SHA do commit em execução.

## A esteira

```text
push (qualquer branch)                          somente na main
        │                                              │
        ▼                                              ▼
[1 Gitleaks] → [2 Semgrep] → [3 Build/Deps/Artefato] → [4 Trivy fs]
                                                          │
        ┌─────────────────────────────────────────────────┘
        ▼
[5 Docker → GHCR] → [6 Trivy image] → [7 Homologação + ZAP]
                                              │
                                              ├──► [Resumo parcial]
                                              ⏸ aprovação humana (environment producao)
                                              ▼
                                      [8 Deploy produção]
                                              │
                                              ▼
                                  [★ Resumo da Esteira (always)]
```

| # | Etapa | Ferramenta | Objetivo | Quality gate | Relatório (artifact) |
|---|-------|-----------|----------|--------------|----------------------|
| 1 | Secrets | Gitleaks | Nenhuma credencial no código ou no histórico completo | Bloqueia | `relatorio-01-gitleaks` |
| 2 | SAST | Semgrep | Falhas no código-fonte (OWASP Top 10, Python/Flask, Dockerfile) | Bloqueia | `relatorio-02-semgrep` |
| 3 | Build, dependências e artefato | pip · pipdeptree · pip-audit · pytest | Build reprodutível, inventário de dependências, testes e artefato com o SHA | Bloqueia (build/testes) | `relatorio-03-build` |
| 4 | SCA | Trivy (fs) | CVEs em bibliotecas e misconfig de Dockerfile/IaC | Bloqueia HIGH/CRITICAL | `relatorio-04-trivy-sca` |
| 5 | Docker build + push | Buildx + GHCR | Imagem imutável, tag = SHA do commit | Bloqueia (falha de build) | `relatorio-05-docker-build` |
| 6 | Scan da imagem | Trivy (image) | SO base e bibliotecas da imagem publicada | Bloqueia HIGH/CRITICAL com correção | `relatorio-06-trivy-image` |
| 7 | Homologação + DAST | OWASP ZAP Baseline | Testes "de fora para dentro" em runtime | Informativo | `relatorio-07-homologacao-zap` |
| 8 | Aprovação + produção | GitHub Environments | Controle de mudança com revisor obrigatório | Aprovação manual | `relatorio-08-producao` |
| ★ | Resumo da Esteira | jq + Job Summary | Consolida status e achados; roda sempre | Sempre executa | `resumo-da-esteira` |

Os relatórios da execução mais recente ficam na página de [Actions](https://github.com/zethw0w/leroy-cyber-quiz-devsecops/actions/workflows/devsecops.yml), seção **Artifacts** de cada execução. Detalhes técnicos de cada etapa em [`docs/pipeline.md`](docs/pipeline.md).

**Decisão sobre o Resumo.** O Resumo final depende da etapa 8 e só existe após a aprovação. Para que o revisor tenha a visão consolidada *antes* de decidir, a esteira também gera o job **Resumo parcial** (etapas 1 a 7), publicado na aba Summary e como artifact `resumo-parcial`.

### Vulnerabilidades da aplicação × vulnerabilidades da imagem

O Trivy aparece duas vezes por motivos diferentes. A etapa 4 (`trivy fs`) analisa o que o grupo escreve e declara: `requirements.txt` e o `Dockerfile` (misconfig). A etapa 6 (`trivy image`) analisa o que foi realmente empacotado: o sistema operacional da imagem base (Alpine/musl/busybox/openssl) e tudo o que ela traz. Um CVE de `Werkzeug` é corrigido atualizando a dependência da aplicação; um CVE de `openssl` é corrigido trocando ou atualizando a imagem base (`apk upgrade`, tag mais nova). Os números reais da comparação, com antes/depois da troca de base, estão em [`docs/observacoes.md`](docs/observacoes.md).

## Registro da aprovação humana (produção)

> Preencher após a primeira execução completa. Print da tela de aprovação em `docs/evidencias/`.

| Campo | Valor |
|-------|-------|
| Aprovador | _nome do integrante revisor_ |
| Data/hora | _AAAA-MM-DD hh:mm_ |
| Execução | _link da execução no Actions_ |
| Commit / imagem | _SHA e digest_ |
| Base da decisão | _relatórios das etapas 1 a 7 consultados e o que foi observado em cada um_ |

## Produção

URL do ambiente de produção: **_preencher (ex.: https://leroy-cyber-quiz.onrender.com)_**

## Resumo da Esteira (execução completa)

> Inserir aqui o print da aba **Summary** de uma execução 100% verde: `docs/evidencias/01-execucao-completa.png`.

## Documentação

- [`docs/pipeline.md`](docs/pipeline.md): explicação de cada etapa (comandos, gates, relatórios).
- [`docs/observacoes.md`](docs/observacoes.md): achados, classificação, correções, falsos positivos e lições aprendidas.
- [`docs/setup-github.md`](docs/setup-github.md): configuração do repositório, environments, secrets e deploy.
- [`docs/evidencias/`](docs/evidencias/): prints exigidos pela atividade.
- [`scripts/demo-quality-gates.sh`](scripts/demo-quality-gates.sh): cria branches de teste que quebram propositalmente cada gate.
