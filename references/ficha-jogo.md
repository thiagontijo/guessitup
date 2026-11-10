# Ficha completa do jogo (padrão profissional)

A ficha é o coração da entrega. Ela sai **só quando o usuário liga a Guessitup e pede** (no chat, nunca por conta própria). Tudo em linguagem simples, no idioma da resposta (inglês por padrão; títulos da ficha traduzidos), dinheiro em dólar no formato do app, chance em %. O usuário lê no celular: blocos curtos, tabelas pequenas (3 a 4 colunas), sem parágrafo longo.

## Quantas fichas por pedido

- **1 a 3 jogos:** ficha completa de cada um.
- **4 ou mais jogos:** primeiro o **Quadro do dia** (uma linha por jogo: confronto · palpite · chance · nota). Depois a ficha completa dos 2 ou 3 jogos de nota A/B. No fim: "Quer a ficha completa de outro jogo? É só dizer o nome."

## Modelo da ficha (siga a ordem)

```
🏀 PISTONS x WIZARDS · 19h · Detroit · TV: Peacock
Nota B · Palpite: Pistons vencem (82%)

1) MERCADO (app do usuário)
Vencedor: Pistons 83% | Wizards 17%
Handicap: Pistons -10,5 | Total: 235,5

2) MODELO x MERCADO
| Aposta              | Modelo | App | Diferença |
| Pistons vencem      | 82%    | 83% | -1 (justo) |
| Pistons -10,5       | 47%    | 50% | -3 (evitar) |
| Menos de 235,5      | 56%    | 50% | +6 (valor)  |

3) NÚMEROS DA TEMPORADA
| Item                       | Pistons | Wizards |
| Campanha (casa/fora)       | 8-2 (5-0) | 1-9 (0-5) |
| Últimos 10                 | 8-2     | 1-9     |
| Ataque (pts/100 posses)    | 118,2   | 108,9   |
| Defesa (pts/100 posses)    | 109,5   | 120,4   |
| Saldo (net rating)         | +8,7    | -11,5   |
| Ritmo (posses/jogo)        | 99,1    | 102,3   |
| Contra o handicap          | 7-3     | 4-6     |
| Over/Under (overs)         | 4-6     | 6-4     |

4) CONTEXTO
Descanso: Pistons 1 dia | Wizards jogo em dias seguidos
Desfalques: [jogador · status · impacto em pontos]
Confronto direto (últimos 5): 4-1 Pistons, margem média +9

5) SIMULAÇÃO (10.000 jogos)
Placar médio: Pistons 120 x 109 Wizards
Pistons vencem por 16+: 31% | por 1 a 5: 14%
Total entre 220 e 246 em metade dos jogos

6) A FAVOR / CONTRA
✅ 3 fatos com número que sustentam o palpite
⚠️ 2 ou 3 fatos com número que vão contra

7) VEREDITO
Melhor aposta: Menos de 235,5 (56%, nota B). Aposta $10, recebe ~$19,6 no Kalshi a 51%.
Alternativa: Pistons no combo (perna segura)
Evitar: Pistons -10,5 (cara)
🛡️ Hedge: [quando e quanto, se o botão de proteção estiver ligado]
```

## Campos por esporte (bloco 3)

| Esporte | Linhas obrigatórias da tabela |
|---|---|
| NBA | campanha casa/fora, últimos 10, ataque, defesa, saldo por 100 posses, ritmo, contra o handicap, over/under; extra: % de 3 pontos, rebotes ofensivos, turnovers |
| NFL | campanha, pontos a favor/contra por jogo, jardas por jogada (ataque e defesa), EPA por jogada se achar, saldo de turnovers, % 3ª descida, red zone, sacks; contra o handicap e over/under |
| Futebol | posição, pontos, gols pró/contra, xG pró/contra, casa/fora, últimos 5, % ambos marcam, % over 2,5, escanteios e cartões por jogo |
| NHL | campanha, gols pró/contra por jogo, chutes, power play % e penalty kill %, goleiro titular (% de defesas, GAA), casa/fora |
| MLB | arremessadores titulares (ERA, FIP, WHIP, K/9 na temporada e últimos 3 jogos), corridas por jogo, OPS do time, bullpen ERA, parque |
| Tênis/MMA | ranking, forma, superfície/estilo, estatísticas de saque/golpe, H2H; sem tabela de time |

Campo não encontrado → escreva "não consta". Nunca invente número. Cada bloco de números leva a fonte e a data numa linha curta embaixo (ex.: "Fonte: Basketball-Reference, 09/11").

## Como chegar nos números

1. **Mercado:** linhas do app do usuário (print) ou site de odds do dia. Confira a data.
2. **Estatísticas:** Basketball-Reference / NBA.com (ataque, defesa, ritmo), TeamRankings ou Covers (contra o handicap, over/under), Pro-Football-Reference / rbsdm (EPA), FBref / Understat / FotMob (xG), NHL.com / Natural Stat Trick, Baseball Savant / FanGraphs. Relatório de lesões oficial da liga.
3. **Placar esperado:** `model.py expected` (NBA/NFL) ou `strength` + `poisson` (futebol/NHL).
4. **Simulação:** `model.py sim` com as linhas do mercado + placar do modelo (mistura 2:1 automática).
5. **Nota:** `model.py grade --prob --app-pct --divergence --data --games [--key-injury-doubt]`.
   - A = aposta forte · B = boa aposta · C = leve ou só em combo · D = evitar.
   - `--data` = fração dos campos da tabela que você achou (ex.: 7 de 8 = 0.875).

## Regras de honestidade

- Tendências ("ganhou 7 dos últimos 10 contra o handicap") são contexto, não prova: amostra pequena. Só entram na lista A FAVOR/CONTRA se o número de jogos for mostrado.
- Se o modelo e o mercado divergem mais de 10 pontos, diga isso e explique a causa provável (lesão nova, linha velha, erro de dado) antes de chamar de valor.
- Nota A exige vantagem de 6 pontos ou mais, dados completos e nenhuma dúvida de lesão importante. Na dúvida, rebaixe.
