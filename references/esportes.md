# Métricas e fontes por esporte

Leia só a seção do esporte pedido. Sempre busque a versão atual na web; as fontes abaixo são ponto de partida.

## Futebol
- **Métricas**: xG/xGA (pró e contra), chutes no alvo, posse com progressão, PPDA (pressão), gols pró/contra casa vs. fora, bola parada, pontos por jogo, forma últimos 5/10.
- **Contexto**: lesões/suspensões, calendário (jogos em 7 dias, viagens continentais), rotação, árbitro (cartões/pênaltis), clima, gramado, necessidade de pontos.
- **Modelo**: Poisson/Dixon-Coles com gols esperados ajustados por mando; Elo (clubelo.com); mercado 1X2 sem margem.
- **Fontes**: FBref, Understat, Sofascore, Transfermarkt, FotMob, Football-Data, ge/GloboEsporte e CBF (Brasil), clubelo.com.
- **Mercados úteis**: 1X2, dupla chance, over/under gols, ambos marcam, handicap asiático, escanteios/cartões.

## Basquete (NBA, NBB, Euroliga)
- **Métricas**: Net Rating, ORtg/DRtg, ritmo (pace), eFG%, TOV%, ORB%, FT rate, margem média, desempenho em back-to-back, minutos/uso das estrelas.
- **Contexto**: lesões (status do dia), descanso, viagem, load management, mando.
- **Modelo**: diferença esperada de pontos ≈ (NetRtg A − NetRtg B) × pace/100 + vantagem de mando (~2-3 pts), com desvio padrão ≈ 11-12 → prob. via normal. Spread e total vs. linha do mercado.
- **Fontes**: Basketball-Reference, NBA.com/stats, Cleaning the Glass, Dunks & Threes, Sofascore.

## NFL / futebol americano
- **Métricas**: EPA/play, success rate, DVOA, pontos pró/contra, taxa de pressão/sacks, turnover margin, red zone, tempo de posse.
- **Contexto**: QB titular, lesões em OL/secundária, clima e vento, descanso (short week), divisão, mando.
- **Modelo**: margem esperada via rating (Elo/DVOA/SRS) + mando (~2 pts), desvio padrão ≈ 13 → prob.; compare com spread.
- **Fontes**: Pro-Football-Reference, rbsdm/nflfastR, FTN/DVOA, ESPN, NFL injury report.

## Baseball (MLB)
- **Métricas**: starter (ERA, FIP, xERA, K%, BB%, últimos 5 starts), bullpen (uso recente), wRC+ do lineup vs. canhoto/destro, park factor, Pythagorean W-L.
- **Contexto**: lineup confirmado, clima/vento, descanso do bullpen.
- **Modelo**: log5 (Bill James, comando `log5`) a partir de win% ajustado (prefira o Pythagorean W-L ao real) + ajuste do arremessador titular e mando (~54%); totais por runs esperados (Poisson/negativa binomial).
- **Fontes**: Baseball Savant, FanGraphs, Baseball-Reference.

## Hóquei (NHL)
- **Métricas**: xG%, Corsi/Fenwick, PDO (regressão à média), save% do goleiro titular, power play/penalty kill.
- **Contexto**: goleiro confirmado, back-to-back, lesões.
- **Modelo**: Poisson para gols com ajuste de goleiro; mercado moneyline/puck line.
- **Fontes**: MoneyPuck, Natural Stat Trick, NHL.com, Hockey-Reference.

## Tênis (ATP/WTA)
- **Métricas**: Elo geral e **por superfície** (tennisabstract), % pontos no saque/devolução, hold/break %, aces/duplas faltas, desempenho em tiebreaks e 3º set, rendimento nas últimas 52 semanas e últimos 10 jogos.
- **Contexto**: H2H **na mesma superfície**, fadiga (minutos jogados na semana), lesões, altitude, melhor de 3 vs. 5.
- **Modelo**: Elo de superfície → prob. de vencer; derivar sets/games via probabilidade de ponto no saque (Markov: ponto → game → set → partida, comando `tennis`). Referências do circuito ATP: ~64% de pontos vencidos no saque, ~80% de holds; WTA: ~57% e ~63%. Masters 1000 e WTA Finals têm muitos jogos parelhos entre top 20: abaixo de 55% trate como moeda.
- **Fontes**: Tennis Abstract, ATP/WTA, Ultimate Tennis Statistics, Sofascore.

## MMA / UFC / boxe
- **Métricas**: SLpM, precisão e defesa de golpes, TD average/precisão/defesa, sub avg, finalização vs. decisão (% de vitórias por método), alcance/envergadura, idade, queda de queixo (derrotas por KO recentes), nível dos adversários.
- **Contexto**: corte de peso, mudança de categoria, rounds (3 vs. 5), camp, adversário substituto de última hora.
- **Modelo**: logística/Elo com estilo (wrestler vs. striker); prob. por método e por round a partir do histórico. Variância alta → confiança raramente Alta.
- **Fontes**: UFCStats, Tapology, Sherdog, FightMatrix, BoxRec (boxe).

## Fórmula 1 / MotoGP
- **Métricas**: ritmo de corrida e de classificação, posição de largada x posição final histórica no circuito, taxa de abandono, degradação de pneus, desempenho por tipo de pista, pit stops, chance de safety car (histórico do circuito).
- **Modelo**: simulação de posições a partir de ritmo relativo + variância por incidentes; pole→vitória por circuito.
- **Fontes**: Formula1.com, F1 Stats (FastF1), Racing-Reference, Motorsport Stats.

## Vôlei, handebol, rugby, críquete, eSports e outros
- Aplique a mesma estrutura: identificar as 4-6 métricas que melhor predizem resultado no esporte (eficiência por posse/ponto/set, rating, Elo) e usar Elo/logística + ajuste de mando + mercado. Se faltarem dados abertos, declare as lacunas e use confiança Baixa.
- eSports: HLTV (CS), Oracle's Elixir (LoL), Liquipedia, VLR (Valorant) - mapas/draft/patch pesam muito; H2H de elencos que mudaram vale pouco.

## Armadilhas comuns (checar sempre)
- Amostra pequena: <8 jogos num recorte → peso baixo.
- Regressão à média: time com PDO/finalização muito acima do xG tende a cair; não extrapole.
- Forma contra adversários fracos infla números → ajuste por força do calendário.
- Escalação mudou? Estatística do time "antes" pode não valer.
- Mercado muito diferente do seu modelo: investigue lesão/notícia que você não viu antes de confiar no modelo.

## Ratings e métricas de avaliação (todos os esportes)
- **Elo**: K≈20-32 (maior = reage mais rápido), vantagem de mando em pontos (futebol ~40-70), multiplicador por margem de gols/pontos para não tratar 1x0 e 5x0 igual. Escala 400 pontos = 10x de odds.
- **Pi-ratings / Massey / Colley**: alternativas que usam o placar (margem) e a força do adversário; úteis quando Elo de resultado puro é grosseiro. Se não houver rating público, derive força de ataque/defesa com `strength`.
- **Decaimento temporal**: jogos recentes pesam mais (`decay`, meia-vida 4-6 jogos no futebol; mais curta em esportes de muitos jogos como NBA/MLB).
- **Avaliação**: Brier e log loss (qualquer esporte), RPS (resultados ordenados como 1X2). Compare sempre com o chute ingênuo (Brier 0,667 em 3 resultados) e com a probabilidade do mercado sem margem.
- **Remoção de margem**: proporcional é o mais simples; potência e Shin corrigem o viés favorito/azarão (azarão pago a menos nas casas).
