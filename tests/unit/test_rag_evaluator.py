"""Testes unitários das verificações determinísticas (rag_evaluator.py).

Estes testes NÃO chamam o SUT nem o LLM juiz: validam apenas a lógica determinística
de normalização, detecção de ausência, verificação de termos, latência e consistência.
"""
import pytest

from rag_evaluator import normalizar, RagEvaluator


# --- normalizar ---

class TestNormalizar:
    def test_minusculas_e_sem_acentos(self):
        assert normalizar("Aprovação") == "aprovacao"

    def test_remove_markdown(self):
        assert normalizar("**não** é permitido") == "nao e permitido"

    def test_remove_extenso_entre_parenteses(self):
        assert normalizar("12 (doze) meses") == "12 meses"

    def test_colapsa_espacos(self):
        assert normalizar("nota   7,0") == "nota 7,0"

    def test_string_vazia(self):
        assert normalizar("") == ""

    def test_numero_com_virgula_preservado(self):
        assert "7,0" in normalizar("conceito igual ou superior a 7,0 (sete)")


# --- reconhece_ausencia ---

class TestReconheceAusencia:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_reconhece_nao_consta(self, avaliador):
        assert avaliador.reconhece_ausencia("Esta informação não consta no regimento.")

    def test_reconhece_nao_ha(self, avaliador):
        assert avaliador.reconhece_ausencia("Não há dados sobre o valor da bolsa.")

    def test_reconhece_nao_sei(self, avaliador):
        assert avaliador.reconhece_ausencia("Eu não sei a resposta.")

    def test_reconhece_fora_do_escopo(self, avaliador):
        assert avaliador.reconhece_ausencia("Isso está fora do escopo do regimento.")

    def test_reconhece_nao_possuo_informacoes(self, avaliador):
        assert avaliador.reconhece_ausencia("Não possuo informações sobre a taxa de matrícula.")

    def test_nao_reconhece_resposta_factual(self, avaliador):
        assert not avaliador.reconhece_ausencia(
            "A nota mínima para aprovação é 7,0, conforme o Art. 37."
        )

    def test_nao_reconhece_com_negacao_apenas(self, avaliador):
        assert not avaliador.reconhece_ausencia(
            "O aluno não pode cursar menos de 24 créditos."
        )


# --- validar_caso: termos_obrigatorios ---

class TestTermosObrigatorios:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_termo_presente_passa(self, avaliador):
        criterios = {"termos_obrigatorios": ["7,0"]}
        avaliador.validar_caso(criterios, "A nota mínima é 7,0 (sete).")

    def test_termo_ausente_falha(self, avaliador):
        criterios = {"termos_obrigatorios": ["7,0"]}
        with pytest.raises(AssertionError, match="termo obrigatório ausente"):
            avaliador.validar_caso(criterios, "A nota mínima é 5,0.")

    def test_lista_de_alternativas_basta_uma(self, avaliador):
        criterios = {"termos_obrigatorios": [["7,0", "7.0", "sete"]]}
        avaliador.validar_caso(criterios, "A nota é sete.")

    def test_lista_de_alternativas_todausentes_falha(self, avaliador):
        criterios = {"termos_obrigatorios": [["7,0", "7.0", "sete"]]}
        with pytest.raises(AssertionError):
            avaliador.validar_caso(criterios, "A nota é cinco.")

    def test_normalizacao_ignora_acentos(self, avaliador):
        criterios = {"termos_obrigatorios": ["colegiado"]}
        avaliador.validar_caso(criterios, "Cabe ao Colegiado aprovar o edital.")


# --- validar_caso: termos_proibidos ---

class TestTermosProibidos:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_termo_proibido_ausente_passa(self, avaliador):
        criterios = {"termos_proibidos": ["R$"]}
        avaliador.validar_caso(criterios, "O regimento não informa valores de bolsa.")

    def test_termo_proibido_presente_falha(self, avaliador):
        criterios = {"termos_proibidos": ["R$"]}
        with pytest.raises(AssertionError, match="termo proibido presente"):
            avaliador.validar_caso(criterios, "A bolsa é de R$ 2.000,00.")

    def test_termo_proibido_canberra(self, avaliador):
        criterios = {"termos_proibidos": ["Canberra"]}
        with pytest.raises(AssertionError, match="Canberra"):
            avaliador.validar_caso(criterios, "A capital da Austrália é Canberra.")


# --- validar_caso: deve_reconhecer_ausencia ---

