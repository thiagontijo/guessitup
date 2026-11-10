# Bots de teste: Chico, Arnaldo e Herman (opcional)

Três bots que apostam com **dinheiro de mentira** usando os palpites da guessitup. Servem para medir, com o tempo, qual estilo de aposta dá mais retorno, sem arriscar um dólar. Eles nunca fazem aposta real, nunca entram em conta de app e só rodam se o usuário escolher.

| Bot | Estilo | Regras | Aposta | Máx. por dia |
|---|---|---|---|---|
| **Chico** | Seguro: joga sempre pensando em ganhar | Vencedor com chance ≥ 70%, ou combo de até 2 pernas (cada uma ≥ 70%). Nunca Over. | 2% da banca | 5 |
| **Arnaldo** | Moderado: arrisca um pouco mais | Vencedor ≥ 60%, combo de 2 a 3 pernas (cada uma ≥ 60%). Handicap/Under só com vantagem ≥ 3 pontos; Over só com ≥ 5. | 3% da banca | 6 |
| **Herman** | Agressivo: arrisca muito para ganhar muito | Combo de 4 a 6 pernas que pague 3x ou mais, ou zebra com valor (chance do modelo > preço do app + 5 pontos). | 1% da banca | 5 |

Todos começam com $1.000 (ou o valor que o usuário escolher). As regras da seção "Autocrítica" de [apostas.md](apostas.md) valem para os três (handicap contra favorito, Over com desconto, dupla chance, `aggregate` no mata-mata, dado faltando baixa a nota).

## Quando oferecer

- Uma vez, no fim da primeira entrega de palpites da conversa, numa linha: "Quer ligar os bots de teste (Chico, Arnaldo e Herman) para ver qual estilo ganha mais com dinheiro de mentira?"
- Sempre que o usuário disser "bots", "Chico", "Arnaldo", "Herman", "simulação" ou "dinheiro de mentira".
- Se o usuário disser não, não ofereça de novo na mesma conversa.

Ao ligar, pergunte com botões (AskUserQuestion): **Banca inicial** ($1.000 · $500 · $5.000) e **Frequência** (Todo dia sozinho · Só quando eu pedir). Depois rode `bots.py init --bank X`.

## Como rodar (cada dia)

```bash
B=~/.claude/skills/guessitup/scripts/bots.py
python3 $B pending                                   # 1. conferir as de ontem
python3 $B settle --id 3 --result win                # win, loss ou void (adiado/cancelado)
python3 $B check --bot herman --type combo --legs 0.8,0.75,0.7,0.7   # 2. a aposta cabe nas regras?
python3 $B add --bot chico --sport nba --game "Knicks x Nets" --bet "Knicks vencem" \
    --type winner --legs 0.82 --price 0.78 --grade B  # 3. registrar (valor calculado sozinho)
python3 $B report                                    # 4. comparar os três
```

- `--legs`: chances do modelo de cada perna (fração). `--price`: preço no app (0.78 = 78%); sem ele, usa a chance do modelo. Combo: preço = produto das pernas.
- `--type`: winner, combo, handicap, over, under ou underdog. `--edge`: vantagem em pontos para handicap/total.
- O script recusa apostas fora das regras do bot e acima do limite do dia. Combo só ganha se todas as pernas ganharem.
- O registro fica em `bots/ledger.csv` (fora do git, só no computador do usuário).

## Frequência "todo dia sozinho"

Se a sessão tiver ferramenta de tarefa agendada, crie uma tarefa diária (de manhã, no fuso do usuário) com um prompt completo: conferir as pendentes, escolher as apostas do dia para cada bot pelas regras acima, registrar com `bots.py`, e mandar o relatório como notificação. Sem ferramenta de agendamento, diga que só roda quando o usuário pedir ("roda os bots").

## Mensagem do dia

1. Resultado de ontem por bot (ganhou/perdeu, em dólar no formato do app: "aposta $20, recebe $26").
2. Placar dos três: banca, % de retorno, acertos (saída de `report`).
3. Apostas de hoje de cada bot.
4. Às segundas: autocrítica da semana (o que funcionou, o que falhou, regra que vale mudar).
5. Lembrete: é dinheiro de mentira, e com menos de ~30 apostas por bot nada é conclusivo. A decisão de apostar de verdade é sempre do usuário.
