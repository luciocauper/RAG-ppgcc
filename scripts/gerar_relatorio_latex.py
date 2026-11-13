"""Converte o relatório revisado (Word) para LaTeX, na estrutura de template.tex.

Entrada: results/Relatorio_Final_Testes_RAG_PPGCC_Revisado.docx
Saída:   relatorio_latex/relatorio.tex e relatorio_latex/figuras/*.png (pasta pronta para o Overleaf)

O conteúdo vem integralmente do Word, que por sua vez é derivado das evidências; nada é digitado aqui
além da capa e do preâmbulo. Compilar com: pdflatex relatorio.tex (duas vezes, por causa do sumário).
"""
from pathlib import Path
import re
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "results" / "Relatorio_Final_Testes_RAG_PPGCC_Revisado.docx"
DESTINO = RAIZ / "relatorio_latex"
SAIDA = DESTINO / "relatorio.tex"

TITULO = "Avaliação automatizada da qualidade de um sistema inteligente baseado em RAG"
SUBTITULO = ("Infraestrutura de testes com Robot Framework, pytest e Ragas aplicada a um assistente "
             "sobre o Regimento do PPGCC/UECE")
DATA = "Novembro de 2026"
# Preencha com os nomes da equipe; as evidências não identificam formalmente os responsáveis.
AUTORES = [r"\textit{[Nome do(a) aluno(a) 1]}", r"\textit{[Nome do(a) aluno(a) 2]}"]

ESPECIAIS = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    "≥": r"$\geq$", "≤": r"$\leq$", "×": r"$\times$", "→": r"$\rightarrow$", "←": r"$\leftarrow$",
    "≠": r"$\neq$", "↔": r"$\leftrightarrow$", "·": r"$\cdot$", "…": r"\ldots{}", "\u00a0": "~",
    "−": "-", "\u2009": r"\,", "\uf0b0": "",
}
# Caracteres não ASCII aceitos diretamente pelo inputenc utf8 + T1.
ACEITOS = set("áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑºª§°—–“”‘’«»")


def esc(texto):
    saida = []
    for c in texto:
        if c in ESPECIAIS:
            saida.append(ESPECIAIS[c])
        elif ord(c) < 128 or c in ACEITOS:
            saida.append(c)
        else:
            raise ValueError(f"Caractere sem mapeamento LaTeX: {c!r} (U+{ord(c):04X}) em {texto[:60]!r}")
    return "".join(saida)


def esc_hash(texto):
    """Hashes longos: fonte monoespaçada com pontos de quebra a cada 16 caracteres."""
    return r"\texttt{" + r"\allowbreak{}".join(texto[i:i + 16] for i in range(0, len(texto), 16)) + "}"


def esc_celula(texto):
    texto = texto.strip()
    if re.fullmatch(r"[0-9a-f]{64}", texto):
        return esc_hash(texto)
    return esc(texto).replace("\n", r" \newline ")


def blocos(doc):
    for el in doc.element.body.iterchildren():
        if el.tag == qn("w:p"):
            yield Paragraph(el, doc)
        elif el.tag == qn("w:tbl"):
            yield Table(el, doc)


def imagem(par, doc):
    blip = par._p.find(".//" + qn("a:blip"))
    if blip is None:
        return None
    return doc.part.related_parts[blip.get(qn("r:embed"))]


def titulo_secao(texto):
    if texto.startswith("Apêndice"):
        return "apendice", re.sub(r"^Apêndice\s+[A-Z]\s+—\s+", "", texto)
    return "normal", re.sub(r"^\d+(\.\d+)*\.?\s+", "", texto)


def larguras(linhas):
    cols = len(linhas[0])
    pesos = []
    for j in range(cols):
        tamanhos = [len(l[j]) for l in linhas]
        media = sum(tamanhos) / len(tamanhos)
        pesos.append(max(4.0, min(60.0, max(tamanhos) * .35 + media * .65)) ** .8)
    total = sum(pesos)
    util = .98 - .02 * cols  # desconta o espaçamento entre colunas
    return [util * p / total for p in pesos]


