# Pipeline DevSecOps · explicação de cada etapa

Arquivo: [`.github/workflows/devsecops.yml`](../.github/workflows/devsecops.yml)

## Princípios

- **Shift-left:** o primeiro job olha o histórico do Git, antes de qualquer build.
- **Sequencial:** cada job usa `needs:` do anterior; se uma etapa falha, as seguintes não rodam.
- **Relatório sempre:** todo upload usa `if: always()`, então o relatório existe mesmo quando a etapa falha, que é quando mais importa.
- **Permissões mínimas:** `contents: read` no topo; `packages: write` só na etapa 5; `packages: read` nas etapas 6 e 7; `security-events: write` só no Semgrep (SARIF); `actions: read` só na etapa 8.
- **Versões fixadas:** ferramentas via variáveis `*_VERSION`, dependências Python em `requirements.txt` (`==`), actions por tag de versão. Em ambiente corporativo o ideal é fixar actions pelo SHA do commit (bônus de boas práticas); ver seção "Conferir versões" no final.
- **Branches de teste:** a esteira roda em qualquer branch (etapas 1 a 4), mas as etapas 5 a 8 só rodam na `main` (`if: github.ref == 'refs/heads/main'`). Assim dá para provar os quality gates sem publicar imagem nem tocar em produção.

## Etapa 1 · Gitleaks (job `secrets-scan`)

| Item | Valor |
|------|-------|
| Checkout | `fetch-depth: 0` (histórico completo) |
| Comando | `gitleaks detect --source . --redact --verbose --report-format json --report-path relatorio/gitleaks.json --exit-code 1` |
| Instalação | binário oficial da release, com verificação de checksum SHA-256 |
| Relatório | `relatorio-01-gitleaks` → `gitleaks.json` |
| Gate | Falha se houver qualquer segredo |
| Supressões | `.gitleaksignore`, apenas com justificativa em `docs/observacoes.md` |

`--redact` impede que o relatório reexponha o segredo. Se um segredo real vazar: revogar/rotacionar a credencial, limpar o histórico e registrar o incidente. Apagar só no último commit não resolve.

## Etapa 2 · Semgrep (job `sast`)

| Item | Valor |
|------|-------|
| Rulesets | `p/default`, `p/owasp-top-ten`, `p/python`, `p/flask`, `p/dockerfile` |
| Saídas | `semgrep.json` e `semgrep.sarif` (enviado à aba Security) |
| Gate | `--error`: qualquer achado não tratado bloqueia |
| Tratamento | corrigir, marcar falso positivo ou aceitar risco, sempre com justificativa |
| Supressões | `# nosemgrep: <regra>` somente com justificativa registrada |

## Etapa 3 · Build, dependências e artefato (job `build`)

1. `pip install -r requirements-dev.txt` em venv (versões fixadas).
2. `pipdeptree` → `arvore-dependencias.txt`.
3. `pip-audit` → `pip-audit.json` (informativo; o bloqueio de dependências é a etapa 4).
4. `pytest` (29 testes: rotas, pesos do quiz, validação de entrada e cabeçalhos de segurança). Falha bloqueia.
5. Artefato `leroy-cyber-quiz-<SHA>.tar.gz` publicado como `artefato-aplicacao`.

## Etapa 4 · Trivy fs (job `sca`)

Scanners `vuln,misconfig,secret` na raiz. Três execuções: tabela completa (`trivy-fs.txt`), JSON filtrado HIGH/CRITICAL (`trivy-fs.json`) e o gate (`exit-code: 1`, HIGH/CRITICAL). O relatório é publicado **antes** do gate para existir mesmo com falha. Depende de `requirements.txt` com versões fixas (arquivo de lock).

## Etapa 5 · Docker build + GHCR (job `docker-build`)

- Buildx + login no GHCR com `GITHUB_TOKEN` (`packages: write` apenas aqui).
- Tag **somente** pelo SHA do commit; nome da imagem em minúsculas (`${GITHUB_REPOSITORY,,}`). A tag `latest` não é usada como referência de deploy.
- `build-arg GIT_SHA` grava o commit em `APP_VERSION`; `/healthz` o expõe, permitindo conferir qual commit está em cada ambiente.
- Relatório `docker-build.md`: imagem, digest e manifesto (`imagetools inspect`).
- **Dockerfile seguro:** multi-stage, base Alpine, `apk upgrade`, pip removido do runtime, usuário não-root 10001, sem segredos, `.dockerignore`, `HEALTHCHECK`.

## Etapa 6 · Trivy image (job `image-scan`)

Escaneia `ghcr.io/<repo>:<SHA>` (mesma tag da etapa 5). Credenciais do registry via `TRIVY_USERNAME`/`TRIVY_PASSWORD` (variáveis de ambiente, nunca na linha de comando). Gera tabela completa, JSON HIGH/CRITICAL com correção disponível (`ignore-unfixed`), SBOM CycloneDX (bônus) e o gate com `exit-code: 1`.

## Etapa 7 · Homologação + ZAP (job `dast-staging`)

- Environment `homologacao`.
- Sobe a imagem aprovada no próprio runner, espera `/healthz` e confere que a versão servida é o SHA do commit.
- ZAP **Baseline Scan** contra `http://localhost:8080` (somente o ambiente do grupo). `fail_action: false`: informativo; quem decide é o aprovador.
- Relatórios: `report_html.html`, `report_json.json`, `report_md.md` (+ log da aplicação).
- O job **Resumo parcial** é publicado em seguida para o revisor.

## Etapa 8 · Aprovação e produção (job `deploy-prod`)

- Environment `producao` com **Required reviewers**; o job espera a aprovação, e rejeitar interrompe o deploy.
- Deploy real no Render por *deploy hook* (secret `RENDER_DEPLOY_HOOK_URL` no environment `producao`) apontando para a imagem `ghcr.io/<repo>:<SHA>`.
- Verificação: o job consulta `PROD_URL/healthz` até a produção responder com o mesmo SHA do commit; caso contrário, falha.
- Relatório `deploy-producao.md`: imagem, digest, quem aprovou (via API de approvals), data e link da execução.

## ★ Resumo da Esteira (job `pipeline-summary`)

`needs` de todos os jobs e `if: always()`. Baixa os relatórios, roda [`scripts/resumo.sh`](../scripts/resumo.sh) (que usa `jq`), escreve a tabela em `$GITHUB_STEP_SUMMARY` e publica `resumo-esteira.md` como `resumo-da-esteira`. Etapas puladas aparecem como `skipped` com `-` nos achados.

## Conferir versões (antes da entrega)

O enunciado pede que as versões do anexo sejam conferidas e atualizadas pela equipe. Antes da primeira execução, conferir nas páginas de releases e atualizar se necessário: `aquasecurity/trivy-action` (0.33.1), `zaproxy/action-baseline` (v0.14.0), `github/codeql-action` (v3), `docker/*-action`, `actions/*` e `GITLEAKS_VERSION` no topo do workflow. Para o bônus de supply chain, trocar as tags de action pelo SHA do commit correspondente.
