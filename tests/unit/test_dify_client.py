"""Testes unitários do DifyClient (lógica determinística, sem rede).

Testa apenas a classificação de erros transitórios (_erro_transitorio), que decide
se uma falha HTTP deve ser reintentada. Não há chamadas ao SUT.
"""
from unittest.mock import Mock

from dify_client import DifyClient


class TestErroTransitorio:
    """A função _erro_transitorio decide se um erro HTTP deve ser reintentado."""

    @staticmethod
    def _resp(status_code, text=""):
        r = Mock()
        r.status_code = status_code
        r.text = text
        return r

    def test_429_e_transitorio(self):
        assert DifyClient._erro_transitorio(self._resp(429))

    def test_502_e_transitorio(self):
        assert DifyClient._erro_transitorio(self._resp(502))

    def test_503_e_transitorio(self):
        assert DifyClient._erro_transitorio(self._resp(503))

    def test_504_e_transitorio(self):
        assert DifyClient._erro_transitorio(self._resp(504))

    def test_200_nao_e_transitorio(self):
        assert not DifyClient._erro_transitorio(self._resp(200, '{"answer":"ok"}'))

    def test_401_nao_e_transitorio(self):
        """401 = chave inválida: falha funcional, não transitória."""
        assert not DifyClient._erro_transitorio(self._resp(401, "Unauthorized"))

    def test_400_com_quota_e_transitorio(self):
        """O Dify repassa erros de cota do Gemini como HTTP 400 com texto específico."""
        texto = '{"error": "RESOURCE_EXHAUSTED: quota exceeded"}'
        assert DifyClient._erro_transitorio(self._resp(400, texto))

    def test_400_com_rate_limit_e_transitorio(self):
        assert DifyClient._erro_transitorio(self._resp(400, "rate limit exceeded"))

    def test_400_sem_marca_transitoria_nao_e_transitorio(self):
        """400 sem marca de erro transitório é falha funcional do SUT."""
        assert not DifyClient._erro_transitorio(self._resp(400, "invalid query"))

    def test_500_com_network_unreachable_e_transitorio(self):
        assert DifyClient._erro_transitorio(self._resp(500, "Network is unreachable"))

    def test_500_com_overloaded_e_transitorio(self):
        """500 sem marca no texto NÃO é transitório; com marca ('overloaded'), é."""
        assert DifyClient._erro_transitorio(self._resp(500, "service overloaded"))

    def test_500_sem_marca_nao_e_transitorio(self):
        """500 'internal error' sem marca de erro de infra: falha funcional do SUT."""
        assert not DifyClient._erro_transitorio(self._resp(500, "internal error"))

    def test_403_nao_e_transitorio(self):
        """403 = proibido: falha funcional, não transitória."""
        assert not DifyClient._erro_transitorio(self._resp(403, "Forbidden"))
