# guessitup

Skill para o [Claude Code](https://claude.com/claude-code) que gera **palpites esportivos baseados em estatística**, em qualquer esporte: futebol, NBA, NFL, MLB, NHL, tênis, MMA/UFC, F1, vôlei, eSports e outros.

Para cada jogo ou luta, a skill busca dados atuais na web e monta um dossiê com:

- campanha em cinco janelas: carreira, temporada, último mês, últimos 5 jogos e situação do jogo (mando, superfície, descanso);
- confronto direto, com peso proporcional à amostra;
- desfalques e contexto;
- probabilidades calculadas para os dois lados (Poisson/Dixon-Coles, Elo, distribuição normal para esportes de pontos), comparadas com o mercado sem margem;
- palpite com nível de confiança, "odd justa", o que mudaria o palpite e lacunas de dados;
- resumo final com todos os palpites ordenados por confiança;
- opções de aposta e combos (seguro, equilibrado, arriscado) dizendo em dólar quanto o app precisa pagar para valer a pena (Kalshi e apps parecidos);
- plano de proteção (hedge) em dólar: quanto apostar no lado contrário e quanto lucro fica garantido;
- modo advisor ao vivo: acompanha as apostas e avisa "manter" ou "considere sair" com base em estatística (a decisão é sempre sua).

A skill sempre pergunta antes quais sugestões você quer (esportes, jogos de hoje ou da semana, combos, acompanhamento ao vivo).

> São probabilidades, não garantias. Nenhum modelo garante resultado, e apostar envolve risco.

## Instalação

Requer Claude Code e Python 3 (só biblioteca padrão).

```bash
git clone https://github.com/thiagontijo/guessitup ~/.claude/skills/guessitup
```

Abra o Claude Code e peça, por exemplo:

- `/guessitup jogos do Brasileirão deste fim de semana`
- "quem leva Palmeiras x Flamengo? quero as chances dos dois lados"
- "palpites do card do UFC de sábado"

## Estrutura

```
guessitup/
├── SKILL.md                 instruções da skill (fluxo, regras, formato do relatório)
├── references/esportes.md   métricas, fontes e modelo indicado por esporte
├── references/apostas.md    Kalshi, combos, hedge, modo advisor e lições aprendidas
└── scripts/model.py         ferramentas numéricas (só biblioteca padrão)
```

### `scripts/model.py`

| Comando | O que faz |
|---|---|
| `poisson --home 1.6 --away 1.1` | gols esperados → 1X2, dupla chance, empate anula, over/under, ambos marcam, placares (com correção Dixon-Coles) |
| `decay --values ... --half-life 5` | média com decaimento temporal (jogo recente pesa mais) |
| `strength --gf --ga --league-gf` | forças de ataque e defesa relativas à liga |
| `elo --a --b --adv --draw` | probabilidades por Elo (com conversão para 1X2) |
| `elo-update` | atualiza Elo após um resultado, com multiplicador por margem |
| `devig --odds ...` | remove a margem da casa: proporcional, potência e Shin |
| `normal --diff --sd --line` | esportes de pontos: chance de vencer e de cobrir spread |
| `blend --probs --weights` | combina modelos e mede a divergência |
| `value --prob --odds` | valor esperado e Kelly fracionado (0,25x, teto de 5%) |
| `clv --taken --closing` | closing line value |
| `combo --probs ... --stake --pays` | chance do combo e pagamento mínimo em dólar para valer a pena |
| `hedge --stake --payout --opp-pct` | proteção total e pela metade: quanto apostar no lado contrário e lucro garantido |
| `livewp --lead --minutes-left --spread --app-pct` | chance ao vivo (NFL/NBA) e sinal MANTER / CONSIDERE SAIR |
| `aggregate --home --away --lead` | mata-mata de ida e volta: chance de classificar pelo placar agregado |
| `ledger add/result/report` | registro de palpites e calibração: Brier, log loss, RPS, acerto por faixa, ROI, CLV |

O ledger fica em `ledger/predictions.jsonl` (fora do git). Registre os palpites, informe os resultados depois e rode `ledger report` para ver se as porcentagens se confirmam. Com menos de ~30 palpites, nada é conclusivo.

## Fontes e inspiração

Técnicas reescritas do zero, inspiradas em projetos abertos: [penaltyblog](https://github.com/martineastwood/penaltyblog) (modelos de gols, ratings, métricas), [Kairos](https://github.com/m1r4g3-code/kairos) (ledger, CLV, Kelly com teto, ancoragem no mercado) e [GoallineIQ](https://github.com/gmalbert/world-cup) (Elo + Poisson).

## Licença

MIT
