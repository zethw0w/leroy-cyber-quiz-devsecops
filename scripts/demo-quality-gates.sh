#!/usr/bin/env bash
# Cria uma branch de teste que quebra propositalmente um quality gate.
# Uso: scripts/demo-quality-gates.sh {secret|sast|deps}
#
# Depois: git push -u origin <branch> e tire o print da execução bloqueada.
# NÃO faça merge na main. Apague a branch depois (o segredo fictício fica no
# histórico da branch de teste).
set -euo pipefail

modo="${1:-}"
base="$(git rev-parse --abbrev-ref HEAD)"

case "$modo" in
  secret)
    branch="demo/gate-secret"
    git checkout -b "$branch"
    # Token FICTÍCIO no formato de PAT do GitHub, gerado na hora (não é uma credencial real).
    token="ghp_$(head -c 400 /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 36)"
    printf 'GITHUB_TOKEN = "%s"\n' "$token" > src/demo_secret.py
    git add src/demo_secret.py
    git commit -m "test: segredo fictício para demonstrar o gate do Gitleaks"
    ;;
  sast)
    branch="demo/gate-sast"
    git checkout -b "$branch"
    cat > src/app/demo_vuln.py <<'EOF'
import subprocess


def executar(comando):
    # Propositalmente inseguro: injeção de comando e eval (demonstração do gate do Semgrep).
    subprocess.run(comando, shell=True)
    return eval(comando)
EOF
    git add src/app/demo_vuln.py
    git commit -m "test: código inseguro para demonstrar o gate do Semgrep"
    ;;
  deps)
    branch="demo/gate-deps"
    git checkout -b "$branch"
    # Dependência antiga com CVEs HIGH conhecidas (demonstração do gate do Trivy).
    printf 'requests==2.19.1\n' >> requirements.txt
    git add requirements.txt
    git commit -m "test: dependência vulnerável para demonstrar o gate do Trivy"
    ;;
  *)
    echo "Uso: $0 {secret|sast|deps}" >&2
    exit 1
    ;;
esac

echo
echo "Branch '$branch' criada a partir de '$base'."
echo "Próximo passo: git push -u origin $branch"
echo "Para voltar:   git checkout $base"
