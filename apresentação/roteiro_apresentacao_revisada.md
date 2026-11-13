# Roteiro oral — apresentação revisada (≈ 20 minutos)

Tempos estimados por slide; ensaiar com cronômetro. Números derivados de results/exec1–exec6 por scripts/auditoria.py.

## 1. Abertura (0:40)

Apresente o objeto: não apenas um chatbot sobre o regimento do PPGCC, mas a infraestrutura que o avalia. Foram 6 execuções oficiais de 30 cenários, com 235 respostas registradas junto dos trechos recuperados. Antecipe a tese: aprovação automatizada e correção factual não são a mesma coisa, e o trabalho mostra onde divergem.

## 2. Problema e motivação (1:00)

Três dificuldades: variabilidade, duas fontes de erro e o oráculo. O CT28 da exec1 resume o problema: a resposta informou 32 créditos para o mestrado, mas citou 24 na decomposição e por isso passou no critério lexical. Esse caso orienta toda a análise: separar o veredicto automatizado da verificação factual.

## 3. Objetivos (0:40)

O objetivo geral tem duas faces: avaliar o assistente e avaliar os instrumentos. Os seis objetivos específicos correspondem às partes da infraestrutura que serão mostradas: dataset, automação, oráculo, avaliação semântica, execuções e análise.

## 4. Questões de pesquisa (0:50)

Leia as três questões. QP1 cobre factualidade e alucinação, 14 cenários; QP2 robustez e segurança, 9 cenários; QP3 contexto conversacional, 4 cenários. Desempenho fica como dimensão complementar. A antiga pergunta sobre comparar oráculos determinístico e semântico não pôde ser respondida, pela cobertura parcial do Ragas.

## 5. Sistema sob teste (0:50)

O SUT é um chatbot do Dify sobre o regimento de 2021, indexado em 47 chunks. O prompt congelado define o comportamento esperado que os testes verificam. Destaque que as inconsistências do próprio regimento foram usadas como casos de teste: CT09 e CT23.

## 6. Arquitetura (1:10)

Dois sistemas. Em cima, o SUT: Dify em contêineres no Ubuntu do WSL, base vetorial e Gemini remoto. Embaixo, a infraestrutura de avaliação: Robot para os cenários, pytest para a própria automação e Ragas depois da execução. A única interface é a API HTTP; por isso a recuperação é observada pelos trechos devolvidos, não pela consulta interna do Dify. Tudo grava em results/execN, que é consolidado sem novas chamadas.

## 7. Tecnologias (0:40)

Percorra as camadas rapidamente. Ressalte duas divergências entre protocolo e evidências: o XML registra Python 3.11.9 e o protocolo 3.12.10; o metadata da exec6 registra Docker 29.1.3 e o guia, 27.5. Não alteram os resultados, mas mostram por que registrar o ambiente por execução importa.

## 8. Dify e recuperação (1:00)

Descreva o caminho de uma pergunta. Há dois Top K no Dify: o da base, que define a busca, e o do app, que junta e reordena resultados de várias bases. A base está em Pesquisa Vetorial com Top K 3; o app, em pontuação ponderada com Top K 4. Na prática chegam 3 trechos, como em todas as 235 respostas, e a busca por palavra-chave nunca rodou. O protocolo registrava a configuração do app; foi corrigido. Importa para o CT09, que depende de recuperar dois artigos distantes.

## 9. Automação (1:00)

Camada de comportamento em BDD, camada de keywords reutilizáveis e camada de implementação em Python. O DifyClient grava cada resposta com os trechos recuperados: é esse registro que permite diagnosticar falhas de recuperação. Erros transitórios do provedor são repetidos com espera exponencial e não contaminam a latência.

## 10. Repositório e casos (0:30)

Mostre a separação de diretórios: dados, SUT, bibliotecas, keywords, testes, scripts e resultados imutáveis. O dataset tem 30 casos em seis categorias, todos conferidos no PDF.

## 11. Gerenciador (1:00)

