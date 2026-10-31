# Principais observações

> **Como usar este arquivo.** A estrutura exigida pelo enunciado está pronta. As linhas marcadas **`PREENCHER`** dependem das execuções reais da esteira no repositório do grupo e **não foram inventadas**: copie cada achado dos relatórios (artifacts), classifique e registre a ação e a evidência. A seção "Controles preventivos" já reflete decisões tomadas no código antes da primeira execução.

Classificações permitidas: **Vulnerabilidade real**, **Falso positivo** (com justificativa) ou **Risco aceito** (com justificativa).

## Controles preventivos aplicados antes da primeira execução

| Controle | Onde | Ferramenta que o valida |
|----------|------|-------------------------|
| Nenhum segredo no repositório; login do mockup não envia nem guarda credenciais | `src/app/static/js/login.js` | Gitleaks, Trivy (secret) |
| DOM atualizado só com `textContent` (sem `innerHTML`, sem `eval`) | `src/app/static/js/*.js` | Semgrep |
| Entrada validada nas rotas de resposta (JSON obrigatório, opção restrita a A–D, corpo ≤ 4 KB) | `src/app/__init__.py` | Semgrep, ZAP, `pytest` |
| Resposta correta do quiz não é exposta pela API de leitura do cenário | `tests/test_app.py` | `pytest` |
| CSP restritiva sem `unsafe-inline`; `frame-ancestors 'none'`; `X-Content-Type-Options`; `X-Frame-Options`; `Referrer-Policy`; `Permissions-Policy`; COOP/COEP/CORP; `Cache-Control: no-store` | `src/app/__init__.py` | ZAP, `pytest` |
| Nenhum cookie emitido (elimina alertas de flags de cookie) | aplicação | ZAP |
| Dependências com versões fixadas; `pip-audit` local sem vulnerabilidades conhecidas | `requirements.txt` | Trivy fs, pip-audit |
| Dockerfile: multi-stage, Alpine, `apk upgrade`, pip removido, usuário não-root, `HEALTHCHECK`, sem segredos | `Dockerfile` | Trivy fs (misconfig), Trivy image |
| Permissões mínimas por job; segredos de produção só no environment `producao` | workflow | Revisão / Semgrep |

## Gitleaks (etapa 1)

| Achado | Onde | Classificação | Ação tomada | Resultado |
|--------|------|---------------|-------------|-----------|
| Execução limpa no histórico | repositório | — | Nenhuma ação necessária | `PREENCHER`: link da execução |
| Segredo fictício de teste (ghp_…) em branch `demo/gate-secret` | `src/demo_secret.py` | Vulnerabilidade real (simulada) | Pipeline bloqueada; em um caso real: revogar/rotacionar, limpar histórico, registrar incidente | `PREENCHER`: print do bloqueio e da execução seguinte |

## Semgrep (etapa 2)

| Achado | Onde | Classificação | Ação tomada | Resultado |
|--------|------|---------------|-------------|-----------|
| `PREENCHER`: regra e severidade | `PREENCHER`: arquivo:linha | `PREENCHER` | `PREENCHER`: commit ou justificativa técnica | `PREENCHER` |
| `eval`/`shell=True` introduzidos em `demo/gate-sast` | `src/app/demo_vuln.py` | Vulnerabilidade real (simulada) | Bloqueio demonstrado e correção | `PREENCHER` |

Toda supressão `nosemgrep` exige linha nesta tabela com a justificativa.

## Build e dependências (etapa 3)

| Achado | Onde | Classificação | Ação tomada | Resultado |
|--------|------|---------------|-------------|-----------|
| `pip-audit`: nenhuma vulnerabilidade conhecida nas dependências fixadas (verificado localmente em 2026-10-30) | `requirements.txt` | — | — | `PREENCHER`: confirmar no relatório `pip-audit.json` da primeira execução |

## Trivy fs (etapa 4)

| Achado | Onde | Classificação | Ação tomada | Resultado |
|--------|------|---------------|-------------|-----------|
| `PREENCHER`: CVE/ID e severidade | `PREENCHER` | `PREENCHER` | `PREENCHER` | `PREENCHER` |
| `requests==2.19.1` (HIGH) em `demo/gate-deps` | `requirements.txt` | Vulnerabilidade real (simulada) | Bloqueio demonstrado; removido | `PREENCHER` |

Toda CVE em `.trivyignore` exige justificativa aqui (ex.: código vulnerável não alcançável).

## Docker build (etapa 5)

| Observação | Evidência |
|------------|-----------|
| Imagem publicada com tag = SHA e digest registrado | `PREENCHER`: print de Packages e link do `docker-build.md` |

## Trivy image (etapa 6)

Comparação com a etapa 4 (aplicação × imagem base) e antes/depois da troca de base:

| Cenário | Imagem base | HIGH | CRITICAL | Observação |
|---------|-------------|------|----------|------------|
| Antes | `PREENCHER`: base testada primeiro | `PREENCHER` | `PREENCHER` | |
| Depois | `python:3.13-alpine` + `apk upgrade` + pip removido | `PREENCHER` | `PREENCHER` | |

## OWASP ZAP (etapa 7)

Alertas que o baseline costuma levantar em aplicações Flask e como a aplicação já se antecipa (confirmar contra o relatório real):

| Alerta | Esperado | Tratamento |
|--------|----------|-----------|
| Content Security Policy (CSP) Header Not Set / Failure to Define Directive | Tratado | CSP completa com `form-action`, `frame-ancestors`, `base-uri` |
| Missing Anti-clickjacking Header | Tratado | `X-Frame-Options: DENY` e `frame-ancestors 'none'` |
| X-Content-Type-Options Header Missing | Tratado | `nosniff` |
| Spectre / isolamento entre origens | Tratado | COOP, COEP, CORP |
| Absence of Anti-CSRF Tokens | Possível em `<form>` de login | Avaliar: o login do mockup não envia dados nem tem sessão → candidato a **falso positivo** (justificar) |
| Server Leaks Version (`Server: gunicorn`) | Possível | Avaliar/aceitar risco ou remover o cabeçalho no proxy |

Registrar abaixo o que o relatório real mostrou:

| Achado | Onde (URL) | Classificação | Ação tomada | Resultado |
|--------|-----------|---------------|-------------|-----------|
| `PREENCHER` | `PREENCHER` | `PREENCHER` | `PREENCHER` | `PREENCHER` |

## Aprovação e produção (etapa 8)

Ver o registro no [README](../README.md#registro-da-aprovação-humana-produção) e o relatório `deploy-producao.md`.

## Lições aprendidas (mínimo de 5 observações da equipe)

> Escrever com base na experiência real da execução. Perguntas-guia: o que mais gerou achados? Quais ferramentas deram mais falsos positivos? Quanto tempo a esteira leva (total e por etapa)? O que mudaria no processo? O que o quality gate bloqueou que passaria despercebido? Qual foi a maior dificuldade (versões de actions, permissões do GHCR, deploy)?

1. `PREENCHER`
2. `PREENCHER`
3. `PREENCHER`
4. `PREENCHER`
5. `PREENCHER`
