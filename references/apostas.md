# Apostas, combos, proteção (hedge) e modo advisor

Guia para transformar probabilidades em opções de aposta em qualquer app (Hard Rock, FanDuel, DraftKings, BetMGM, Caesars, Fanatics, bet365, Kalshi, Polymarket, Betano etc.) e para acompanhar as apostas ao vivo.

## Como falar com o usuário (obrigatório)

- **Linguagem simples e direta.** Frases curtas, sem jargão.
- **Valores sempre em dólar**, no formato que o app mostra: em inglês "bet $20, get back $38.42", em português "aposta $20, recebe $38,42", em espanhol "apuesta $20, cobras $38.42". Nunca fale em centavos.
- **Idioma:** inglês por padrão; português ou espanhol (ou outro) quando o usuário pedir ou escrever nele (regra "Idioma" do SKILL.md).
- **Não use a palavra "contrato"** (nem "contract" em inglês, nem "contrato" em espanhol). Fale "aposta"/"bet"/"apuesta", "aposta de proteção"/"hedge bet"/"apuesta de cobertura", "o lado contrário"/"the other side"/"el otro lado".
- **Use o formato de odd do app do usuário** (americana, decimal ou %), sempre com o valor em dólar ao lado ("aposta $10, recebe $12,50").
- "Hedge" pode aparecer, mas sempre explicado como **proteção** ou **seguro**.

Regra fixa: a decisão é sempre do usuário. A skill sugere, calcula e avisa; nunca faz a aposta, nunca entra na conta do usuário e não se apresenta como consultor financeiro licenciado.


## Menu de botões (sempre no início)

Chame AskUserQuestion uma vez, com as 4 perguntas abaixo (pule a que já foi respondida na conversa):

| # | header | Pergunta | Opções (label · description) |
|---|--------|----------|------------------------------|
| 1 | App | Em qual app você vai apostar? | Kalshi · chance em % ("Sim a 72%") / Hard Rock · odds americanas e parlay / FanDuel · odds americanas / DraftKings · odds americanas |
| 2 | Aposta | Que tipo de aposta você quer? | Palpite simples · um jogo por aposta / Combo · vários jogos juntos, paga mais / Os dois · simples + combos |
| 3 | Hedge | Quer ativar a proteção (hedge)? | Ativar proteção · plano de seguro em dólar + aviso ao vivo no celular / Sem proteção · só os palpites |
| 4 | Mercados (multiSelect) | Quais tipos de aposta você quer ver? | Vencedor · quem ganha / Handicap · ganha por X pontos / Over/Under · total de pontos ou gols |

Regras:
- A opção recomendada vem primeiro e com "(Recomendado)" no fim: no App, o app que o usuário usou da última vez; no Hedge, "Ativar proteção" quando houver combo.
- Cada pergunta deve fazer sentido sozinha (o usuário pode ver só o diálogo).
- Entregue só o que foi escolhido. Com hedge ativado, agende check-ins ao vivo (send_later) e mande notificação no celular em cada alerta.

## 0. Qual app? (perguntar sempre)

Antes das opções, pergunte em qual app o usuário vai apostar (se ele ainda não disse na conversa). Tudo é montado no formato desse app, e depois comparado com os outros.

| Tipo de app | Exemplos | Como mostra a odd | Como explicar |
|---|---|---|---|
| Casa americana | Hard Rock, FanDuel, DraftKings, BetMGM, Caesars, Fanatics, ESPN Bet | americana: −400 / +150 | negativa: mais perto de zero paga mais; positiva: maior paga mais |
| Casa com odd decimal | bet365, Betano, Superbet, Pinnacle | decimal: 1,25 / 2,50 | maior paga mais; aposta $10 × odd = quanto recebe |
| App de previsão | Kalshi, Polymarket, Novig | % de chance (ou preço por $1) | % menor = paga mais; aposta $10 ÷ % = quanto recebe |

Nomes: combo = "parlay" (casas americanas) = "múltipla" (casas brasileiras). Cash out existe na maioria dos apps.

