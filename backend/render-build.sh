#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "🔧 Iniciando build do backend..."

pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️  Aplicando migrações do banco..."
sleep 5
alembic upgrade head

echo "✅ Build concluído com sucesso!"
