# guessitup

[English](README.md) · **Português** · [Español](README.es.md)

**[⬇️ Baixar a skill (ZIP)](https://github.com/thiagontijo/guessitup/archive/refs/heads/main.zip)** · **[🎮 Ver os bots ao vivo: Guessitup Arena](https://thiagontijo.github.io/guessitup/)**

Skill para o Claude ([app](https://claude.ai) e [Claude Code](https://claude.com/claude-code)) que gera **palpites esportivos baseados em estatística**, em qualquer esporte: futebol, NBA, NFL, MLB, NHL, tênis, MMA/UFC, F1, vôlei, eSports e outros.

Para cada jogo ou luta, a skill busca dados atuais na web e monta um dossiê com:

- campanha em cinco janelas: carreira, temporada, último mês, últimos 5 jogos e situação do jogo (mando, superfície, descanso);
- confronto direto, com peso proporcional à amostra;
- desfalques e contexto;
- probabilidades calculadas para os dois lados (Poisson/Dixon-Coles, Elo, distribuição normal para esportes de pontos), comparadas com o mercado sem margem;
- palpite com nível de confiança, "odd justa", o que mudaria o palpite e lacunas de dados;
- resumo final com todos os palpites ordenados por confiança;
- opções de aposta e combos (seguro, equilibrado, arriscado) no app que você escolher (Hard Rock, FanDuel, DraftKings, bet365, Kalshi, Betano...), com a odd mínima em dólar e a comparação de qual app paga mais;
- plano de proteção (hedge) em dólar: quanto apostar no lado contrário e quanto lucro fica garantido;
- modo advisor ao vivo: acompanha as apostas e avisa "manter" ou "considere sair" com base em estatística (a decisão é sempre sua).

A skill sempre abre um menu de botões: **App** (Kalshi, Hard Rock, FanDuel, DraftKings ou outro), **Tipo de aposta** (palpite simples, combo ou os dois), **Proteção hedge** (ativar ou não) e **Mercados** (vencedor, handicap, over/under, com simulação de 10.000 jogos). Cada jogo sai numa **ficha completa**: números da temporada, contexto, simulação e nota de confiança A-D. Com a proteção ativada, ela monta o plano de hedge e te avisa ao vivo no celular.

### Bots de teste (opcional)

Quer testar antes de apostar de verdade? Ligue os três bots, que apostam com **dinheiro de mentira** usando os palpites da skill:

- **Chico** (seguro): só vencedor com 70% ou mais, combo de até 2 jogos, 2% da banca.
- **Arnaldo** (moderado): vencedor com 60% ou mais, combos de 2 a 3 jogos, handicap e over/under com vantagem, 3% da banca.
- **Herman** (agressivo): combos de 4 a 6 jogos que pagam 3x ou mais e zebras com valor, 1% da banca.

Peça "liga os bots" e escolha **quanto dinheiro cada bot recebe**, o **limite de apostas por dia de cada um** (e, se quiser, um teto em dólar) e se eles rodam todo dia sozinhos ou só quando você pedir.

Os bots têm **vida própria**: cada um escolhe as apostas dentro do seu estilo e, quando nada compensa, passa o dia e diz por quê ("hoje não tem jogo seguro, vou guardar a banca"). Eles são modelos: todo dia cada bot apresenta as propostas que faria, e **você escolhe** se segue o Chico, o Arnaldo, o Herman, só algumas apostas, ou se hoje não vai jogar. **Quanto colocar em cada aposta é você que decide.** Ou só **acompanhe sem gastar**: siga todos os bots com um valor simulado (por exemplo, $100 por aposta) e veja quanto teria ganhado ou perdido. O placar mostra os três bots e uma linha "Você" com o resultado do que você escolheu seguir. Todo dia você vê o placar dos três: banca, % de retorno, acertos e dias que passaram. O registro fica só no seu computador (`bots/ledger.csv`).

**Guessitup Arena.** O Chico, o Arnaldo e o Herman do projeto jogam todo dia em um app que você instala no celular: **[thiagontijo.github.io/guessitup](https://thiagontijo.github.io/guessitup/)**. Ele mostra as apostas deles com dinheiro de mentira, acompanha o placar real ao vivo e diz quanto você teria ganhado seguindo os bots com o seu valor por aposta. No iPhone: abra o link no Safari, toque em Compartilhar e depois em "Adicionar à Tela de Início". Detalhes em [references/bots.md](references/bots.md).

> **Brasil:** as apostas esportivas estão proibidas no Brasil desde 25/09/2026 (MP 1.394/2026, ainda em análise no Congresso). Para quem está no Brasil, a skill entrega a análise e os bots de dinheiro de mentira, mas não monta apostas em casas brasileiras.

> São probabilidades, não garantias. Nenhum modelo garante resultado, e apostar envolve risco.

## Instalação

### No app do Claude (site, desktop ou celular)

1. Baixe o **[ZIP da skill](https://github.com/thiagontijo/guessitup/archive/refs/heads/main.zip)** (é o mesmo que o botão verde **Code → Download ZIP**).
2. No Claude, abra **Configurações → Capacidades → Skills** e envie o arquivo ZIP.
3. Peça: "guessitup, jogos de hoje".

(O nome do menu pode mudar entre versões do app; procure por "Skills".)

### No Claude Code (computador)

Requer Python 3 (só biblioteca padrão).

```bash
git clone https://github.com/thiagontijo/guessitup ~/.claude/skills/guessitup
```

Para atualizar depois:

```bash
cd ~/.claude/skills/guessitup && git pull
```

### Idioma

A skill responde em **inglês** por padrão. Para **português** ou **espanhol**, é só pedir ("responde em português", "responde en español") ou escrever para ela nesse idioma: ela continua nele até você pedir outro.

### Exemplos de pedido

- `/guessitup jogos do Brasileirão deste fim de semana`
- "quem leva Palmeiras x Flamengo? quero as chances dos dois lados"
- "palpites do card do UFC de sábado"
- "monta opções de combo pra hoje na Hard Rock e compara com os outros apps"
- "acompanha minhas apostas e me avisa se devo manter ou sair"

## Estrutura

```
guessitup/
├── SKILL.md                 instruções da skill (fluxo, regras, formato do relatório)
├── references/esportes.md   métricas, fontes e modelo indicado por esporte
├── references/apostas.md    Kalshi, combos, hedge, modo advisor e lições aprendidas
├── references/ficha-jogo.md formato da ficha completa do jogo
├── references/handicap-total.md  handicap e over/under com a simulação de 10.000 jogos
├── references/bots.md       bots de teste Chico, Arnaldo e Herman (dinheiro de mentira)
├── scripts/model.py         ferramentas numéricas (só biblioteca padrão)
└── scripts/bots.py          bots de teste: regras, registro e placar
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
| `tennis --pa --pb --best-of` | tênis: % de pontos no saque → hold, set, partida e placar em sets (cadeia de Markov) |
| `log5 --a --b --home` | baseball e afins: win% de cada lado → chance no confronto, com mando |
| `blend --probs --weights` | combina modelos e mede a divergência |
| `value --prob --odds` | valor esperado e Kelly fracionado (0,25x, teto de 5%) |
| `clv --taken --closing` | closing line value |
| `combo --probs ... --stake --pays` | chance do combo e pagamento mínimo em dólar para valer a pena |
| `hedge --stake --payout --opp-pct` | proteção total e pela metade: quanto apostar no lado contrário e lucro garantido |
| `sim --sport --market-spread --market-total [--home --away] --spread --total` | simula 10.000 jogos: vencedor, handicap, over/under, margem e preço justo |
| `expected --sport nba ou nfl ...` | placar esperado pelas estatísticas da temporada (ritmo, ataque, defesa, descanso, desfalques) |
| `grade --prob --app-pct --divergence --data --games` | nota de confiança A-D com os motivos |
| `livewp --lead --minutes-left --spread --app-pct` | chance ao vivo (NFL/NBA) e sinal MANTER / CONSIDERE SAIR |
| `odds --odd --prob` | converte odd americana, decimal ou % para dólar e diz a odd mínima |
| `compare --apps App=odd ... --prob` | mesma aposta em vários apps: qual paga mais |
| `aggregate --home --away --lead` | mata-mata de ida e volta: chance de classificar pelo placar agregado |
| `temper --probs --k` | recalibra probabilidades com a "temperatura" aprendida nos resultados anteriores |
| `ledger add/result/void/pending/report/calibrate` | registro de palpites e calibração: Brier, skill score, comparação com o mercado, acertos esperados x reais, por esporte/confiança/força, ROI, CLV |

O ledger fica em `ledger/predictions.jsonl` (fora do git). A skill registra os palpites sozinha. Depois dos jogos, peça "compare os resultados": ela busca os placares, registra e mostra se as porcentagens se confirmaram. Com menos de ~30 palpites, nada é conclusivo.

A skill aprende com o próprio histórico: `ledger calibrate` mede se ela anda tímida ou confiante demais em cada esporte, e o SKILL.md guarda as lições de cada conferência (seção "Lições da calibração"). O histórico de palpites de cada pessoa fica só no computador dela.

## Fontes e inspiração

Técnicas reescritas do zero, inspiradas em projetos abertos: [penaltyblog](https://github.com/martineastwood/penaltyblog) (modelos de gols, ratings, métricas), [Kairos](https://github.com/m1r4g3-code/kairos) (ledger, CLV, Kelly com teto, ancoragem no mercado) e [GoallineIQ](https://github.com/gmalbert/world-cup) (Elo + Poisson).

## Licença

MIT
