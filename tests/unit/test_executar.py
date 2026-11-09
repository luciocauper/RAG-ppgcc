"""Fluxos do gerenciador testados com subprocess e HTTP simulados."""
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import executar


def processo(args, stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args, returncode, stdout, stderr)


def test_proxima_execucao_nao_reutiliza_pastas(tmp_path):
    assert executar.proxima_execucao(tmp_path) == 1
    (tmp_path / "exec1").mkdir()
    (tmp_path / "exec4").mkdir()
    (tmp_path / "exec4" / "unit").mkdir()
    (tmp_path / "exec-bad").mkdir()
    assert executar.proxima_execucao(tmp_path) == 5


def test_status_operacional_usa_compose_e_api_sem_expor_chave(tmp_path):
    (tmp_path / ".env").write_text(
        "DIFY_API_URL=http://localhost/v1\nDIFY_API_KEY=fake-key\n", encoding="utf-8")
    compose = "\n".join(json.dumps({"Service": name, "State": "running", "Status": "Up"})
                         for name in ("api", "worker", "web"))
    results = [
        processo([], "Ubuntu\n"),
        processo([], "Ubuntu\n"),
        processo([], "27.5\n"),
        processo([], compose),
    ]
    getter = Mock(return_value=Mock(status_code=200))
    manager = executar.GerenciadorRAG(tmp_path, run=Mock(side_effect=results), get=getter,
                                      output=lambda _: None)

    status = manager.verificar_status()

    assert status["estado"] == "operacional"
    assert status["servicos_essenciais_ok"]
    assert "fake-key" not in repr(status)
    assert getter.call_args.kwargs["headers"]["Authorization"] == "Bearer fake-key"


def test_status_nao_chama_api_se_configuracao_ausente(tmp_path):
    manager = executar.GerenciadorRAG(tmp_path, run=Mock(), get=Mock(), output=lambda _: None)
    manager._command = Mock(side_effect=[
        processo([], "Ubuntu"), processo([], "Ubuntu"), processo([], "27.5"),
        processo([], ""),
    ])

    status = manager.verificar_status()

    assert status["estado"] == "erro_configuracao"
    manager._get.assert_not_called()


def test_inicializacao_reutiliza_dify_operacional(tmp_path):
    manager = executar.GerenciadorRAG(tmp_path, run=Mock(), get=Mock(), output=lambda _: None)
    manager.verificar_status = Mock(return_value={"estado": "operacional", "checks": {}})
    manager._command = Mock()

    assert manager.inicializar_dify()
    manager._command.assert_not_called()


def test_inicializacao_delega_ao_script_existente(tmp_path):
    script = tmp_path / "scripts" / "subir_ambiente.ps1"
    script.parent.mkdir()
    script.touch()
    manager = executar.GerenciadorRAG(tmp_path, run=Mock(), get=Mock(), output=lambda _: None)
    off = {"estado": "desligado", "checks": {"wsl": "disponível", "ubuntu": "desligada",
                                               "docker": "indisponível", "servicos": []},
           "servicos_essenciais_ok": False}
    ready = {"estado": "operacional", "checks": {"wsl": "disponível", "ubuntu": "em execução",
                                                    "docker": "27.5", "servicos": [],
                                                    "api": "HTTP 200", "configuracao": {}, "python": {}},
             "servicos_essenciais_ok": True}
    manager.mostrar_status = Mock()
    manager.verificar_status = Mock(side_effect=[off, ready])
    manager._command = Mock(return_value=processo([], "Dify started"))

    assert manager.inicializar_dify()
    args = manager._command.call_args.args[0]
    assert args[:3] == ["powershell.exe", "-NoProfile", "-File"]
    assert args[3] == str(script)


def test_ciclo_prossegue_apos_reprovacao_robot(tmp_path):
    manager = executar.GerenciadorRAG(tmp_path, run=Mock(), get=Mock(),
                                      input_fn=lambda _: "2", output=lambda _: None)
    manager.verificar_status = Mock(return_value={
        "estado": "operacional",
        "checks": {"wsl": "disponível", "ubuntu": "em execução", "docker": "27.5",
                   "servicos": [], "api": "HTTP 200", "configuracao": {}, "python": {}},
    })
    manager.mostrar_status = Mock()
    ordem = []
    def registar(pasta, metadata, nome, estado):
        metadata["etapas"][nome] = {"estado": estado}

    def unit(pasta, metadata):
        ordem.append("unit")
        registar(pasta, metadata, "unit", "aprovado")
        return True

    def smoke(pasta, metadata):
        ordem.append("smoke")
        registar(pasta, metadata, "smoke", "aprovado")
        return True

    def robot(pasta, metadata):
        ordem.append("robot")
        registar(pasta, metadata, "robot", "reprovado")
        return 1, True

    def ragas(pasta, metadata):
        ordem.append("ragas")
        registar(pasta, metadata, "ragas", "parcial")
        return {"estado": "parcial", "validas": 1}

    def relatorios(numero, pasta, metadata):
        ordem.append("relatorios")
        registar(pasta, metadata, "relatorio_individual", "gerado")
        return True

    manager._executar_unit = unit
    manager._executar_smoke = smoke
    manager._executar_robot = robot
    manager._executar_ragas = ragas
    manager._gerar_relatorios = relatorios

    manager.executar_ciclo()

    assert ordem == ["smoke", "unit", "robot", "ragas", "relatorios"]
    pasta = tmp_path / "results" / "exec1"
    saved = json.loads((pasta / "metadata.json").read_text(encoding="utf-8"))
    assert saved["etapas"]["robot"]["estado"] == "reprovado"
    assert saved["estado"] == "parcial"
