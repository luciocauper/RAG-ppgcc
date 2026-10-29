"""Cliente da API de chat do Dify (edição community), exposto como biblioteca do Robot Framework.

Cada chamada é registrada em RESULTADOS_JSONL (pergunta, resposta, contextos recuperados,
latência), que depois alimenta a avaliação com Ragas (scripts/avaliar_ragas.py).
"""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from robot.api import logger
from robot.api.deco import keyword, library

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


@library(scope="GLOBAL")
class DifyClient:
    def __init__(self, base_url=None, api_key=None, timeout=None):
        self.base_url = (base_url or os.getenv("DIFY_API_URL", "http://localhost/v1")).rstrip("/")
        self.api_key = api_key or os.getenv("DIFY_API_KEY", "")
        self.timeout = float(timeout or os.getenv("DIFY_TIMEOUT", "120"))
        self.user = os.getenv("DIFY_USER", "robot-tests")
        self.saida = RAIZ / os.getenv("RESULTADOS_JSONL", "results/respostas.jsonl")
        # Plano gratuito do Gemini: pausa entre chamadas e novas tentativas quando a cota estoura.
        self.intervalo_s = float(os.getenv("DIFY_INTERVALO_S", "0"))
        self.max_tentativas = int(os.getenv("DIFY_MAX_TENTATIVAS", "5"))
        self.espera_base_s = float(os.getenv("DIFY_ESPERA_BASE_S", "15"))
        self.session = requests.Session()

    def _headers(self, api_key=None):
        return {
            "Authorization": f"Bearer {api_key or self.api_key}",
            "Content-Type": "application/json",
        }

    @keyword("Verificar Disponibilidade Da API")
    def verificar_disponibilidade(self):
        """Falha se a API do Dify estiver inacessível ou a chave for inválida."""
        if not self.api_key or self.api_key.startswith("app-xxx"):
            raise AssertionError("DIFY_API_KEY não configurada no .env (veja .env.example)")
        resp = self.session.get(
            f"{self.base_url}/parameters",
            headers=self._headers(),
            params={"user": self.user},
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise AssertionError(f"API do Dify indisponível: HTTP {resp.status_code} - {resp.text[:300]}")

    @keyword("Enviar Pergunta")
    def enviar_pergunta(self, pergunta, conversation_id="", caso_id=None, rodada=1):
        """Envia uma pergunta ao chatbot e retorna um dicionário com resposta, contextos e latência.

        Passe o ``conversation_id`` de uma resposta anterior para manter o contexto da conversa;
        vazio inicia uma nova conversa.
        """
        payload = {
            "inputs": {},
            "query": pergunta,
            "response_mode": "blocking",
            "conversation_id": conversation_id or "",
            "user": self.user,
        }
        resp, latencia, tentativas = self._post_com_retentativa(payload)
        if resp.status_code != 200:
            raise AssertionError(f"Dify retornou HTTP {resp.status_code}: {resp.text[:500]}")

        corpo = resp.json()
        recursos = corpo.get("metadata", {}).get("retriever_resources", []) or []
        resultado = {
            "caso_id": caso_id,
            "rodada": int(rodada),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pergunta": pergunta,
            "resposta": corpo.get("answer", ""),
            "conversation_id": corpo.get("conversation_id", ""),
            "message_id": corpo.get("message_id", ""),
            "latencia_s": round(latencia, 3),
            "tentativas": tentativas,
            "contextos": [r.get("content", "") for r in recursos],
            "fontes": [
                {
                    "documento": r.get("document_name"),
                    "segment_id": r.get("segment_id"),
                    "score": r.get("score"),
                }
                for r in recursos
            ],
            "uso": corpo.get("metadata", {}).get("usage", {}),
        }
        self._registrar(resultado)
        logger.info(
            f"Pergunta: {pergunta}\nResposta ({resultado['latencia_s']} s): {resultado['resposta']}\n"
            f"Trechos recuperados: {len(recursos)}"
        )
        return resultado

    @keyword("Obter Status Da Requisicao")
    def obter_status(self, pergunta, api_key=None):
        """Envia uma pergunta sem exigir sucesso e retorna apenas o status HTTP.

        Usado em testes negativos (chave inválida, entrada extensa).
        """
        resp = self.session.post(
            f"{self.base_url}/chat-messages",
            headers=self._headers(api_key=api_key),
            json={"inputs": {}, "query": pergunta, "response_mode": "blocking", "user": self.user},
            timeout=self.timeout,
        )
        logger.info(f"HTTP {resp.status_code}: {resp.text[:300]}")
        return resp.status_code

    def _post_com_retentativa(self, payload):
        """POST em /chat-messages, repetindo quando o provedor do LLM recusa por limite de cota.

        A latência devolvida é a da tentativa bem-sucedida, sem incluir as esperas, para não
        contaminar os testes de desempenho com o rate limit do plano gratuito.
        """
        for tentativa in range(1, self.max_tentativas + 1):
            if self.intervalo_s:
                time.sleep(self.intervalo_s)
            inicio = time.perf_counter()
            resp = self.session.post(
                f"{self.base_url}/chat-messages",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
            latencia = time.perf_counter() - inicio
            if not self._erro_transitorio(resp) or tentativa == self.max_tentativas:
                return resp, latencia, tentativa
            espera = self.espera_base_s * 2 ** (tentativa - 1)
            logger.warn(f"Erro transitório do provedor (HTTP {resp.status_code}); nova tentativa em {espera:.0f} s")
            time.sleep(espera)

    @staticmethod
    def _erro_transitorio(resp):
        """Cota estourada ou falha de rede/serviço entre o Dify e o Gemini — não é comportamento do SUT.

        O Dify repassa esses erros do plugin como HTTP 400; o texto da mensagem os identifica.
        """
        if resp.status_code in (429, 502, 503, 504):
            return True
        texto = resp.text.lower()
        return resp.status_code >= 400 and any(
            marca in texto
            for marca in (
                "resource_exhausted", "rate limit", "ratelimit", "quota", "429",
                "network is unreachable", "connecterror", "connection reset", "timed out",
                "503", "unavailable", "overloaded",
            )
        )

    def _registrar(self, resultado):
        self.saida.parent.mkdir(parents=True, exist_ok=True)
        with self.saida.open("a", encoding="utf-8") as f:
            f.write(json.dumps(resultado, ensure_ascii=False) + "\n")
