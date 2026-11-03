"""Regressões da leitura de evidências e dos relatórios, sem API."""
import json
from pathlib import Path
import sys

from docx import Document
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import consolidar


@pytest.fixture
def execucao(tmp_path, monkeypatch):
    monkeypatch.setattr(consolidar, "RAIZ", tmp_path)
    (tmp_path / "datasets").mkdir()
    (tmp_path / "datasets/casos_teste.json").write_text(json.dumps({"casos": [
        {"id": "CT01", "categoria": "factual", "termos_obrigatorios": ["7"],
         "pergunta": "Qual a nota?", "resposta_referencia": "7"}]}), encoding="utf-8")
    pasta = tmp_path / "results/exec5"
    pasta.mkdir(parents=True)
    (pasta / "output.xml").write_text('''<robot generator="Robot teste" generated="2026-11-03">
      <suite name="raiz"><suite name="aninhada"><suite name="factual">
      <test id="s1-s1-s1-t1" name="CT01 Nota"><status status="FAIL">termo ausente</status></test>
      </suite></suite><test id="s1-t1" name="API"><status status="SKIP"/></test></suite>
      </robot>''', encoding="utf-8")
    (pasta / "respostas.jsonl").write_text(json.dumps({"caso_id": "CT01", "pergunta": "Qual a nota?",
        "resposta": "Resposta completa preservada", "latencia_s": 1.5}) + "\n", encoding="utf-8")
    return pasta


def test_leitura_aninhada_e_nova_execucao(execucao):
    e = consolidar.ler_execucao(5)
    assert consolidar.descobrir_execucoes() == [5]
    assert consolidar.resumo(e["testes"]) == [2, 0, 1, 1, "0.0%"]
    assert [t["experimental"] for t in e["testes"]] == [False, True]


def test_html_divergente_nao_e_silenciosamente_aceito(execucao):
    (execucao / "report.html").write_text(
        'window.output["stats"] = [[{"pass":2,"fail":0,"skip":0}]];', encoding="utf-8")
    with pytest.raises(ValueError, match="divergentes"):
        consolidar.ler_execucao(5)


def test_jsonl_ausente_e_limite_explicito(execucao):
    (execucao / "respostas.jsonl").unlink()
    e = consolidar.ler_execucao(5)
    assert not e["respostas"]
    assert any("respostas.jsonl ausente" in a for a in e["avisos"])


def test_word_preserva_resposta_falha_e_evidencias(execucao):
    originais = {p: p.read_bytes() for p in execucao.iterdir()}
    saida = consolidar.gerar_relatorio(consolidar.ler_execucao(5))
    doc = Document(saida)
    texto = "\n".join(p.text for p in doc.paragraphs)
    assert "Resposta completa preservada" in texto
    assert "termo ausente" in texto
    assert "respostas.jsonl, linha 1" in texto
    assert len(doc.tables) >= 5 and len(doc.inline_shapes) == 2
    assert all(p.read_bytes() == conteudo for p, conteudo in originais.items())


def test_word_bloqueado_preserva_original_e_continua_lote(execucao, monkeypatch, capsys):
    destino = execucao / "Relatorio_Execucao_05.docx"
    Document().save(destino)
    original = destino.read_bytes()
    segunda = execucao.parent / "exec6"
    segunda.mkdir()
    for nome in ("output.xml", "respostas.jsonl"):
        (segunda / nome).write_bytes((execucao / nome).read_bytes())

    substituir = consolidar.os.replace

    def substituir_com_bloqueio(origem, destino_final):
        if Path(destino_final) == destino:
            raise PermissionError("arquivo em uso")
        return substituir(origem, destino_final)

    monkeypatch.setattr(consolidar.os, "replace", substituir_com_bloqueio)
    monkeypatch.setattr(sys, "argv", ["consolidar.py", "5", "6"])

    consolidar.main()

    alternativo = execucao / "Relatorio_Execucao_05_novo.docx"
    assert destino.read_bytes() == original
    assert "Resposta completa preservada" in "\n".join(
        p.text for p in Document(alternativo).paragraphs)
    assert (segunda / "Relatorio_Execucao_06.docx").exists()
    assert "original foi preservado" in capsys.readouterr().err