def tabela_latex(t, legenda=None, fonte=None):
    linhas = [[c.text for c in r.cells] for r in t.rows]
    ws = larguras(linhas)
    spec = "".join(rf">{{\raggedright\arraybackslash}}p{{{w:.3f}\linewidth}}" for w in ws)
    cab = " & ".join(r"\textbf{" + esc_celula(c) + "}" for c in linhas[0]) + r" \\"
    out = [r"{\footnotesize", r"\begin{longtable}{" + spec + "}"]
    if legenda:
        out.append(r"\caption{" + esc(legenda) + r"}\\")
    out += [r"\toprule", cab, r"\midrule", r"\endfirsthead",
            r"\toprule", cab, r"\midrule", r"\endhead",
            r"\bottomrule", r"\endfoot"]
    for linha in linhas[1:]:
        out.append(" & ".join(esc_celula(c) for c in linha) + r" \\")
    out.append(r"\end{longtable}}")
    if fonte:
        out.append(r"\vspace{-0.6em}{\footnotesize\noindent Fonte: " + esc(fonte) + r"}\par\medskip")
    return out


def corpo(doc):
    out, figuras, n_fig = [], DESTINO / "figuras", 0
    itens = list(blocos(doc))
    i, em_lista, iniciou = 0, False, False
    legenda_tabela = None

    def fechar_lista():
        nonlocal em_lista
        if em_lista:
            out.append(r"\end{itemize}")
            em_lista = False

    while i < len(itens):
        b = itens[i]
        if isinstance(b, Table):
            fechar_lista()
            fonte = None
            j = i + 1  # o Word insere um parágrafo vazio após cada tabela
            while (j < len(itens) and isinstance(itens[j], Paragraph) and not itens[j].text.strip()
                   and imagem(itens[j], doc) is None):
                j += 1
            if j < len(itens) and isinstance(itens[j], Paragraph) and itens[j].text.startswith("Fonte:"):
                fonte = itens[j].text[len("Fonte:"):].strip()
                i = j
            out += tabela_latex(b, legenda_tabela, fonte)
            legenda_tabela = None
            i += 1
            continue
        texto = b.text.strip()
        estilo = b.style.name
        parte = imagem(b, doc)
        if not iniciou:  # capa e nota de versão: tratadas no preâmbulo do template
            if estilo.startswith("Heading") and texto == "Resumo":
                iniciou = True
            else:
                i += 1
                continue
        if parte is not None:
            fechar_lista()
            n_fig += 1
            nome = f"fig{n_fig:02d}.png"
            figuras.mkdir(parents=True, exist_ok=True)
            (figuras / nome).write_bytes(parte.blob)
            legenda, fonte = "", ""
            if i + 1 < len(itens) and isinstance(itens[i + 1], Paragraph) and itens[i + 1].text.startswith("Figura"):
                cap = re.sub(r"^Figura \d+ — ", "", itens[i + 1].text.strip())
                legenda, _, fonte = cap.partition(". Fonte: ")
                fonte = fonte.rstrip(".")
                i += 1
            out += [r"\begin{figure}[H]", r"\centering",
                    rf"\includegraphics[width=\linewidth,height=0.42\textheight,keepaspectratio]{{figuras/{nome}}}",
                    r"\caption{" + esc(legenda) + "}"]
            if fonte:
                out.append(r"\par{\footnotesize Fonte: " + esc(fonte) + ".}")
            out.append(r"\end{figure}")
            i += 1
            continue
        if not texto:
            i += 1
            continue
        if re.match(r"^Tabela \d+ — ", texto):
            legenda_tabela = re.sub(r"^Tabela \d+ — ", "", texto)
            i += 1
            continue
        if estilo.startswith("Heading"):
            fechar_lista()
            nivel = int(estilo.split()[-1]) if estilo.split()[-1].isdigit() else 1
            tipo, nome = titulo_secao(texto)
            if texto == "Resumo":
                out += [r"\section*{Resumo}", r"\addcontentsline{toc}{section}{Resumo}"]
            elif texto.startswith(("20. Referências", "Referências")) or nome == "Referências":
                out += [r"\section{Referências}"]
            elif tipo == "apendice":
                out += [r"\appendix", r"\section{" + esc(nome) + "}"]
            else:
                out.append((r"\section{" if nivel == 1 else r"\subsection{") + esc(nome) + "}")
            i += 1
            continue
        if estilo == "List Bullet":
            if not em_lista:
                out.append(r"\begin{itemize}")
                em_lista = True
            out.append(r"\item " + esc(texto))
            i += 1
            continue
        fechar_lista()
        if texto.startswith("Palavras-chave:"):
            out.append(r"\noindent\textbf{Palavras-chave:} " + esc(texto.split(":", 1)[1].strip()))
        else:
            out.append(esc(texto).replace("\n", r"\\ "))
        out.append("")
        i += 1
    fechar_lista()
    return out, n_fig


