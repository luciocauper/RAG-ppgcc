"""Verificações determinísticas sobre as respostas do SUT, expostas como biblioteca do Robot Framework.

As métricas semânticas (Ragas) não rodam aqui: são calculadas em lote por scripts/avaliar_ragas.py,
sobre o arquivo de respostas gerado na execução da suíte.
"""
import difflib
import itertools
import json
import re
import unicodedata
from pathlib import Path

from robot.api import SkipExecution, logger
from robot.api.deco import keyword, library

RAIZ = Path(__file__).resolve().parent.parent

# Expressões que indicam que o assistente reconheceu não haver a informação no regimento.
PADROES_AUSENCIA = [
    r"nao (consta|ha|encontrei|existe|foi possivel|esta (disponivel|prevista?|especificad[ao]))",
    r"nao (menciona|informa|especifica|trata|aborda|define|estabelece|preve|fixa|determina|lista|nomeia|detalha|apresenta|contem|traz)",
    r"nao (sao|estao|e|esta) (nomead|listad|especificad|informad|mencionad|definid|citad|previst)",
    r"nao ha (o |um |nenhum )?art",
    r"inexist",
    r"nao sei",
    r"nao (possuo|tenho|disponho de) (informac|dados)",
    r"nao (esta|e) relacionad",
    r"nao (posso|consigo|e possivel) (responder|informar)",
    r"(sem|nenhuma) informac",
    r"fora do escopo",
]
PADRAO_CITACAO = r"\b(art\.?|artigo)\s*\d+"


def normalizar(texto):
    """Minúsculas, sem acentos, sem markdown e com espaços colapsados, para comparações tolerantes.

    Também reduz "12 (doze) meses" a "12 meses", estilo de redação do regimento que o modelo copia.
    """
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    texto = re.sub(r"[*_`#]", "", texto)
    texto = re.sub(r"(\d+)\s*\(\s*[a-z][a-z\s-]*\)", r"\1", texto)
    return re.sub(r"\s+", " ", texto).strip()


@library(scope="GLOBAL")
class RagEvaluator:
    def __init__(self, dataset="datasets/casos_teste.json"):
        caminho = RAIZ / dataset
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        self.casos = {c["id"]: c for c in dados["casos"]}

    @keyword("Obter Caso")
    def obter_caso(self, caso_id):
        if caso_id not in self.casos:
            raise AssertionError(f"Caso {caso_id} não existe em datasets/casos_teste.json")
        caso = self.casos[caso_id]
        if not caso.get("verificado", False):
            logger.warn(f"{caso_id}: resposta de referência ainda NÃO conferida no regimento.")
        return caso

    @keyword("Validar Caso")
    def validar_caso(self, criterios, resposta, pular_sem_criterios=True):
        """Aplica os critérios declarados no caso (ou em um turno de conversa) à resposta.

        Critérios suportados: ``termos_obrigatorios``, ``termos_proibidos``,
        ``deve_reconhecer_ausencia`` e ``deve_citar_artigo``. Cada termo obrigatório pode ser
        uma string ou uma lista de alternativas (basta uma estar presente).
        """
        falhas = []
        avaliados = 0
        if criterios.get("termos_obrigatorios"):
            avaliados += 1
            falhas += self._termos_ausentes(resposta, criterios["termos_obrigatorios"])
        if criterios.get("termos_proibidos"):
            avaliados += 1
            falhas += self._termos_presentes(resposta, criterios["termos_proibidos"])
        if criterios.get("deve_reconhecer_ausencia"):
            avaliados += 1
            if not self.reconhece_ausencia(resposta):
                falhas.append("não reconheceu a ausência da informação no regimento")
        if criterios.get("deve_citar_artigo"):
            avaliados += 1
            if not re.search(PADRAO_CITACAO, normalizar(resposta)):
                falhas.append("não citou artigo do regimento")

        if avaliados == 0 and pular_sem_criterios is True:
            raise SkipExecution("Caso sem critérios de aceitação definidos no dataset.")
        if falhas:
            raise AssertionError("; ".join(falhas))

    @keyword("Reconhece Ausencia De Informacao")
    def reconhece_ausencia(self, resposta):
        texto = normalizar(resposta)
        return any(re.search(p, texto) for p in PADROES_AUSENCIA)

    @keyword("Validar Latencia")
    def validar_latencia(self, resultados, limite_s):
        latencias = [r["latencia_s"] for r in resultados]
        media = sum(latencias) / len(latencias)
        logger.info(f"Latências (s): {latencias} | média {media:.2f} | máx {max(latencias):.2f}")
        if max(latencias) > float(limite_s):
            raise AssertionError(f"Latência máxima {max(latencias):.2f} s excede o limite de {limite_s} s")
        return media

    @keyword("Validar Consistencia")
    def validar_consistencia(self, resultados, minimo):
        """Similaridade lexical média entre pares de respostas à mesma pergunta.

        É um indicador simples de variabilidade; a consistência factual é verificada
        à parte, aplicando os critérios do caso a cada repetição.
        """
        textos = [normalizar(r["resposta"]) for r in resultados]
        pares = list(itertools.combinations(textos, 2))
        media = sum(difflib.SequenceMatcher(None, a, b).ratio() for a, b in pares) / len(pares)
        logger.info(f"Similaridade média entre {len(textos)} respostas: {media:.3f}")
        if media < float(minimo):
            raise AssertionError(f"Similaridade média {media:.3f} abaixo do mínimo {minimo}")
        return media

    def _termos_ausentes(self, resposta, termos):
        texto = normalizar(resposta)
        falhas = []
        for termo in termos:
            alternativas = termo if isinstance(termo, list) else [termo]
            if not any(normalizar(t) in texto for t in alternativas):
                falhas.append(f"termo obrigatório ausente: {' | '.join(alternativas)}")
        return falhas

    def _termos_presentes(self, resposta, termos):
        texto = normalizar(resposta)
        return [f"termo proibido presente: {t}" for t in termos if normalizar(t) in texto]
