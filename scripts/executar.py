"""Gerenciador local do ambiente, dos testes e dos relatórios RAG-PPGCC."""
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import requests
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "results"
EXECUCAO_RE = re.compile(r"^exec(\d+)$")
IMPORTS_ESSENCIAIS = {
    "robotframework": "robot",
    "pytest": "pytest",
    "requests": "requests",
    "python-dotenv": "dotenv",
    "python-docx": "docx",
    "ragas": "ragas",
    "langchain-openai": "langchain_openai",
}
SERVICOS_ESSENCIAIS = {"api", "worker", "web"}


def agora():
    return datetime.now(timezone.utc).isoformat()


def proxima_execucao(results_dir=RESULTADOS):
    raiz = Path(results_dir)
    if not raiz.exists():
        return 1
    numeros = [int(match.group(1)) for pasta in raiz.iterdir()
               if pasta.is_dir() and (match := EXECUCAO_RE.fullmatch(pasta.name))]
    return max(numeros, default=0) + 1


def parse_services(saida):
    servicos = []
    for linha in saida.splitlines():
        try:
            item = json.loads(linha)
        except json.JSONDecodeError:
            continue
        nome = item.get("Service") or item.get("Name") or item.get("service")
        state = item.get("State") or item.get("Status") or item.get("state") or "unknown"
        servicos.append({"name": nome, "state": state})
    return servicos