As primeiras execuções usaram procedimentos diferentes: rebot por suíte, exclusão do smoke, script PowerShell. O gerenciador padroniza o ciclo completo em sete etapas e grava o estado de cada uma. A exec6 foi feita com ele: smoke e pytest aprovados, Robot com três reprovações, Ragas parcial e relatórios gerados. Também permite rodar cada etapa isoladamente.

## 12. Estratégia e oráculos (0:50)

Quatro níveis de teste e o que cada um prova. Testes de API não entram nos 30 cenários; isso evita comparar totais brutos diferentes entre execuções. Embaixo, os seis tipos de critério do oráculo determinístico.

## 13. Protocolo (0:50)

A calibração aconteceu antes das execuções oficiais; depois, falsos negativos foram registrados e não corrigidos. As seis execuções diferem em procedimento e ambiente: a exec4 foi no computador de outro integrante; a exec6, pelo gerenciador. Por isso falamos em variação observada, nunca em melhoria ou regressão.

## 14. Visão consolidada (0:50)

Entre 25 e 27 dos 30 cenários foram aprovados em cada execução. Os testes de API passaram sempre, mas não dizem nada sobre a qualidade das respostas. A diferença entre execuções é pequena e o desenho não permite atribuir causa a ela.

## 15. Resultados por categoria (0:40)

Factualidade 8 de 9 em todas as execuções, e a falha é sempre o CT09. Robustez e segurança 100%. Desempenho falhou só nas exec1 e exec2 pelo critério de similaridade. Conversa ficou entre 1 e 3 de 4: é a dimensão mais frágil.

## 16. Casos recorrentes (1:30)

CT09: o Art. 35 vem nos trechos em todas as execuções; o Art. 39 alínea d, nunca. O modelo responde fiel ao que recebeu e omite a contradição: falha de recuperação com consequência factual. CT28 e CT30: no primeiro turno, o trecho certo é recuperado; no turno elíptico, não. A sessão é mantida. Em CT16 e CT29, cujas continuações têm termos próprios, o contexto funciona. Isso é compatível com recuperação baseada na mensagem corrente, mas a API não mostra a consulta interna; é hipótese, não causa comprovada.

## 17. Aprovação versus correção (1:00)

Os casos da tabela foram lidos manualmente. CT28 na exec1 é falso positivo; CT21 na exec3 é falso negativo; CT18 falha por similaridade lexical com o mesmo fato; CT22 é omissão real. Endurecer o oráculo também tem custo: no CT14, citar 5,0 é correto. Por isso o veredicto automatizado precisa de avaliação semântica e de leitura humana.

## 18. Questões de pesquisa (1:20)

QP1: 75 de 84, resposta parcialmente favorável, com a contradição normativa nunca apontada e oráculo imperfeito. QP2: 54 de 54, favorável dentro do conjunto testado, sem generalização. QP3: 12 de 24, fragilidade recorrente em elipses curtas. Note que os percentuais não respondem sozinhos: a análise das evidências é que sustenta cada resposta.

## 19. Ragas (1:00)

O Ragas foi integrado, mas a cobertura é parcial: na exec6, 3 de 48 avaliações produziram valor; quase todo o resto falhou por cota do plano gratuito. A média de faithfulness usa dois valores e não deve ser interpretada. O ganho desta etapa é de engenharia: registro incremental, status e retomada para concluir a avaliação quando houver cota.

## 20. Dificuldades (1:00)

Destaque três: a troca do LLM local pelo Gemini por limitação de hardware; o tratamento de erros transitórios que o Dify repassa como HTTP 400; e a cota do juiz Ragas. Diga quais ficaram resolvidas, mitigadas ou pendentes. O relatório detalha cada uma com impacto, ação e aprendizado.

## 21. Ameaças à validade (0:40)

Construto: o oráculo verifica forma. Interna: ambiente e procedimento variaram. Externa: um documento. Conclusão: seis execuções não formam amostra estatística. Avaliador semântico com cobertura mínima. E a inspeção humana não cobriu todas as aprovações.

## 22. Conclusões (1:00)

Feche com as contribuições: a infraestrutura e o método de diagnóstico. Responda às três QPs em uma frase cada. Termine com os próximos passos, começando por concluir o Ragas e testar recuperação com histórico. Abra para perguntas.
