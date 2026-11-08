# Apostas, combos, hedge e modo advisor

Guia para transformar probabilidades em opções de aposta (em especial no Kalshi e em outros mercados de previsão) e para acompanhar as apostas ao vivo. Explique tudo em português simples: o usuário quer entender o porquê de cada número.

Regra fixa: a decisão é sempre do usuário. A skill sugere, calcula e avisa; nunca faz a aposta, nunca entra na conta do usuário e não se apresenta como consultor financeiro licenciado.

## 1. Como ler o preço no Kalshi (e mercados de previsão)

- Cada contrato paga **$1** se acertar e **$0** se errar.
- O preço em centavos é a probabilidade que o mercado dá. Contrato a **72¢** = mercado acha que a chance é 72%.
- **Preço justo** = sua probabilidade × 100. **Teto** = preço justo menos 1¢ de margem (taxa e erro de modelo).
- Só vale entrar se o preço estiver **abaixo do teto**. Acima disso está caro, mesmo que o time seja favorito.
- Se o app mostra "$20 paga $38,42", o preço pago foi 20 / 38,42 = **52¢**.
- Leia prints do app quando o usuário mandar: valor pago, quanto paga, % de cada perna e preço de cash out.

## 2. Opções de aposta (sempre oferecer)

Depois das probabilidades, entregue sempre um cardápio, do mais seguro ao mais arriscado:

1. **Apostas simples** – as 3 a 5 pernas de maior probabilidade, com "pague até X¢".
2. **Combo seguro** – 2 pernas fortes.
3. **Combo equilibrado** – 3 pernas.
4. **Combo agressivo** – 4 pernas.
5. **Combo longo** – 5 pernas (opcional).
6. **Combo misto** – esportes diferentes, quando há mercado para todas as pernas.

Para cada combo: pernas, chance de acertar tudo (produto das probabilidades), preço justo e teto em ¢, e como o combo evolui perna a perna (`model.py combo`). Use só pernas independentes (jogos diferentes) e que ainda não começaram. Deixe de fora jogos quase cara ou coroa e jogos com confiança baixa ou sem odds atuais.

Avisos que sempre acompanham o cardápio:
- Se as suas probabilidades estão perto das do mercado, **não há value**: na média o combo empata ou perde um pouco por causa da taxa. É diversão, não vantagem.
- Quanto mais pernas, maior o risco (combo de 28% perde 7 em cada 10 vezes).
- O combo fecha no início do primeiro jogo.
- Valor pequeno e fixo (ex.: 1% da banca por aposta). Nada de aumentar a aposta para recuperar perda.

## 3. Hedge (sempre explicar e planejar)

**Hedge é um seguro.** Você aposta no resultado contrário ao da sua aposta para receber dinheiro aconteça o que acontecer.

Exemplo real (combo KC + SF + SEA, pago $20, paga $38,42):
- No 4º quarto, KC e SF já garantidos, falta só o Seattle. O combo virou uma aposta simples: SEA ganha = $38,42; Cardinals ganha = $0.
- Compre **38 contratos de "Cardinals vencem"** a 20¢ = $7,60.
- SEA ganha: combo paga $38,42. Cardinals ganha: os contratos pagam $38.
- Nos dois casos recebe ~$38. Gastou $27,60. **Lucro de ~$10,80 garantido.**

A troca:
- Sem hedge: 79% de chance de +$18 e 21% de chance de −$20.
- Com hedge: 100% de chance de +$10,80.

Pontos que sempre devem ser ditos:
1. **Hedge não cria dinheiro.** O valor esperado fica quase igual (um pouco menor pela taxa); ele só tira o risco.
2. **Pode ser parcial.** Metade dos contratos garante um mínimo menor e mantém lucro maior se a perna ganhar.
3. **Timing manda no preço.** Quanto melhor a sua perna estiver no jogo, mais barato o lado contrário e maior o lucro travado. Hedge cedo é caro.
4. **Hedge antes da hora piora o risco.** Comprar o lado contrário enquanto outras pernas do combo ainda estão abertas não trava nada e aumenta a perda máxima (ex.: combo morre em outra perna e o hedge também perde).
5. Atenção a jogos no mesmo horário: se as duas últimas pernas jogam juntas, não existe o momento "só falta uma" antes do jogo; o hedge acontece ao vivo.
6. Faz sentido quando perder o valor apostado incomodaria mais do que a alegria do lucro máximo. É escolha de tranquilidade, não de matemática.

Cálculo: `model.py hedge --stake 20 --payout 38.42 --opp-price 20` (mostra hedge total e parcial e o cenário sem hedge). Monte também uma tabela de lucro travado para alguns preços do lado contrário (10¢, 20¢, 40¢).

## 4. Modo advisor ao vivo

Quando o usuário pedir para acompanhar as apostas:

1. Pergunte quais apostas ele fez e quanto pagou (ou leia o print do app).
2. Combine as 5 regras antes do jogo:
   - **Valor:** prob. ao vivo > preço de venda + 3 pp → MANTER; < preço − 3 pp → CONSIDERE SAIR; no meio → NEUTRO (escolha do usuário).
   - **Alerta vermelho:** prob. cai 20 pp+ desde a entrada, ou lesão de QB/estrela → reavaliar.
   - **Travar lucro (opcional):** perna passa de 95% ou combo fica com 1 perna → calcular hedge.
   - **Disciplina:** sem aposta nova para recuperar; limite de perda do dia definido antes.
   - **Cálculo:** placar + tempo restante + spread pré-jogo (`model.py livewp`).
3. Agende check-ins nos momentos que decidem (2º quarto, intervalo, 4º quarto, fim) e mande notificação no celular em cada um, com o sinal de cada aposta.
4. Placar ao vivo: ferramenta de dados esportivos quando disponível; senão busca na web.
5. No fim do dia: resumo de pernas ganhas e perdidas e os comandos de `ledger result` para registrar.

## 5. Mata-mata de ida e volta

Nunca use a probabilidade de vencer o jogo como chance de classificar. Use o placar agregado: `model.py aggregate --home 1.35 --away 1.15 --lead 1`. Exemplo: Palmeiras venceu a ida por 1 a 0 e joga fora → classifica ~70%, não 87%. Perder por 1 leva aos pênaltis; perder por 2+ elimina.

## 6. Lições aprendidas (não repetir)

- **Lado do palpite:** em jogos escritos "A x B" em campo neutro, confirme no mercado quem é favorito antes de registrar. Um "A" interpretado como o segundo time deu Indiana 69% quando o mercado tinha Denver -7,5.
- **Probabilidade velha:** palpites do ledger de dias antes devem ser atualizados com as odds do dia (sem margem) antes de virar aposta.
- **Divergência grande do mercado** (>10 pp): investigue antes de confiar no modelo; quase sempre o modelo esqueceu algo (agregado, lesão, rotação).