class TestReconhecerAusencia:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_reconheceu_passa(self, avaliador):
        criterios = {"deve_reconhecer_ausencia": True}
        avaliador.validar_caso(criterios, "O regimento não menciona esse valor.")

    def test_nao_reconheceu_falha(self, avaliador):
        criterios = {"deve_reconhecer_ausencia": True}
        with pytest.raises(AssertionError, match="não reconheceu a ausência"):
            avaliador.validar_caso(criterios, "A bolsa é de R$ 1.500 por mês.")


# --- validar_caso: deve_citar_artigo ---

class TestCitarArtigo:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_citou_artigo_passa(self, avaliador):
        criterios = {"deve_citar_artigo": True}
        avaliador.validar_caso(criterios, "Segundo o Art. 37, a nota é 7,0.")

    def test_citou_artigo_com_ponto_passa(self, avaliador):
        criterios = {"deve_citar_artigo": True}
        avaliador.validar_caso(criterios, "Conforme o art. 39, alínea d.")

    def test_nao_citou_artigo_falha(self, avaliador):
        criterios = {"deve_citar_artigo": True}
        with pytest.raises(AssertionError, match="não citou artigo"):
            avaliador.validar_caso(criterios, "A nota mínima é 7,0.")


# --- validar_caso: sem criterios ---

class TestSemCriterios:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_sem_criterios_pula_por_padrao(self, avaliador):
        from robot.api import SkipExecution
        with pytest.raises(SkipExecution):
            avaliador.validar_caso({}, "qualquer resposta")

    def test_sem_criterios_nao_pula_quando_solicitado(self, avaliador):
        avaliador.validar_caso({}, "qualquer resposta", pular_sem_criterios=False)


# --- validar_caso: combinacao de criterios ---

class TestCombinacaoCriterios:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_obrigatorios_e_proibidos_juntos(self, avaliador):
        criterios = {
            "termos_obrigatorios": ["75%"],
            "termos_proibidos": ["R$"],
        }
        avaliador.validar_caso(criterios, "A frequência mínima é de 75%.")

    def test_falha_acumulada(self, avaliador):
        criterios = {
            "termos_obrigatorios": ["75%"],
            "termos_proibidos": ["R$"],
        }
        with pytest.raises(AssertionError) as exc:
            avaliador.validar_caso(criterios, "O valor é R$ 100.")
        assert "ausente" in str(exc.value)
        assert "proibido" in str(exc.value)


# --- validar_latencia ---

class TestLatencia:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_dentro_do_limite_passa(self, avaliador):
        resultados = [{"latencia_s": 1.0}, {"latencia_s": 2.0}, {"latencia_s": 3.0}]
        media = avaliador.validar_latencia(resultados, limite_s=10.0)
        assert media == pytest.approx(2.0)

    def test_excede_limite_falha(self, avaliador):
        resultados = [{"latencia_s": 1.0}, {"latencia_s": 35.0}]
        with pytest.raises(AssertionError, match="excede o limite"):
            avaliador.validar_latencia(resultados, limite_s=30.0)


# --- validar_consistencia ---

class TestConsistencia:
    @pytest.fixture
    def avaliador(self):
        return RagEvaluator()

    def test_respostas_identicas_alta_similaridade(self, avaliador):
        resultados = [
            {"resposta": "A nota mínima é 7,0."},
            {"resposta": "A nota mínima é 7,0."},
            {"resposta": "A nota mínima é 7,0."},
        ]
        media = avaliador.validar_consistencia(resultados, minimo=0.9)
        assert media == pytest.approx(1.0)

    def test_respostas_diferentes_baixa_similaridade(self, avaliador):
        resultados = [
            {"resposta": "A nota mínima é 7,0 conforme o artigo 37."},
            {"resposta": "O regimento estabelece frequência de 75%."},
        ]
        with pytest.raises(AssertionError, match="abaixo do mínimo"):
            avaliador.validar_consistencia(resultados, minimo=0.5)


# --- obter_caso ---

class TestObterCaso:
    def test_caso_existente(self):
        avaliador = RagEvaluator()
        caso = avaliador.obter_caso("CT01")
        assert caso["id"] == "CT01"
        assert "pergunta" in caso
        assert "termos_obrigatorios" in caso

    def test_caso_inexistente_falha(self):
        avaliador = RagEvaluator()
        with pytest.raises(AssertionError, match="CT99"):
            avaliador.obter_caso("CT99")