**Comparação obrigatória:** para cada aposta simples e combo, mostre
1. a **odd mínima no app do usuário** (`model.py odds --prob 0.69`);
2. **onde paga mais**, quando houver odds de outros apps (`model.py compare --apps HardRock=-210 FanDuel=-190 Kalshi=68% --prob 0.69`). Boas fontes de odds de vários apps juntos: VegasInsider (tabela por casa), Covers, Action Network, OddsShark, FanDuel Research; para futebol, sites de comparação de odds.
3. Se outro app paga mais pela mesma aposta, diga em dólar quanto a mais ("na FanDuel a mesma aposta paga $0,50 a mais por $10").

Avise que nem todo app existe em todo estado ou país e que os mercados (ex.: combos de esportes diferentes, classificação em mata-mata) variam de app para app.

### Usuário no Brasil (regra obrigatória)

Desde **25/09/2026**, a Medida Provisória nº 1.394/2026 proíbe a exploração, a oferta, a intermediação e a publicidade de apostas de quota fixa (esportivas e cassino online) no Brasil, inclusive por empresas do exterior que atendam pessoas no Brasil. Os sites e apps brasileiros saíram do ar em outubro. A MP precisa ser votada pelo Congresso (prazo inicial 23/11/2026, prorrogável por 60 dias) e há ações no STF, então isso pode mudar.

Quando o usuário disser que está no Brasil, citar uma casa brasileira (Betano, Superbet, KTO, Sportingbet, EstrelaBet, Betnacional etc.) ou pedir valores em reais:
1. Diga em uma ou duas frases, sem sermão, que as apostas esportivas estão proibidas no Brasil desde 25/09/2026 pela MP 1.394/2026 e que a situação pode mudar com a votação no Congresso.
2. **Não monte apostas, combos, hedge nem comparação de preços em casas brasileiras** e não indique sites ou apps para apostar a partir do Brasil.
3. Continue entregando a análise: probabilidades, ficha do jogo, nota A–D e o porquê dos números. Isso é estatística esportiva, não aposta.
4. Os bots Chico, Arnaldo e Herman podem rodar normalmente: eles usam dinheiro de mentira e não fazem apostas.
5. Antes de afirmar a situação, confira na web se a MP ainda está em vigor (pode ter sido aprovada, alterada ou ter perdido a validade). Se as apostas esportivas voltarem a ser permitidas, só cite casas da lista oficial da Secretaria de Prêmios e Apostas (domínio .bet.br).

## 1. Como saber se o preço do app está bom

- O app mostra a chance de cada resultado em % e quanto você recebe se ganhar ("$20 paga $38,42").
- **Pagamento justo** = valor apostado ÷ chance. Ex.: chance de 51%, aposta de $20 → justo é receber $39.
- Só vale a pena se o app pagar **pelo menos o pagamento mínimo** que a skill calcula (o justo mais uma pequena margem).
- Se o app paga menos que isso, está **caro**, mesmo que o time seja favorito.
- Sempre dê o exemplo com um valor redondo: "apostando $10, o app tem que pagar pelo menos $X".
- Leia prints do app quando o usuário mandar: quanto apostou, quanto recebe, % de cada perna e o valor de cash out.

Cálculo: `model.py combo --probs 0.81 0.80 0.79 --stake 20 --pays 38.42`. Para converter qualquer odd (−213, 1,47 ou 68%) para dólar: `model.py odds --odd -213`.

## 2. Opções de aposta (sempre oferecer)

Depois das probabilidades, entregue um cardápio, do mais seguro ao mais arriscado:

1. **Apostas simples**: as 3 a 5 mais fortes, com a odd mínima no app do usuário e "apostando $10, precisa receber pelo menos $X".
2. **Combo seguro**: 2 pernas fortes.
3. **Combo equilibrado**: 3 pernas.
4. **Combo arriscado**: 4 pernas.
5. **Combo longo**: 5 pernas (opcional).
6. **Combo misto**: esportes diferentes, quando o app tiver todos.

Para cada combo: as pernas, a chance de acertar tudo, a odd mínima no app do usuário, onde paga mais entre os apps, quanto o app precisa pagar para valer a pena e como a chance sobe conforme as pernas vão acertando. Use só jogos diferentes e que ainda não começaram. Deixe de fora jogos quase cara ou coroa, jogos com confiança baixa e jogos sem odds do dia.

