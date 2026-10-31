#!/usr/bin/env bash
# Gera o "Resumo da Esteira" (Markdown) a partir dos relatórios baixados.
#
# Entradas (variáveis de ambiente):
#   RESULT_1..RESULT_8  resultado de cada job (success, failure, cancelled, skipped)
#   REPORTS_DIR         pasta com os artifacts baixados (padrão: reports)
#   MODE                "final" (padrão) ou "parcial" (omite a etapa 8)
#   OUTPUT              arquivo de saída (padrão: resumo-esteira.md)
set -euo pipefail

REPORTS_DIR="${REPORTS_DIR:-reports}"
MODE="${MODE:-final}"
OUTPUT="${OUTPUT:-resumo-esteira.md}"

# Localiza um arquivo de relatório dentro do diretório do artifact.
achar() { find "$REPORTS_DIR" -type f -name "$1" 2>/dev/null | head -n 1 || true; }

# Executa um jq e devolve "0" se o arquivo não existir ou der erro.
contar() {
  local arquivo="$1" filtro="$2"
  if [[ -n "$arquivo" && -s "$arquivo" ]]; then
    jq -r "$filtro" "$arquivo" 2>/dev/null || echo "0"
  else
    echo "0"
  fi
}

# Mostra "-" na coluna de achados quando a etapa não chegou a executar.
col() {
  case "${1:-skipped}" in
    skipped|cancelled|"") echo "-" ;;
    *) echo "$2" ;;
  esac
}

# Resultado do job.
status() {
  case "${1:-skipped}" in
    success) echo "success" ;;
    *) echo "${1:-skipped}" ;;
  esac
}

# --- Etapa 1: Gitleaks
f="$(achar gitleaks.json)"
n1="$(contar "$f" 'length')"

# --- Etapa 2: Semgrep
f="$(achar semgrep.json)"
n2="$(contar "$f" '.results | length')"

# --- Etapa 3: pip-audit (informativo)
f="$(achar pip-audit.json)"
n3="$(contar "$f" '[.dependencies[]? | (.vulns // []) | length] | add // 0')"

# --- Etapa 4: Trivy fs (HIGH/CRITICAL)
f="$(achar trivy-fs.json)"
n4="$(contar "$f" '[.Results[]? | ((.Vulnerabilities // []) + (.Misconfigurations // []) + (.Secrets // [])) | length] | add // 0')"

# --- Etapa 5: digest da imagem
f="$(achar docker-build.md)"
d5="-"
if [[ -n "$f" ]]; then
  d5="$(grep -oE 'sha256:[0-9a-f]{12}' "$f" | head -n 1 || true)"
  d5="${d5:+digest ${d5}…}"
  d5="${d5:--}"
fi

# --- Etapa 6: Trivy image (HIGH/CRITICAL com correção)
f="$(achar trivy-image.json)"
n6="$(contar "$f" '[.Results[]? | ((.Vulnerabilities // []) + (.Misconfigurations // []) + (.Secrets // [])) | length] | add // 0')"

# --- Etapa 7: ZAP (alertas High e Medium; riskcode 3 = High, 2 = Medium)
f="$(achar report_json.json)"
z_high="$(contar "$f" '[.site[]?.alerts[]? | select(.riskcode == "3")] | length')"
z_med="$(contar "$f" '[.site[]?.alerts[]? | select(.riskcode == "2")] | length')"

# --- Etapa 8: aprovador
f="$(achar deploy-producao.md)"
a8="-"
if [[ -n "$f" ]]; then
  a8="$(grep -i 'Aprovado por' "$f" | head -n 1 | sed 's/.*: *//' || true)"
  a8="${a8:+aprovado por ${a8}}"
  a8="${a8:--}"
fi

{
  if [[ "$MODE" == "parcial" ]]; then
    echo "## Resumo parcial da esteira (etapas 1 a 7, antes da aprovação humana)"
  else
    echo "## Resumo da esteira"
  fi
  echo
  echo "| # | Etapa | Resultado | Achados |"
  echo "|---|-------|-----------|---------|"
  echo "| 1 | Secrets (Gitleaks) | $(status "${RESULT_1:-}") | $(col "${RESULT_1:-}" "${n1} segredos") |"
  echo "| 2 | SAST (Semgrep) | $(status "${RESULT_2:-}") | $(col "${RESULT_2:-}" "${n2} achados") |"
  echo "| 3 | Build + dependências | $(status "${RESULT_3:-}") | $(col "${RESULT_3:-}" "${n3} vulns (pip-audit)") |"
  echo "| 4 | SCA (Trivy fs) | $(status "${RESULT_4:-}") | $(col "${RESULT_4:-}" "${n4} HIGH/CRITICAL") |"
  echo "| 5 | Docker build + GHCR | $(status "${RESULT_5:-}") | $(col "${RESULT_5:-}" "${d5}") |"
  echo "| 6 | Scan da imagem (Trivy) | $(status "${RESULT_6:-}") | $(col "${RESULT_6:-}" "${n6} HIGH/CRITICAL") |"
  echo "| 7 | Homologação + ZAP | $(status "${RESULT_7:-}") | $(col "${RESULT_7:-}" "${z_high} alertas High, ${z_med} Medium") |"
  if [[ "$MODE" != "parcial" ]]; then
    echo "| 8 | Aprovação + produção | $(status "${RESULT_8:-}") | $(col "${RESULT_8:-}" "${a8}") |"
  fi
  echo
  echo "Commit: \`${GITHUB_SHA:-local}\` · Execução: ${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-owner/repo}/actions/runs/${GITHUB_RUN_ID:-0}"
} > "$OUTPUT"

cat "$OUTPUT"
