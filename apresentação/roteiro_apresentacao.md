# Roteiro oral — 15 minutos

Duração anotada é estimativa. Ensaio com cronômetro continua necessário.

## 1. Avaliação automatizada da qualidade de um sistema RAG (0:45)

Abra pelo escopo: um assistente RAG sobre o regimento do PPGCC, avaliado com Robot Framework. Foram conduzidas quatro execuções oficiais de 30 casos cada. O trabalho mede comportamento observado nos critérios e documentos disponíveis; não certifica o sistema nem apresenta métricas Ragas.

## 2. Motivação e problema do oráculo (1:00)

O exemplo CT28 da primeira execução mostra a limitação de um critério lexical: a resposta passou porque mencionava 24 na decomposição, embora informasse total incorreto de 32 créditos. Esse caso motivou separar resultado automatizado de julgamento factual. Não recalibramos o histórico depois de observar as execuções.

## 3. Questões de pesquisa consolidadas (1:30)

QP1: Em que medida o assistente RAG apresenta respostas corretas e fundamentadas no regulamento do PPGCC? QP2: Como o assistente RAG se comporta diante de entradas ambíguas, contraditórias ou potencialmente maliciosas? QP3: Em que medida o assistente RAG preserva o contexto e a coerência das respostas em interações com múltiplos turnos? A latência é complementar. Como Ragas não foi executado, não há comparação empírica entre oráculos semântico e determinístico.

## 4. Sistema sob teste (1:00)

Apresente o fluxo observado: pergunta, trechos recuperados pelo Dify, resposta do Gemini e registros locais. O protocolo documenta Dify 1.18.0, Gemini flash-lite, embeddings Gemini e busca híbrida Top K quatro. Esses são valores declarados, não snapshots completos de cada execução. Contextos no JSONL não mostram a consulta interna.

## 5. Desenho experimental e cobertura (1:15)

A suíte contém 30 casos experimentais: nove factuais, cinco de alucinação, cinco robustos, quatro de segurança, quatro conversacionais e três de desempenho. Execuções 1 a 3 também têm quatro testes de API, incluindo smoke; execução 4 tem três. Por isso comparamos sempre os 30 cenários, não totais brutos diferentes.

## 6. BDD e limites do oráculo (1:15)

As suítes expressam Given, When e Then; keywords compartilhadas chamam o cliente e o avaliador Python. Os critérios cobrem termos, ausência, citação, latência e similaridade. Um PASS significa que o critério passou; não demonstra todas as relações factuais. Ragas está implementado, mas não foi executado e não gerou métricas.

## 7. QP1 — Qualidade das respostas (1:30)

A factualidade passou em oito de nove casos em cada execução. Alucinação passou em quatro de cinco, cinco de cinco, quatro de cinco e quatro de cinco. CT09 falhou em todas; CT22, na primeira e quarta. O quadro não esgota a qualidade: CT28 da primeira execução passou apesar do total incorreto, e CT21 da terceira rejeitou uma recusa adequada. Assim, a resposta à QP1 é parcial e limitada pelos oráculos lexicais.

## 8. QP2 — Robustez e segurança (1:00)

Robustez teve cinco de cinco aprovações e segurança quatro de quatro em cada execução. Isso sustenta a conclusão de que os casos selecionados passaram os critérios determinísticos. Não equivale a uma avaliação ampla de segurança, nem permite afirmar que não existam vulnerabilidades ou comportamento adversarial não coberto.

## 9. QP3 — Consistência conversacional (1:30)

A categoria passou em três de quatro casos na primeira execução, dois de quatro na segunda e terceira, e um de quatro na quarta. CT30 falhou em todas; CT28 em execuções posteriores; CT29 na quarta. CT28/exec1 passou com total errado. Contextos observáveis sustentam hipótese de recuperação insuficiente em perguntas elípticas, mas não provam o caminho interno da busca no Dify.

## 10. Desempenho como dimensão complementar (1:15)

O desempenho teve dois de três, dois de três, três de três e três de três aprovações. As médias JSONL variaram, e a quarta execução teve uma máxima maior; são estatísticas descritivas das respostas registradas. Pausas e chamadas sem registro ficam fora. Como ambiente e ordem variaram, não inferimos regressão de modelo.

## 11. Limitações e validade (1:30)

Quatro limites devem acompanhar a leitura: oráculos lexicais podem aceitar erro e rejeitar recusa válida; Ragas não foi executado; o experimento usa um documento e não tem snapshot remoto completo; diferenças de totais não isolam causa. São resultados observados no desenho usado, não estimativas universais do comportamento de sistemas RAG.

## 12. Conclusões (1:30)

Responda diretamente: QP1, evidência parcialmente favorável mas limitada por erros e oráculos; QP2, os casos de robustez e segurança passaram sem garantia geral; QP3, conversas multi-turno tiveram dificuldades recorrentes. A contribuição é a rastreabilidade e a análise crítica dos critérios. O estudo futuro pode testar recuperação contextual e avaliação semântica com ambiente congelado. Ensaie com cronômetro.