PREAMBULO = r"""%----------------------------------------------------------------------------------------
%	PACKAGES AND OTHER DOCUMENT CONFIGURATIONS
%	Gerado por scripts/gerar_relatorio_latex.py a partir do relatório revisado (Word).
%	Adaptações do template.tex: babel em português, inputenc utf8 (utf8x está obsoleto),
%	margens ABNT, tabelas longas, figuras fixas e correção da titlepage aninhada.
%----------------------------------------------------------------------------------------

\documentclass[12pt,a4paper]{article}
\usepackage[brazilian]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{textcomp}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage[top=3cm,left=3cm,bottom=2cm,right=2cm]{geometry}
\usepackage{float}
\usepackage{array}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{indentfirst}
\usepackage[font=small,labelfont=bf]{caption}
\usepackage[hidelinks]{hyperref}
\setlength{\parskip}{0.4em}
\renewcommand{\arraystretch}{1.15}
\setlength{\LTpre}{0.3em}
\setlength{\LTpost}{0.3em}
\addto\captionsbrazilian{\renewcommand{\contentsname}{Sumário}}

\begin{document}

\begin{titlepage}

\newcommand{\HRule}{\rule{\linewidth}{0.5mm}} % Defines a new command for the horizontal lines

\center % Center everything on the page

%----------------------------------------------------------------------------------------
%	HEADING SECTIONS
%----------------------------------------------------------------------------------------

\textsc{\normalsize Universidade Estadual do Ceará}\\[1.0cm]
\textsc{\Large Programa de Pós-Graduação em Ciência da Computação}\\[0.2cm]
\textsc{\large Teste de Sistemas Inteligentes}\\[0.2cm]

%----------------------------------------------------------------------------------------
%	TITLE SECTION
%----------------------------------------------------------------------------------------

\HRule \\[0.4cm]
{ \huge \bfseries \LARGE{<<TITULO>>} \\ [1.0cm]
\emph{\large{<<SUBTITULO>>}}
}\\[0.4cm]
\HRule \\[1.0cm]

%----------------------------------------------------------------------------------------
%	AUTHOR SECTION
%----------------------------------------------------------------------------------------

\flushleft \Large \emph{Alunos:}\\
<<AUTORES>>

%----------------------------------------------------------------------------------------
%	DATE SECTION
%----------------------------------------------------------------------------------------

\center {\large <<DATA>>}\\[2cm]

%----------------------------------------------------------------------------------------
%	LOGO SECTION (opcional: coloque logo.jpg na pasta para exibi-lo)
%----------------------------------------------------------------------------------------

\IfFileExists{logo.jpg}{\includegraphics[scale = 0.3]{logo.jpg}\\[1cm]}{}

\vfill
\end{titlepage}

%---------------------------------------------------------------------------------------- FOLHA DE ROSTO

\begin{titlepage}
\vfill
\begin{center}
{\large <<AUTORES_ROSTO>>} \\[5cm]
{\Huge <<TITULO>>}\\[1cm]
\hspace{.45\textwidth}
\begin{minipage}{.5\textwidth}
Relatório acadêmico revisado apresentado à disciplina Teste de Sistemas Inteligentes do Programa de
Pós-Graduação em Ciência da Computação da Universidade Estadual do Ceará. Versão de auditoria: os valores
foram recalculados a partir das evidências originais das execuções, sem novas chamadas ao Dify ou ao Gemini.
\end{minipage}
\vfill
<<DATA>>
\end{center}
\end{titlepage}

\tableofcontents
\clearpage

"""


def gerar():
    if not ENTRADA.exists():
        raise SystemExit(f"Relatório Word não encontrado: {ENTRADA}. Rode scripts/gerar_relatorio_revisado.py.")
    doc = Document(ENTRADA)
    linhas, n_fig = corpo(doc)
    preambulo = (PREAMBULO.replace("<<TITULO>>", esc(TITULO)).replace("<<SUBTITULO>>", esc(SUBTITULO))
                 .replace("<<DATA>>", DATA).replace("<<AUTORES>>", "\\\\\n".join(AUTORES) + r"\\")
                 .replace("<<AUTORES_ROSTO>>", r" \\ [0.1cm] ".join(AUTORES)))
    texto = preambulo + "\n".join(linhas) + "\n\n\\end{document}\n"
    abre, fecha = len(re.findall(r"\\begin\{", texto)), len(re.findall(r"\\end\{", texto))
    if abre != fecha:
        raise ValueError(f"Ambientes desbalanceados: {abre} begin × {fecha} end")
    DESTINO.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(texto, encoding="utf-8")
    print(f"{SAIDA} · {n_fig} figuras · {texto.count(chr(92) + 'section{')} seções")
    return SAIDA


if __name__ == "__main__":
    sys.exit(0 if gerar() else 1)