Avisos que sempre acompanham o cardápio:
- Se as suas chances estão perto das do app, **não há vantagem**: na média você empata ou perde um pouco por causa da taxa. É diversão, não investimento.
- Quanto mais pernas, maior o risco (um combo de 28% perde 7 em cada 10 vezes).
- O combo fecha quando começa o primeiro jogo.
- Valor pequeno e sempre igual (ex.: 1% do saldo por aposta). Nada de aumentar a aposta para recuperar perda.

## 3. Proteção (hedge): sempre explicar e planejar

**A proteção é um seguro.** Você faz uma aposta no lado contrário para receber dinheiro aconteça o que acontecer.

Exemplo real (combo Chiefs + 49ers + Seahawks: apostou $20, recebe $38,42):
- No 4º quarto, Chiefs e 49ers já garantidos, falta só o Seattle. Agora é tudo ou nada: Seattle ganha, você recebe $38,42; Cardinals ganha, você recebe $0.
- O app mostra Cardinals com 20% de chance. Você aposta **$7,68 no Cardinals**, e essa aposta paga **$38,42** se o Cardinals ganhar.
- Seattle ganha: o combo paga $38,42. Cardinals ganha: a proteção paga $38,42.
- Nos dois casos você recebe $38,42. Gastou $27,68. **Lucro de ~$10,74 garantido.**

A troca:
- Sem proteção: 80% de chance de ganhar $18 e 20% de chance de perder $20.
- Com proteção: 100% de chance de ganhar ~$10,74.

Sempre diga também:
1. **A proteção não cria dinheiro.** Na média dá quase o mesmo (um pouco menos por causa da taxa); ela só tira o risco.
2. **Pode ser pela metade.** Proteção menor garante menos, mas deixa um lucro maior se você ganhar (ex.: $3,84 no Cardinals → +$14,58 se Seattle ganhar, −$4,63 se Cardinals ganhar).
3. **A hora certa muda tudo.** Quanto melhor a sua aposta estiver no jogo, mais barata a proteção e maior o lucro garantido. Proteger cedo sai caro.
4. **Proteger antes da hora piora.** Se ainda faltam outras pernas do combo, a proteção não garante nada e aumenta a perda máxima.
5. **Jogos no mesmo horário:** se as duas últimas pernas jogam juntas, a proteção acontece com os jogos rolando.
6. Faz sentido quando perder o valor apostado incomodaria mais do que a alegria do lucro máximo. É escolha de tranquilidade, não de matemática.

Sempre mostre uma tabela simples:

| O app mostra o lado contrário com | Aposta de proteção | Lucro garantido |
|---|---|---|
| 10% | $3,84 | ~$14,58 |
| 20% | $7,68 | ~$10,74 |
| 40% | $15,37 | ~$3,05 |

Cálculo: `model.py hedge --stake 20 --payout 38.42 --opp-pct 20` (mostra proteção total, pela metade e o cenário sem proteção). Em casa com odd americana ou decimal, converta a odd do lado contrário para % com `model.py odds --odd +400` (+400 = 20%), ou faça direto: **quanto apostar = quanto o seu combo paga ÷ odd decimal do lado contrário** (ex.: combo paga $14,70, Milwaukee +400 = 5,00 → aposte $2,94).

A proteção pode ser feita **em outro app** que pague mais pelo lado contrário. Compare também com o **Cash Out** do app: diga em dólar qual das duas opções deixa mais dinheiro garantido.

## 4. Modo advisor ao vivo

Quando o usuário pedir para acompanhar as apostas:

