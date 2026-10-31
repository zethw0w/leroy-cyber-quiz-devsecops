# Principais observações

> Registro das execuções reais da esteira (#1 a #8 e a execução bloqueada #11). Os valores vêm dos relatórios e do Resumo da Esteira. Os gates de segredos (Gitleaks) e de SAST (Semgrep) foram exercitados só com repositório limpo; o bloqueio foi demonstrado com o gate de dependências (Trivy). Os controles preventivos abaixo já foram aplicados no código antes da primeira execução.

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
| Execução limpa no histórico (0 segredos) | repositório | — | Nenhuma ação necessária | Execuções #1, #2 e #3: https://github.com/zethw0w/leroy-cyber-quiz-devsecops/actions/runs/41157850203 |

## Semgrep (etapa 2)

| Achado | Onde | Classificação | Ação tomada | Resultado |
|--------|------|---------------|-------------|-----------|
| Nenhum achado (0) com `p/default`, `p/owasp-top-ten`, `p/python`, `p/flask` e `p/dockerfile` | `src/`, `Dockerfile`, `.github/` | — | Nenhuma ação necessária (código escrito já seguindo os controles preventivos) | Execução #3, etapa 2: 0 achados |

Toda supressão `nosemgrep` exige linha nesta tabela com a justificativa.

## Build e dependências (etapa 3)

| Achado | Onde | Classificação | Ação tomada | Resultado |
|--------|------|---------------|-------------|-----------|
| `pip-audit`: nenhuma vulnerabilidade conhecida nas dependências fixadas | `requirements.txt` | — | — | Execução #3: 0 vulns no `pip-audit.json`; 29 testes passando |

## Trivy fs (etapa 4)

| Achado | Onde | Classificação | Ação tomada | Resultado |
|--------|------|---------------|-------------|-----------|
| Nenhum HIGH/CRITICAL (0) em dependências, Dockerfile (misconfig) e secrets | raiz do repositório | — | Nenhuma ação necessária | Execução #2 e #3, etapa 4: 0 HIGH/CRITICAL |
| `requests==2.19.1` adicionada de propósito em `demo/gate-deps` (commit `cfc7fd1`) | `requirements.txt` | Vulnerabilidade real (simulada) | **Quality gate bloqueou** a etapa 4 (Trivy fs: 1 HIGH/CRITICAL); as etapas 5 a 8 ficaram *skipped*, então nenhuma imagem foi publicada nem houve deploy. O pip-audit da etapa 3 listou 37 vulnerabilidades, mas não bloqueia: o gate fica no Trivy. A branch não foi mesclada na `main` | [Execução #11](https://github.com/zethw0w/leroy-cyber-quiz-devsecops/actions/runs/41206630012) e print `docs/evidencias/02-gate-bloqueado.png` |

Toda CVE em `.trivyignore` exige justificativa aqui (ex.: código vulnerável não alcançável).

## Docker build (etapa 5)

| Observação | Evidência |
|------------|-----------|
| Imagem publicada com tag = SHA do commit e digest registrado (`sha256:73e7b3e13834…` na execução #3) | `ghcr.io/zethw0w/leroy-cyber-quiz-devsecops:d510dd8f07570a9d6601afaa5c7f85f68989893e`; relatório `relatorio-05-docker-build`; print de Packages em `docs/evidencias/` |

## Trivy image (etapa 6)

Comparação com a etapa 4 (aplicação × imagem base) e antes/depois da troca de base:

Resultado real da etapa 6 na execução #2 (o quality gate **bloqueou** a esteira):

| Cenário | Imagem | HIGH | CRITICAL | Observação |
|---------|--------|------|----------|------------|
| Antes (execução #2) | `python:3.13-alpine` com o pip do venv e do Python base | 5 | 0 | SO Alpine 3.24.3: 0. Os 5 achados estavam em pacotes Python do pip: `urllib3` 2.7.0 (CVE-2026-97687, CVE-2026-97689; correção 2.8.0), `msgpack` 1.1.2 (CVE-2026-114613 e GHSA-6v7p-g79w-8964; correção 1.2.3/1.2.1) e `setuptools` 70.3.0 (CVE-2025-47273; correção 78.1.1) |
| Depois (execução #3, commit `d510dd8`) | mesma base, **sem pip**: venv criado com `--without-pip`, `site-packages`, `ensurepip` e `pip` removidos do Python base | 0 | 0 | Etapa 6 verde |

Diferença entre as etapas 4 e 6: a etapa 4 (`trivy fs`) analisou `requirements.txt`/Dockerfile e deu 0; as 5 vulnerabilidades só apareceram na etapa 6 porque estavam na ferramenta de empacotamento da imagem, e não nas dependências da aplicação. Corrigidas retirando o pip da imagem final, sem alterar o código.

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

Resultado real (execução #8, ZAP Baseline contra a imagem em homologação): **0 alertas High e 0 Medium**.

| Achado | Onde (URL) | Classificação | Ação tomada | Resultado |
|--------|-----------|---------------|-------------|-----------|
| Alertas Low/Informational | A consultar no `report_md.md` do artifact `relatorio-07-homologacao-zap` (execução #8) | A classificar pela equipe | Nenhuma (a execução #8 não teve alerta High nem Medium) | Execução #8, etapa 7: 0 High, 0 Medium |

## Aprovação e produção (etapa 8)

Ver o registro no [README](../README.md#registro-da-aprovação-humana-produção) e o relatório `deploy-producao.md`.

## Lições aprendidas (mínimo de 5 observações da equipe)

> Rascunho baseado nos fatos das execuções #1 a #3. A equipe deve revisar, ajustar e acrescentar o que viveu (por exemplo, dificuldades com o deploy em produção).

1. **A etapa que mais gerou achados foi o scan da imagem (etapa 6):** 5 HIGH, todos no pip embutido na imagem base, enquanto as etapas 1 a 4 não encontraram nada. Só o scan da imagem enxerga o que a aplicação carrega "de carona".
2. **Pinar versões protege, mas é preciso conferi-las:** a primeira execução falhou na etapa 4 porque a versão de `trivy-action` usada não existia mais. O projeto Trivy sofreu um ataque à cadeia de suprimentos e migrou todas as tags para o prefixo `v`. Passamos a usar `v0.36.0` fixada pelo SHA completo do commit (`ed142fd…`).
3. **Falsos positivos:** nenhum até agora; as ferramentas de SAST, secrets e SCA retornaram 0 achados, o que reflete os controles preventivos aplicados desde o código.
4. **Tempo da esteira:** a execução #3 levou 4 min 23 s até a falha esperada da etapa 8 (sem secret de produção). Por etapa: Gitleaks 7 s, Semgrep 30 s, Build 28 s, Trivy fs 26 s, Docker 30 s, Trivy image 43 s, ZAP 1 min 5 s.
5. **Os relatórios publicados com `if: always()` e o resumo que roda sempre** foram essenciais para diagnosticar as falhas: o Resumo da Esteira mostrou na hora que a quebra estava na etapa 8 e que as etapas 1 a 7 estavam verdes.
6. **Melhoria futura:** migrar actions para Node 24 (avisos de depreciação do Node 20), assinar a imagem com Cosign e usar OIDC no deploy.
