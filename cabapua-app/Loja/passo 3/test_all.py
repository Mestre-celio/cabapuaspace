"""
Módulo 4 — Suite de Testes (QA/Validação)
pytest para a rota auth/login + proteção de rotas por role.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Fixtures — aplicação e banco mock
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_db():
    """Banco de dados totalmente mockado — sem PostgreSQL real nos testes."""
    return AsyncMock()


@pytest.fixture
def app(mock_db):
    """
    Cria a aplicação FastAPI substituindo a dependência de banco por mock.
    Importe sua app real aqui; o exemplo usa um factory genérico.
    """
    from main import create_app  # ajuste para o caminho real da sua app
    from core.database import get_db

    application = create_app()
    application.dependency_overrides[get_db] = lambda: mock_db
    return application


# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------

VALID_CREDENTIALS = {
    "username": "terapeuta@selene.com",
    "password": "Senha@Segura123",
}

INVALID_CREDENTIALS = {
    "username": "terapeuta@selene.com",
    "password": "senha_errada",
}

ALUNO_CREDENTIALS = {
    "username": "joao.aluno@cabapua.com",
    "password": "Aluno@Pass456",
}

# Tokens pré-assinados para testes sem chamar o endpoint de login
TERAPEUTA_TOKEN_PAYLOAD = {
    "sub": "1",
    "role": "terapeuta",
    "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
}

ALUNO_TOKEN_PAYLOAD = {
    "sub": "99",
    "role": "aluno",
    "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
}

ADMIN_ROUTE = "/admin/dashboard"
THERAPY_ROUTE = "/therapy-sessions/42"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_token(payload: dict, secret: str = "test_secret") -> str:
    """Gera um JWT real usando a mesma lógica da aplicação."""
    import jwt  # PyJWT
    return jwt.encode(payload, secret, algorithm="HS256")


# ---------------------------------------------------------------------------
# Testes — auth/login
# ---------------------------------------------------------------------------

class TestAuthLogin:

    @pytest.mark.asyncio
    async def test_login_com_credenciais_corretas_retorna_jwt_com_role(self, app, mock_db):
        """
        Cenário 1: Login válido deve retornar access_token contendo a role correta.
        """
        # Mock: banco retorna usuário existente com senha válida
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = VALID_CREDENTIALS["username"]
        mock_user.role = "terapeuta"
        mock_user.hashed_password = "$2b$12$KIX..."  # bcrypt hash mockado

        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("core.auth.verify_password", return_value=True), \
             patch("core.auth.create_access_token", return_value="mocked.jwt.token") as mock_token:

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/auth/login", json=VALID_CREDENTIALS)

        assert response.status_code == 200, f"Esperado 200, recebido {response.status_code}"

        body = response.json()
        assert "access_token" in body, "Resposta deve conter 'access_token'"
        assert body.get("token_type") == "bearer", "token_type deve ser 'bearer'"

        # Verifica que create_access_token foi chamado com a role correta
        call_kwargs = mock_token.call_args[1] if mock_token.call_args[1] else {}
        data_arg = mock_token.call_args[0][0] if mock_token.call_args[0] else call_kwargs.get("data", {})
        assert data_arg.get("role") == "terapeuta", (
            f"Token deve conter role='terapeuta', recebido: {data_arg.get('role')}"
        )

    @pytest.mark.asyncio
    async def test_login_com_credenciais_erradas_retorna_401(self, app, mock_db):
        """
        Cenário 2: Senha incorreta deve retornar HTTP 401 Unauthorized.
        """
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = MagicMock(
            hashed_password="$2b$12$KIX..."
        )
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("core.auth.verify_password", return_value=False):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/auth/login", json=INVALID_CREDENTIALS)

        assert response.status_code == 401, (
            f"Esperado 401 para senha errada, recebido {response.status_code}"
        )
        body = response.json()
        assert "detail" in body
        # Mensagem deve ser genérica — não vazar qual campo está errado
        assert "inválid" in body["detail"].lower() or "incorret" in body["detail"].lower(), (
            "Mensagem de erro deve indicar credenciais inválidas sem revelar qual campo"
        )

    @pytest.mark.asyncio
    async def test_login_usuario_nao_cadastrado_retorna_401(self, app, mock_db):
        """
        Bônus: Usuário não cadastrado também deve retornar 401 (não 404)
        para não revelar se o e-mail existe no sistema.
        """
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = None  # usuário não encontrado
        mock_db.execute = AsyncMock(return_value=mock_result)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/login",
                json={"username": "naoexiste@email.com", "password": "qualquer"},
            )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Testes — controle de acesso por role
# ---------------------------------------------------------------------------

class TestRoleBasedAccess:

    @pytest.mark.asyncio
    async def test_aluno_nao_pode_acessar_rota_admin_retorna_403(self, app, mock_db):
        """
        Cenário 3: Token com role='aluno' acessando rota de admin
        deve retornar HTTP 403 Forbidden.
        """
        token = _make_token(ALUNO_TOKEN_PAYLOAD)
        headers = {"Authorization": f"Bearer {token}"}

        # Mock do get_current_user para retornar aluno
        aluno_user = MagicMock(user_id=99, role="aluno", client_ip="127.0.0.1")

        with patch("core.auth.get_current_user", return_value=aluno_user):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(ADMIN_ROUTE, headers=headers)

        assert response.status_code == 403, (
            f"Aluno não deve acessar rota admin. Esperado 403, recebido {response.status_code}"
        )
        body = response.json()
        assert "detail" in body

    @pytest.mark.asyncio
    async def test_terapeuta_pode_acessar_rota_clinica(self, app, mock_db):
        """
        Bônus: Terapeuta deve ter acesso liberado às rotas de therapy_sessions.
        """
        token = _make_token(TERAPEUTA_TOKEN_PAYLOAD)
        headers = {"Authorization": f"Bearer {token}"}

        # Mock: sessões do paciente 42
        mock_sessions = [
            {
                "id": 1, "patient_id": 42, "therapist_id": 1,
                "session_date": datetime.utcnow().isoformat(),
                "notes": "Sessão inicial", "duration_minutes": 50,
                "created_at": datetime.utcnow().isoformat(),
            }
        ]
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = mock_sessions
        mock_db.execute = AsyncMock(return_value=mock_result)

        terapeuta_user = MagicMock(user_id=1, role="terapeuta", client_ip="127.0.0.1")

        with patch("core.auth.get_current_user", return_value=terapeuta_user), \
             patch("routers.therapy.get_current_user", return_value=terapeuta_user):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(THERAPY_ROUTE, headers=headers)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_token_expirado_retorna_401(self, app):
        """
        Bônus: Token expirado deve retornar 401 antes mesmo de checar a role.
        """
        expired_payload = {
            "sub": "1",
            "role": "terapeuta",
            "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp(),  # no passado
        }
        expired_token = _make_token(expired_payload)
        headers = {"Authorization": f"Bearer {expired_token}"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(THERAPY_ROUTE, headers=headers)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_requisicao_sem_token_retorna_401(self, app):
        """
        Bônus: Requisição sem header Authorization deve retornar 401.
        """
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(THERAPY_ROUTE)

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Testes — checkout (smoke tests para integração)
# ---------------------------------------------------------------------------

class TestCheckoutFlow:

    @pytest.mark.asyncio
    async def test_checkout_estoque_insuficiente_retorna_409(self, app, mock_db):
        """
        Estoque insuficiente deve retornar 409 com error='stock_insufficient'.
        """
        from fastapi import HTTPException as FastHTTP
        mock_db.execute = AsyncMock(
            side_effect=FastHTTP(
                status_code=409,
                detail={"error": "stock_insufficient", "available": 0, "requested": 2},
            )
        )

        payload = {
            "customer_id": 1,
            "items": [{"product_id": 10, "quantity": 2, "size": "M"}],
            "payment_method": "credit_card",
            "card_token": "tok_valid",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/checkout/", json=payload)

        assert response.status_code == 409
        assert response.json()["detail"]["error"] == "stock_insufficient"

    @pytest.mark.asyncio
    async def test_checkout_pagamento_recusado_retorna_402(self, app, mock_db):
        """
        Falha no gateway deve retornar 402 com error='payment_failed'.
        """
        # Produto disponível
        mock_product = {"id": 10, "name": "Uniforme", "price": 89.90, "stock": 5}
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = mock_product
        mock_db.execute = AsyncMock(return_value=mock_result)

        payload = {
            "customer_id": 1,
            "items": [{"product_id": 10, "quantity": 1, "size": "G"}],
            "payment_method": "credit_card",
            "card_token": "FAIL_TOKEN",  # token mágico que simula recusa
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/checkout/", json=payload)

        assert response.status_code == 402
        assert response.json()["detail"]["error"] == "payment_failed"


# ---------------------------------------------------------------------------
# Testes — sistema de presença
# ---------------------------------------------------------------------------

class TestAttendance:

    @pytest.mark.asyncio
    async def test_checkin_plano_vencido_retorna_mensagem_amigavel(self, app, mock_db):
        """
        Plano vencido não deve registrar presença e retorna success=False + mensagem amigável.
        """
        expired_student = {
            "id": 5,
            "name": "Maria",
            "plan_status": "active",
            "last_payment_date": datetime.utcnow() - timedelta(days=45),  # vencido
            "attendance_total": 10,
        }
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = expired_student
        mock_db.execute = AsyncMock(return_value=mock_result)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/attendance/checkin",
                json={"student_id": 5, "class_code": "YOGA-01"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert "Maria" in body["message"]
        assert body["attendance_id"] is None  # presença NÃO foi registrada

    @pytest.mark.asyncio
    async def test_checkin_plano_ativo_registra_presenca(self, app, mock_db):
        """
        Aluno com plano ativo e pagamento em dia deve ter presença registrada.
        """
        active_student = {
            "id": 7,
            "name": "Carlos",
            "plan_status": "active",
            "last_payment_date": datetime.utcnow() - timedelta(days=5),  # em dia
            "attendance_total": 20,
        }

        # Sequência de chamadas ao banco: busca aluno → busca aula → checa dup → insert → update
        mock_db.execute = AsyncMock(side_effect=[
            _mock_row(active_student),
            _mock_row({"id": 3}),        # aula encontrada
            _mock_row(None),              # sem duplicidade
            _mock_scalar(101),            # attendance_id
            _mock_scalar(21),             # novo total
        ])
        mock_db.commit = AsyncMock()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/attendance/checkin",
                json={"student_id": 7, "class_code": "CROSS-02"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["attendance_id"] == 101
        assert body["attendance_total"] == 21


# ---------------------------------------------------------------------------
# Helpers para mocks de SQLAlchemy
# ---------------------------------------------------------------------------

def _mock_row(data: dict | None) -> MagicMock:
    m = MagicMock()
    m.mappings.return_value.first.return_value = data
    return m


def _mock_scalar(value) -> MagicMock:
    m = MagicMock()
    m.scalar_one.return_value = value
    return m
