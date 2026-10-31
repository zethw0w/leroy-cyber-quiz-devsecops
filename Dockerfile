# syntax=docker/dockerfile:1

# ---------- Estágio 1: build das dependências ----------
FROM python:3.13-alpine AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
COPY requirements.txt .
# venv SEM pip: o pip do builder instala os pacotes e nada de pip/ferramentas
# de build (com suas bibliotecas embutidas, ex.: urllib3/msgpack) vai para o runtime.
RUN python -m venv --without-pip /opt/venv \
 && pip --python /opt/venv/bin/python install --no-compile -r requirements.txt

# ---------- Estágio 2: runtime mínimo ----------
FROM python:3.13-alpine AS runtime

# Identificador do commit (não é segredo). Exposto em /healthz.
ARG GIT_SHA=dev

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${GIT_SHA}

# Aplica correções de segurança do SO e remove o pip/ensurepip do Python base
# (reduz a superfície de ataque; as dependências já estão no venv).
RUN apk upgrade --no-cache \
 && rm -rf /usr/local/lib/python3*/site-packages/* \
           /usr/local/lib/python3*/ensurepip \
           /usr/local/bin/pip* \
 && addgroup -g 10001 -S app \
 && adduser -u 10001 -S -G app -H -h /app app

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=10001:10001 src/ /app/

# Usuário não-root
USER 10001:10001

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).status == 200 else 1)"

# --no-control-socket: o gunicorn 26 tenta criar /app/.gunicorn (somente leitura para o usuário não-root); o socket de controle não é usado.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--no-control-socket", "--access-logfile", "-", "wsgi:app"]