class GerenciadorRAG:
    def __init__(self, raiz=RAIZ, run=subprocess.run, get=requests.get,
                 input_fn=input, output=print):
        self.raiz = Path(raiz)
        self.results = self.raiz / "results"
        self._run = run
        self._get = get
        self.input = input_fn
        self.output = output

    def _command(self, args, timeout=30, env=None):
        return self._run(
            args,
            cwd=self.raiz,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )

    def verificar_status(self):
        env_file = self.raiz / ".env"
        env = dotenv_values(env_file) if env_file.exists() else {}
        config_ok = bool(env.get("DIFY_API_URL") and env.get("DIFY_API_KEY"))
        config = {
            "arquivo_env": env_file.exists(),
            "url_configurada": bool(env.get("DIFY_API_URL")),
            "chave_configurada": bool(env.get("DIFY_API_KEY")),
        }
        python = {nome: importlib.util.find_spec(modulo) is not None
                  for nome, modulo in IMPORTS_ESSENCIAIS.items()}
        python_ok = all(python.values())
        checks = {
            "wsl": "indisponível",
            "ubuntu": "não verificada",
            "docker": "não verificado",
            "servicos": [],
            "api": "não verificada",
            "configuracao": config,
            "python": python,
        }
        try:
            installed = self._command(["wsl.exe", "--list", "--quiet"], timeout=10)
        except (OSError, subprocess.SubprocessError) as erro:
            checks["wsl"] = f"erro: {erro.__class__.__name__}"
            return self._estado(checks, "desligado", python_ok)
        if installed.returncode != 0:
            checks["wsl"] = "indisponível"
            return self._estado(checks, "desligado", python_ok)
        distros = installed.stdout.replace("\x00", "").lower()
        checks["wsl"] = "disponível"
        if "ubuntu" not in distros:
            checks["ubuntu"] = "não instalada"
            return self._estado(checks, "desligado", python_ok)

        try:
            running = self._command(["wsl.exe", "--list", "--running", "--quiet"], timeout=10)
            nomes_ativos = running.stdout.replace("\x00", "").lower()
        except (OSError, subprocess.SubprocessError) as erro:
            checks["ubuntu"] = f"erro: {erro.__class__.__name__}"
            return self._estado(checks, "desligado", python_ok)
        if running.returncode != 0 or "ubuntu" not in nomes_ativos:
            checks["ubuntu"] = "desligada"
            return self._estado(checks, "desligado", python_ok)
        checks["ubuntu"] = "em execução"

        try:
            docker = self._command([
                "wsl.exe", "-d", "Ubuntu", "--", "docker", "info", "--format", "{{.ServerVersion}}"
            ], timeout=15)
        except (OSError, subprocess.SubprocessError) as erro:
            checks["docker"] = f"indisponível ({erro.__class__.__name__})"
            return self._estado(checks, "desligado", python_ok)
        checks["docker"] = docker.stdout.strip() if docker.returncode == 0 else "indisponível"
        if docker.returncode != 0:
            return self._estado(checks, "desligado", python_ok)

        try:
            services_result = self._command([
                "wsl.exe", "-d", "Ubuntu", "--", "bash", "-lc",
                "cd ~/dify/docker && docker compose ps --format json",
            ], timeout=20)
        except (OSError, subprocess.SubprocessError) as erro:
            checks["servicos"] = [{"name": "compose", "state": f"erro ({erro.__class__.__name__})"}]
            return self._estado(checks, "parcialmente disponível", python_ok)
        checks["servicos"] = parse_services(services_result.stdout) if services_result.returncode == 0 else []
        services_running = {
            service["name"] for service in checks["servicos"]
            if service["name"] and str(service["state"]).lower().startswith(("running", "up"))
        }
        services_ok = SERVICOS_ESSENCIAIS.issubset(services_running)

        if not config_ok:
            checks["api"] = "não consultada: configuração obrigatória incompleta"
            return self._estado(checks, "erro_configuracao", python_ok, services_ok)
        try:
            response = self._get(
                f"{str(env['DIFY_API_URL']).rstrip('/')}/parameters",
                headers={"Authorization": f"Bearer {env['DIFY_API_KEY']}"},
                params={"user": "rag-ppgcc-status"},
                timeout=8,
            )
            checks["api"] = f"HTTP {response.status_code}"
            api_ok = response.status_code == 200
        except requests.RequestException as erro:
            checks["api"] = f"indisponível ({erro.__class__.__name__})"
            api_ok = False

        if api_ok and services_ok and python_ok:
            estado = "operacional"
        elif api_ok or services_running:
            estado = "parcialmente disponível"
        else:
            estado = "desligado"
        return self._estado(checks, estado, python_ok, services_ok)

    @staticmethod
    def _estado(checks, estado, python_ok, services_ok=False):
        return {
            "estado": estado,
            "checks": checks,
            "servicos_essenciais_ok": services_ok,
            "python_essencial_ok": python_ok,
        }

    def mostrar_status(self, status):
        self.output(f"Estado do ambiente: {status['estado']}")
        checks = status["checks"]
        self.output(f"WSL: {checks['wsl']} · Ubuntu: {checks['ubuntu']} · Docker Engine: {checks['docker']}")
        self.output("Serviços Dify:")
        if checks["servicos"]:
            for servico in checks["servicos"]:
                self.output(f"  {servico['name']}: {servico['state']}")
        else:
            self.output("  sem estado retornado pelo Docker Compose")
        self.output(f"API Dify: {checks['api']}")
        config = checks["configuracao"]
        self.output(".env: " + ("URL e chave configuradas" if config["url_configurada"] and config["chave_configurada"]
                                else "configuração obrigatória incompleta"))
        deps = ", ".join(nome for nome, ok in checks["python"].items() if not ok)
        self.output("Python: dependências essenciais disponíveis" if not deps else f"Python: faltam {deps}")

    def inicializar_dify(self):
        status = self.verificar_status()
        if status["estado"] == "operacional":
            self.output("Dify já está operacional; reutilizando os serviços existentes.")
            return True
        if status["checks"]["wsl"] != "disponível" or status["checks"]["ubuntu"] == "não instalada":
            self.output("Não foi possível iniciar: WSL2/Ubuntu não está disponível. Nenhuma instalação foi tentada.")
            return False
        if status["servicos_essenciais_ok"]:
            self.output("Os serviços essenciais já estão ativos, mas a aplicação não passou na verificação. "
                        "Não reinicializei o ambiente; verifique a configuração/API.")
            return False
        script = self.raiz / "scripts" / "subir_ambiente.ps1"
        if not script.exists():
            self.output(f"Script de inicialização não encontrado: {script}")
            return False
        self.output("Iniciando o ambiente com scripts/subir_ambiente.ps1 (sem reinstalar o Dify)...")
        try:
            resultado = self._command([
                "powershell.exe", "-NoProfile", "-File", str(script),
            ], timeout=240)
        except Exception as erro:
            self.output(f"Falha ao chamar subir_ambiente.ps1: {erro.__class__.__name__}")
            return False
        if resultado.stdout:
            self.output(resultado.stdout.rstrip())
        if resultado.stderr:
            self.output(resultado.stderr.rstrip())
        if resultado.returncode != 0:
            self.output(f"Inicialização falhou (código {resultado.returncode}); sem reinstalação ou limpeza automática.")
            return False
        final = self.verificar_status()
        self.mostrar_status(final)
        return final["estado"] == "operacional"

    def _nova_execucao(self, modo):
        self.results.mkdir(parents=True, exist_ok=True)
        numero = proxima_execucao(self.results)
        while True:
            pasta = self.results / f"exec{numero}"
            try:
                pasta.mkdir()
                break
            except FileExistsError:
                numero += 1
        metadata = {
            "execucao": numero,
            "modo": modo,
            "inicio_em": agora(),
            "estado": "em_andamento",
            "etapas": {},
        }
        self._salvar_metadata(pasta, metadata)
        return numero, pasta, metadata

    @staticmethod
    def _salvar_metadata(pasta, metadata):
        destino = pasta / "metadata.json"
        temporario = destino.with_suffix(".json.tmp")
        temporario.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(destino)

    def _etapa(self, pasta, metadata, nome, estado, **dados):
        metadata["etapas"][nome] = {"estado": estado, "atualizado_em": agora(), **dados}
        metadata["atualizado_em"] = agora()
        self._salvar_metadata(pasta, metadata)
        self.output(f"{nome}: {estado}")

    def _env_resultados(self, destino):
        env = os.environ.copy()
        env["RESULTADOS_JSONL"] = str(destino)
        env["PYTHONIOENCODING"] = "utf-8"
        return env

    def _executar_smoke(self, pasta, metadata):
        destino = pasta / "smoke"
        destino.mkdir(parents=True, exist_ok=True)
        self.output("Executando smoke test da API...")
        try:
            resultado = self._command(
                [sys.executable, str(self.raiz / "scripts" / "smoke_test.py")],
                timeout=180,
                env=self._env_resultados(destino / "respostas.jsonl"),
            )
        except Exception as erro:
            (destino / "smoke_test.txt").write_text(f"Erro: {erro.__class__.__name__}: {erro}", encoding="utf-8")
            self._etapa(pasta, metadata, "smoke", "falhou", erro=erro.__class__.__name__)
            return False
        (destino / "smoke_test.txt").write_text(
            (resultado.stdout or "") + ("\n" + resultado.stderr if resultado.stderr else ""),
            encoding="utf-8",
        )
        estado = "aprovado" if resultado.returncode == 0 else "falhou"
        self._etapa(pasta, metadata, "smoke", estado, codigo_saida=resultado.returncode,
                    evidencias=str(destino))
        return resultado.returncode == 0

    def _executar_unit(self, pasta, metadata):
        destino = pasta / "unit"
        destino.mkdir(parents=True, exist_ok=True)
        self.output("Executando testes unitários Python...")
        try:
            resultado = self._command(
                [sys.executable, "-m", "pytest", "tests/unit", "-q"],
                timeout=300,
            )
        except Exception as erro:
            (destino / "resultado_pytest.txt").write_text(
                f"Erro: {erro.__class__.__name__}: {erro}", encoding="utf-8")
            self._etapa(pasta, metadata, "unit", "falhou", erro=erro.__class__.__name__)
            return False
        (destino / "resultado_pytest.txt").write_text(
            (resultado.stdout or "") + ("\n" + resultado.stderr if resultado.stderr else ""),
            encoding="utf-8",
        )
        estado = "aprovado" if resultado.returncode == 0 else "falhou"
        self._etapa(pasta, metadata, "unit", estado, codigo_saida=resultado.returncode,
                    evidencias=str(destino / "resultado_pytest.txt"))
        return resultado.returncode == 0

    def _executar_robot(self, pasta, metadata, filtro=None, saida=None, incluir_smoke=False):
        saida = Path(saida or pasta)
        saida.mkdir(parents=True, exist_ok=True)
        argumentos = [sys.executable, "-m", "robot", "--outputdir", str(saida)]
        if filtro is None:
            if incluir_smoke:
                argumentos.append("tests/")
            else:
                argumentos.extend(["--exclude", "smoke", "tests/"])
        else:
            tipo, valor = filtro
            opcao = {"suite": "--suite", "tag": "--include", "caso": "--test"}[tipo]
            argumentos.extend([opcao, valor, "tests/"])
        jsonl = saida / "respostas.jsonl"
        self.output("Executando Robot Framework; falhas de cenário não interrompem as etapas posteriores...")
        try:
            resultado = self._command(argumentos, timeout=7200,
                                      env=self._env_resultados(jsonl))
        except Exception as erro:
            existe_xml = (saida / "output.xml").exists()
            self._etapa(pasta, metadata, "robot" if filtro is None else "robot_parcial", "erro",
                        erro=erro.__class__.__name__, output_xml=str(saida / "output.xml"))
            return 1, existe_xml
        if resultado.stdout:
            self.output(resultado.stdout.rstrip())
        if resultado.stderr:
            self.output(resultado.stderr.rstrip())
        existe_xml = (saida / "output.xml").exists()
        estado = "aprovado" if resultado.returncode == 0 else "reprovado" if existe_xml else "erro"
        self._etapa(pasta, metadata, "robot" if filtro is None else "robot_parcial", estado,
                    codigo_saida=resultado.returncode, output_xml=str(saida / "output.xml"),
                    respostas_jsonl=str(jsonl))
        return resultado.returncode, existe_xml

    def _executar_ragas(self, pasta, metadata=None, caso_id=None, limite=None, retomar=True):
        import avaliar_ragas

        entrada = pasta / "respostas.jsonl"
        if not entrada.exists():
            if metadata is not None:
                self._etapa(pasta, metadata, "ragas", "ignorada", motivo="respostas.jsonl ausente")
            return None
        saida_dir = pasta / "ragas"
        saida_dir.mkdir(parents=True, exist_ok=True)
        try:
            status = avaliar_ragas.avaliar(
                entrada,
                saida_dir / "metricas_ragas.csv",
                caso_id=caso_id,
                limite=limite,
                retomar=retomar,
            )
            if metadata is not None:
                self._etapa(pasta, metadata, "ragas", status["estado"],
                            status_file=str(saida_dir / "status_avaliacao.json"),
                            validas=status["validas"], falhas=status["falhas"], ausentes=status["ausentes"])
            return status
        except Exception as erro:
            if metadata is not None:
                self._etapa(pasta, metadata, "ragas", "falhou", erro=avaliar_ragas.mensagem_segura(erro))
            return None

    def _gerar_relatorios(self, numero, pasta, metadata, academico=True):
        if not (pasta / "output.xml").exists():
            self._etapa(pasta, metadata, "relatorio_individual", "ignorado",
                        motivo="output.xml ausente; evidência Robot incompleta")
            return False
        try:
            sys.path.insert(0, str(self.raiz / "scripts"))
            import consolidar
            e = consolidar.ler_execucao(numero)
            saida = consolidar.gerar_relatorio(e)
            self._etapa(pasta, metadata, "relatorio_individual", "gerado", arquivo=str(saida))
        except Exception as erro:
            self._etapa(pasta, metadata, "relatorio_individual", "falhou", erro=str(erro))
            return False
        if academico:
            try:
                import gerar_relatorio
                saida_academico = gerar_relatorio.gerar()
                self._etapa(pasta, metadata, "relatorio_academico", "gerado", arquivo=str(saida_academico))
            except Exception as erro:
                self._etapa(pasta, metadata, "relatorio_academico", "falhou", erro=str(erro))
        return True

    def executar_ciclo(self):
        self.output("Verificar e inicializar automaticamente o Dify, se necessário?")
        self.output("1. Sim — recomendado\n2. Não — apenas verificar\n3. Cancelar")
        escolha = self.input("Escolha: ").strip()
        if escolha == "3":
            self.output("Ciclo cancelado; nenhuma execução foi criada.")
            return
        if escolha not in ("1", "2"):
            self.output("Opção inválida; nenhuma execução foi criada.")
            return
        status = self.verificar_status()
        self.mostrar_status(status)
        if escolha == "1" and status["estado"] != "operacional":
            inicializado = self.inicializar_dify()
            status = self.verificar_status()
            if not inicializado or status["estado"] != "operacional":
                self.output("Dify não operacional; etapas dependentes serão interrompidas.")
        numero, pasta, metadata = self._nova_execucao("ciclo_completo")
        metadata["ambiente_inicial"] = status
        self._salvar_metadata(pasta, metadata)

        api_ok = status["estado"] == "operacional"
        if api_ok:
            api_ok = self._executar_smoke(pasta, metadata)
        else:
            self._etapa(pasta, metadata, "smoke", "interrompida", motivo="Dify não operacional")
        unit_ok = self._executar_unit(pasta, metadata)

        robot_xml = False
        if api_ok:
            _, robot_xml = self._executar_robot(pasta, metadata)
        else:
            self._etapa(pasta, metadata, "robot", "interrompida", motivo="Smoke falhou ou Dify indisponível")
        ragas_status = self._executar_ragas(pasta, metadata) if robot_xml else None
        relatorios_ok = self._gerar_relatorios(numero, pasta, metadata) if robot_xml else False
        estados = [step["estado"] for step in metadata["etapas"].values()]
        metadata["estado"] = "concluida" if all(x in ("aprovado", "gerado", "concluida") for x in estados) else "parcial"
        metadata["concluido_em"] = agora()
        self._salvar_metadata(pasta, metadata)
        self.output(f"Execução {numero}: {metadata['estado']}")
        self.output(f"Evidências: {pasta}")
        if not unit_ok:
            self.output("Aviso: testes unitários falharam; as evidências permanecem preservadas.")
        if ragas_status:
            self.output(f"Ragas: {ragas_status['estado']} ({ragas_status['validas']} métricas válidas).")
        if not relatorios_ok:
            self.output("Relatório individual não foi gerado; evidências não foram removidas.")

    def executar_smoke_individual(self):
        numero, pasta, metadata = self._nova_execucao("smoke_individual")
        ok = self._executar_smoke(pasta, metadata)
        metadata["estado"] = "concluida" if ok else "parcial"
        metadata["concluido_em"] = agora()
        self._salvar_metadata(pasta, metadata)
        self.output(f"Smoke {numero}: {metadata['estado']} · {pasta / 'smoke'}")

    def executar_unit_individual(self):
        numero, pasta, metadata = self._nova_execucao("unit_individual")
        ok = self._executar_unit(pasta, metadata)
        metadata["estado"] = "concluida" if ok else "parcial"
        metadata["concluido_em"] = agora()
        self._salvar_metadata(pasta, metadata)
        self.output(f"Testes unitários {numero}: {metadata['estado']} · {pasta / 'unit'}")

    def executar_robot_individual(self):
        self.output("Escopo Robot: 1. todos  2. suíte  3. tag  4. caso  5. cancelar")
        tipo = self.input("Escolha: ").strip()
        if tipo == "5":
            return
        mapa = {"1": None, "2": "suite", "3": "tag", "4": "caso"}
        if tipo not in mapa:
            self.output("Opção inválida.")
            return
        filtro = None if tipo == "1" else (mapa[tipo], self.input("Nome da suíte, tag ou caso: ").strip())
        if filtro and not filtro[1]:
            self.output("Filtro vazio; execução cancelada.")
            return
        numero, pasta, metadata = self._nova_execucao("robot_parcial")
        parcial = pasta / "robot_parciais" / datetime.now().strftime("%Y%m%d_%H%M%S")
        codigo, tem_xml = self._executar_robot(pasta, metadata, filtro, parcial, incluir_smoke=True)
        metadata["estado"] = "concluida" if codigo == 0 else "parcial"
        metadata["concluido_em"] = agora()
        self._salvar_metadata(pasta, metadata)
        self.output(f"Robot parcial {numero}: {'output.xml gerado' if tem_xml else 'sem output.xml'} · {parcial}")

    def escolher_execucao(self, prompt="Número da execução: "):
        try:
            numero = int(self.input(prompt).strip())
        except ValueError:
            self.output("Informe um número de execução válido.")
            return None
        pasta = self.results / f"exec{numero}"
        if numero < 1 or not pasta.is_dir():
            self.output(f"Execução exec{numero} não encontrada.")
            return None
        return numero, pasta

    def executar_ragas_individual(self):
        selecionada = self.escolher_execucao()
        if not selecionada:
            return
        numero, pasta = selecionada
        caso = self.input("Caso específico (Enter para todos): ").strip() or None
        limite_texto = self.input("Limite de amostras (Enter para sem limite): ").strip()
        try:
            limite = int(limite_texto) if limite_texto else None
            if limite is not None and limite < 1:
                raise ValueError
        except ValueError:
            self.output("Limite inválido.")
            return
        resume_text = self.input("Retomar resultados existentes? [S/n]: ").strip().lower()
        status = self._executar_ragas(pasta, None, caso, limite, resume_text != "n")
        if status:
            self.output(f"Ragas exec{numero}: {status['estado']} · válidas={status['validas']} "
                        f"falhas={status['falhas']} ausentes={status['ausentes']}")

    def gerar_relatorios_individual(self):
        self.output("Relatório: 1. individual  2. acadêmico  3. ambos  4. cancelar")
        tipo = self.input("Escolha: ").strip()
        if tipo in ("1", "3"):
            selecionada = self.escolher_execucao()
            if selecionada:
                numero, pasta = selecionada
                if (pasta / "output.xml").exists():
                    sys.path.insert(0, str(self.raiz / "scripts"))
                    import consolidar
                    destino = consolidar.gerar_relatorio(consolidar.ler_execucao(numero))
                    self.output(f"Relatório individual: {destino}")
                else:
                    self.output("A execução não tem output.xml; o relatório não foi regenerado.")
        if tipo in ("2", "3"):
            sys.path.insert(0, str(self.raiz / "scripts"))
            import gerar_relatorio
            self.output(f"Relatório acadêmico: {gerar_relatorio.gerar()}")
        elif tipo not in ("1", "4"):
            self.output("Opção inválida.")

    def consultar_resultados(self):
        sys.path.insert(0, str(self.raiz / "scripts"))
        import consolidar
        execucoes = sorted(
            ((int(match.group(1)), pasta) for pasta in self.results.iterdir()
             if pasta.is_dir() and (match := EXECUCAO_RE.fullmatch(pasta.name))),
            key=lambda item: item[0],
        ) if self.results.exists() else []
        if not execucoes:
            self.output("Nenhuma execução registrada.")
            return
        for numero, pasta in execucoes:
            metadata_path = pasta / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
            if (pasta / "output.xml").exists():
                e = consolidar.ler_execucao(numero)
                exp = [t for t in e["testes"] if t["experimental"]]
                aux = [t for t in e["testes"] if not t["experimental"]]
                self.output(f"exec{numero}: RAG {consolidar.resumo(exp)} · API/infra {consolidar.resumo(aux)}")
            else:
                self.output(f"exec{numero}: {metadata.get('modo', 'parcial')} · "
                            f"{metadata.get('estado', 'sem output.xml Robot')}")
            status_path = pasta / "ragas" / "status_avaliacao.json"
            if status_path.exists():
                status = json.loads(status_path.read_text(encoding="utf-8"))
                self.output(f"  Ragas: {status['estado']} · válidas={status['validas']} "
                            f"falhas={status['falhas']} ausentes={status['ausentes']}")

    def menu(self):
        while True:
            self.output("\nRAG-PPGCC — GERENCIADOR DE TESTES")
            self.output("1. Verificar status do ambiente\n2. Inicializar ambiente Dify\n3. Executar ciclo completo\n"
                        "4. Executar smoke test\n5. Executar testes Robot Framework\n6. Executar testes unitários Python\n"
                        "7. Executar avaliação semântica Ragas\n8. Gerar relatórios Word\n9. Consultar resultados das execuções\n10. Sair")
            escolha = self.input("Escolha: ").strip()
            if escolha == "1":
                self.mostrar_status(self.verificar_status())
            elif escolha == "2":
                self.inicializar_dify()
            elif escolha == "3":
                self.executar_ciclo()
            elif escolha == "4":
                self.executar_smoke_individual()
            elif escolha == "5":
                self.executar_robot_individual()
            elif escolha == "6":
                self.executar_unit_individual()
            elif escolha == "7":
                self.executar_ragas_individual()
            elif escolha == "8":
                self.gerar_relatorios_individual()
            elif escolha == "9":
                self.consultar_resultados()
            elif escolha == "10":
                self.output("Encerrado.")
                return
            else:
                self.output("Opção inválida; escolha de 1 a 10.")


def main():
    GerenciadorRAG().menu()


if __name__ == "__main__":
    main()
