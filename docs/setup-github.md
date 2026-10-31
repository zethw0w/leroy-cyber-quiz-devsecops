# Configuração do GitHub (passo a passo)

## 1. Repositório

1. Criar repositório **público** no GitHub e enviar este código (`git init`, `git remote add origin ...`, `git push -u origin main`).
2. Todos os integrantes devem ter commits no histórico (a contribuição individual pode ser verificada).
3. Trocar `OWNER/REPO` no `README.md` pelo caminho real.

## 2. Permissões do workflow

`Settings → Actions → General → Workflow permissions`: manter **Read repository contents** como padrão. As permissões extras (`packages: write` etc.) são declaradas por job no YAML.

## 3. Environments

`Settings → Environments`:

| Environment | Configuração |
|-------------|--------------|
| `homologacao` | Sem revisor. Usado na etapa 7. |
| `producao` | **Required reviewers**: pelo menos 1 integrante. Opcional: *Deployment branches → Selected branches → `main`*. |

No environment `producao`, cadastrar:

- **Secret** `RENDER_DEPLOY_HOOK_URL`: URL do deploy hook do serviço no Render (`https://api.render.com/deploy/srv-XXXX?key=YYYY`). Nunca no código.
- **Variable** `PROD_URL`: URL pública do serviço (ex.: `https://leroy-cyber-quiz.onrender.com`).

## 4. Serviço de produção (Render)

O workflow usa o Render, mas o provedor pode ser trocado (Azure, AWS, GCP, Fly.io): basta substituir os passos "Deploy da imagem pelo SHA" e manter a verificação de `/healthz`.

1. No Render: **New → Web Service → Existing image** e informar `ghcr.io/<owner>/<repo>:<qualquer SHA já publicado>`.
2. Porta: `8080`. Health check path: `/healthz`.
3. Copiar o **Deploy Hook** (Settings do serviço) para o secret acima.
4. O pacote no GHCR nasce privado. Duas opções: tornar o pacote **público** (`Packages → leroy-cyber-quiz → Package settings → Change visibility`) ou cadastrar credenciais do GHCR no Render (*Registry Credentials*, com um PAT `read:packages`).
5. Na primeira vez, o serviço precisa de uma imagem existente: rode a esteira na `main` até a etapa 6 e use o SHA publicado.

## 5. Primeira execução

1. Push na `main`: roda as etapas 1 a 7. Verifique os relatórios em **Artifacts** e o **Resumo parcial** na aba Summary.
2. O job `8 · Aprovação + produção` fica em espera: o revisor abre a execução, consulta os relatórios, clica em **Review deployments**, aprova (ou rejeita) e comenta a base da decisão. Tirar print da tela.
3. Após o deploy, o Resumo da Esteira final aparece na aba Summary. Tirar print.

## 6. Execução bloqueada por quality gate (entregável 3)

Use [`scripts/demo-quality-gates.sh`](../scripts/demo-quality-gates.sh):

```bash
scripts/demo-quality-gates.sh secret   # branch demo/gate-secret: Gitleaks bloqueia
scripts/demo-quality-gates.sh sast     # branch demo/gate-sast: Semgrep bloqueia
scripts/demo-quality-gates.sh deps     # branch demo/gate-deps: Trivy bloqueia por CVE HIGH/CRITICAL
git push -u origin demo/gate-secret    # abre a execução que deve falhar
```

Depois do print do bloqueio, corrija na mesma branch (ou descarte), mostre o `Resumo da Esteira` com o ponto de quebra e registre o antes/depois em `docs/observacoes.md`. **Não faça merge** dessas branches na `main`. Observação: o segredo fictício continua no histórico *da branch de teste*; apague a branch no GitHub depois do print.

## 7. Evidências (`docs/evidencias/`)

| Arquivo sugerido | Conteúdo |
|------------------|----------|
| `01-execucao-completa.png` | Execução completa (8 etapas + resumo) verde |
| `02-gate-bloqueado.png` | Execução bloqueada por um quality gate |
| `03-aprovacao-producao.png` | Tela de aprovação do environment `producao` |
| `04-packages-ghcr.png` | Imagem publicada em **Packages** |
| `05-jogo-producao.png` | Aplicação em produção |