1. Pergunte o que ele apostou: quanto apostou e quanto recebe (ou leia o print do app).
2. Combine as 5 regras antes do jogo:
   - **Valor:** se a minha chance ao vivo está mais de 3 pontos acima do % do app → MANTER; mais de 3 pontos abaixo → CONSIDERE SAIR (cash out); no meio → TANTO FAZ (escolha dele).
   - **Alerta vermelho:** a chance cai 20 pontos ou mais desde a aposta, ou o QB/estrela se machuca → reavaliar.
   - **Garantir lucro (opcional):** a perna passa de 95% ou o combo fica com 1 perna → calcular a proteção.
   - **Disciplina:** nada de aposta nova para recuperar; limite de perda do dia definido antes.
   - **Cálculo:** placar + tempo restante + favoritismo de antes do jogo (`model.py livewp ... --app-pct 75`).
3. Agende check-ins nos momentos que decidem (2º quarto, intervalo, 4º quarto, fim) e mande notificação no celular em cada um, com o sinal de cada aposta em dólar.
4. Placar ao vivo: ferramenta de dados esportivos quando houver; senão, busca na web.
5. No fim do dia: resumo do que ganhou e perdeu em dólar e os comandos de `ledger result`.

## 5. Mata-mata de ida e volta

Nunca use a chance de vencer o jogo como chance de classificar. Use o placar somado das duas partidas: `model.py aggregate --home 1.35 --away 1.15 --lead 1`. Ex.: Palmeiras venceu a ida por 1 a 0 e joga fora → classifica ~70%, não 87%. Perder por 1 leva aos pênaltis; perder por 2 ou mais elimina.

## 6. Lições aprendidas (não repetir)

- **Lado do palpite:** em jogos "A x B" em campo neutro, confirme no mercado quem é favorito antes de registrar. Um "A" lido como o segundo time deu Indiana 69% quando o mercado tinha Denver favorito por 7,5 pontos.
- **Chance velha:** palpites do ledger de dias antes precisam ser atualizados com as odds do dia antes de virar aposta.
- **Diferença grande para o mercado** (mais de 10 pontos): investigue antes de confiar no modelo; quase sempre o modelo esqueceu algo (placar da ida, lesão, time reserva).
- **Taxa do app entra no "só vale se"** (09/11): o Under 45,5 a 50% no Kalshi pagava $18,95 e não $20. Calcule o preço mínimo já com a taxa: a vantagem de 3 pontos tem que sobrar depois dela.

### Autocrítica do fim de semana 7-9/11 (regras novas)

Resultado: vencedores muito bons (favoritos de 50%+ no futebol europeu 6/6; NBA segunda 5/6; NFL domingo favoritos quase todos), mas handicap e Over erraram.

1. **Handicap: siga o mercado, não o azarão.** Errei os 3 contra o favorito (Bills -3,5 venceu por 17; Warriors -9 venceu por 51; Vikings +3,5 perdeu). O modelo de pontos puxava para o azarão. Regra: no handicap use mistura **3:1 mercado:modelo** (não 2:1) e nunca marque nota acima de C contra o favorito quando o azarão tem contexto ruim (jogo em dias seguidos, quarterback reserva, 3+ desfalques) — esse contexto aumenta a chance de lavada, não de jogo apertado.
2. **NFL: não use só pontos feitos/sofridos.** O placar esperado por pontos deu os Vikings favoritos e errou. Use EPA por jogada/SRS (ajusta força do adversário) e só use pontos como conferência.
3. **Over está superestimado.** Overs 3/8, Unders 4/4. Antes de recomendar Over: reduza o total esperado do modelo em ~5% (futebol: λ × 0,95) e exija vantagem de **5 pontos** (Under continua com 3). NBA: se um time pode abrir lavada (favorito de 9+ contra time cansado/desfalcado), rebaixe o Over um nível — os titulares saem cedo e o ritmo cai.
4. **Empate no futebol.** 4 de 22 jogos empataram e o modelo nunca escolhe empate. Quando as chances de mandante e visitante estão a menos de 6 pontos uma da outra, não dê palpite seco: ofereça **dupla chance** ou "sem aposta".
5. **Excesso de confiança em mata-mata.** Palmeiras saiu a 87% antes de usar o placar somado (real ~70%; passou nos pênaltis). Mata-mata sempre por `aggregate`.
6. **Dados faltando = nota cai, e diga quais.** Warriors x Pelicans saiu com ratings estimados por pontos por jogo; o Over 232,5 perdeu (225).
