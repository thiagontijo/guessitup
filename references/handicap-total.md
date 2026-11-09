# Handicap (spread) e Over/Under — simulação de 10.000 jogos

Leia antes de entregar qualquer aposta de handicap ou de total. Ferramenta: `model.py sim`.

## O que é cada aposta (explique assim para o usuário)

- **Handicap (spread):** o time precisa ganhar por mais que a linha. "Pistons -10,5" = os Pistons precisam ganhar por 11 ou mais. "Wizards +10,5" = os Wizards ganham a aposta se vencerem ou perderem por até 10.
- **Over/Under (total):** soma dos pontos/gols dos dois times. "Mais de 228,5" ganha se o jogo terminar com 229 ou mais.
- **Linha inteira (ex.: -3, 45):** se cair exatamente na linha, o app devolve o dinheiro (push). Linha com ,5 nunca empata.
- No Kalshi aparece como chance em % ("Pistons ganham por mais de 10,5: 48%"). Nos apps de sportsbook aparece como odd americana (normalmente -110 para os dois lados).

## Passo a passo

1. **Pegue as linhas do mercado** (handicap e total) do app do usuário ou de um site de odds do dia (Covers, Action Network, ESPN, DraftKings/FanDuel research). Confira a data: páginas de anos anteriores aparecem muito nas buscas. Sem linha do dia, diga "linha não encontrada" e peça o print do app.
2. **Monte o placar esperado do modelo** (pontos de cada time):
   - **NBA:** posses esperadas = média do ritmo (pace) dos dois times. Pontos do time A = posses × (ataque de A por 100 posses × defesa de B por 100 posses ÷ média da liga) ÷ 100. Ajustes rotulados: mando de quadra +2 na margem; jogo em dias seguidos (back-to-back) -2 a -3 para o time cansado; desfalque de titular: use o impacto do jogador (on/off, net rating) e diga o número usado.
   - **NFL:** pontos por campanha / EPA por jogada de ataque e defesa, mando +1,5, clima (vento forte e chuva derrubam o total), desfalque de quarterback (3 a 7 pontos).
   - **Futebol / NHL / MLB:** gols (ou corridas) esperados de cada time pelo método de força de ataque × defesa (`model.py strength` + `poisson`). Use esses números em `--home` e `--away`.
3. **Simule:**
   ```bash
   # NBA/NFL: linhas do mercado + placar do modelo (mistura 2:1 mercado:modelo automática)
   python3 scripts/model.py sim --sport nba --market-spread -10.5 --market-total 230.5 \
       --home 121 --away 108 --home-name Pistons --away-name Wizards \
       --spread -10.5 -7.5 --total 226.5 230.5 234.5
   # Futebol/NHL/MLB: só os gols esperados
   python3 scripts/model.py sim --sport soccer --home 1.6 --away 1.0 --home-name Flamengo --away-name Bahia \
       --spread -0.5 -1.5 --total 1.5 2.5 3.5
   ```
   `--market-spread` é a linha do **mandante** (negativo = mandante favorito). Avalie a linha principal e 1 ou 2 linhas alternativas de cada lado.
4. **Entregue em tabela** (uma linha por aposta): aposta · chance · preço justo no app do usuário · "só vale se" · veredito. Só marque como boa aposta quando a chance passa o preço do app por **3 pontos ou mais**. Abaixo disso, "preço justo, sem vantagem".
5. **Mostre a distribuição** (1 ou 2 linhas): "Warriors vencem por 16+ em 30% dos jogos; por 1 a 5 em 16%". Isso explica por que um handicap alto é arriscado mesmo com favorito forte.

## Desvio padrão usado (já embutido no `sim`)

| Esporte | Margem | Total | Observação |
|---|---|---|---|
| NBA | 12 | 18 | |
| NFL | 13,5 | 10 | números-chave: muitos jogos terminam por 3 ou 7; linhas -3 e -7 têm push frequente, e sair de -3,5 para -2,5 vale muito |
| NCAAB | 11 | 16 | |
| NCAAF | 16 | 14 | |
| Futebol, NHL, MLB | Poisson | Poisson | NHL: empate no tempo normal vai para prorrogação/pênaltis; MLB tem mais variação que Poisson, então rebaixe a confiança |

Use `--sd-margin` / `--sd-total` só com motivo declarado (ex.: time com ritmo muito irregular).

## Cuidados

- **Combo com handicap do mesmo jogo:** "Pistons vencem" e "Pistons -10,5" estão ligados (se o segundo acontece, o primeiro já aconteceu). Nunca multiplique as chances. Combo de handicap e total de jogos **diferentes** pode ser multiplicado (`combo`).
- **Favorito forte + handicap alto:** a chance de vencer é alta, mas a de cobrir costuma ficar perto de 50%. Muitas vezes o vencedor simples ou um handicap menor é melhor.
- **Total e ritmo:** desfalque de armador ou de pivô muda o ritmo; jogo decidido cedo (lavada) tende a ter final mais lento.
- **Hedge:** o plano de proteção funciona igual. A chance ao vivo de cobrir o handicap é a mesma conta do `livewp`, usando `--lead` = vantagem atual menos a linha.
