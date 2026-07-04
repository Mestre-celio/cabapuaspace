# 🚀 Deploy no Render

## Pré-requisitos

- [ ] Conta no [Render](https://render.com)
- [ ] Repositório no GitHub com todos os commits
- [ ] Variáveis de ambiente preparadas

## Opção A: Deploy via Blueprint (Recomendado)

### 1. Conecte o GitHub ao Render
1. Acesse [dashboard.render.com](https://dashboard.render.com)
2. Clique em **New +** → **Blueprint**
3. Conecte seu repositório GitHub
4. Selecione o repositório

### 2. Render detecta automaticamente
O Render lê o `render.yaml` da raiz e cria:
- ✅ Backend (Docker)
- ✅ Frontend (Docker)
- ✅ PostgreSQL gerenciado
- ✅ Variáveis de ambiente linkadas

### 3. Configure variáveis obrigatórias
No dashboard, edite as variáveis marcadas como `sync: false`:
- `ALLOWED_ORIGINS`: `https://cabapua-frontend.onrender.com`
- `NEXT_PUBLIC_API_URL`: `https://cabapua-backend.onrender.com`

### 4. Deploy!
Clique em **Apply** e aguarde ~5 minutos.

---

## Opção B: Deploy Manual

### 1. Banco de Dados PostgreSQL
1. **New +** → **PostgreSQL**
2. Nome: `cabapua-db`
3. Região: Oregon
4. Plano: Starter
5. Copie o **Internal Database URL**

### 2. Backend (Web Service)
1. **New +** → **Web Service**
2. Conecte o GitHub → selecione o repo
3. Configuração:
   - **Name**: `cabapua-backend`
   - **Region**: Oregon
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Dockerfile Path**: `Dockerfile.render`
   - **Plan**: Starter
4. **Environment Variables**:
   ```
   DATABASE_URL=<internal-url-do-banco>
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   SECRET_KEY=<gere-um-random>
   ALLOWED_ORIGINS=https://cabapua-frontend.onrender.com
   ```
5. Clique em **Create Web Service**

### 3. Frontend (Web Service)
1. **New +** → **Web Service**
2. Conecte o GitHub → selecione o repo
3. Configuração:
   - **Name**: `cabapua-frontend`
   - **Region**: Oregon
   - **Branch**: `main`
   - **Root Directory**: `cabapua-app`
   - **Runtime**: Docker
   - **Dockerfile Path**: `Dockerfile.render`
   - **Plan**: Starter
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://cabapua-backend.onrender.com
   ```
5. Clique em **Create Web Service**

---

## Pós-Deploy

### 1. Atualize CORS
No dashboard do backend, adicione a URL do frontend em `ALLOWED_ORIGINS`:
```
https://cabapua-frontend.onrender.com
```

### 2. Verifique Health Checks
```bash
curl https://cabapua-backend.onrender.com/health
```

### 3. Execute Migrações (se não rodaram)
Via Render Shell:
1. Backend → **Shell**
2. Execute: `alembic upgrade head`

---

## Custos Estimados

| Serviço | Plano | Custo/mês |
|---------|-------|-----------|
| Backend | Starter | $7 |
| Frontend | Starter | $7 |
| PostgreSQL | Starter | $7 |
| **Total** | | **$21/mês** |

---

## Troubleshooting

### "Application failed to respond"
- Verifique se o backend está ouvindo em `0.0.0.0:$PORT`
- Confira os logs em **Logs** → **Build** e **Runtime**

### "Connection refused" no banco
- Use o **Internal Database URL** (não o externo)
- Aguarde o banco ficar "Available" (~2min)

### CORS no frontend
- Adicione a URL exata do frontend em `ALLOWED_ORIGINS`
- Inclua `https://` e sem barra no final

### Migrações não rodaram
- Verifique se `render-build.sh` tem permissão de execução
- Rode manualmente via Render Shell

---

## Deploy Contínuo

A cada `git push` na branch `main`, o Render:
1. Detecta o commit
2. Faz build automático
3. Roda migrações (se houver)
4. Faz deploy com zero downtime
