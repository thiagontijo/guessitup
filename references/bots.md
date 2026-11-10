# Bots de teste: Chico, Arnaldo e Herman (opcional)

Três bots que apostam com **dinheiro de mentira** usando os palpites da guessitup. Cada um tem um estilo e **vida própria**: ele mesmo escolhe as apostas do dia dentro das suas regras e pode dizer "hoje não compensa" e não apostar nada. Eles servem de **modelo**: quem quiser pode acompanhar, comparar e copiar o estilo que der mais certo. Nunca fazem aposta real, nunca entram em conta de app e só rodam se o usuário escolher.

| Bot | Estilo | Regras | Aposta | Limite padrão |
|---|---|---|---|---|
| **Chico** | Seguro: joga sempre pensando em ganhar | Vencedor com chance ≥ 70%, ou combo de até 2 pernas (cada uma ≥ 70%). Nunca Over. | 2% da banca | 5 por dia |
| **Arnaldo** | Moderado: arrisca um pouco mais | Vencedor ≥ 60%, combo de 2 a 3 pernas (cada uma ≥ 60%). Handicap/Under só com vantagem ≥ 3 pontos; Over só com ≥ 5. | 3% da banca | 6 por dia |
| **Herman** | Agressivo: arrisca muito para ganhar muito | Combo de 4 a 6 pernas que pague 3x ou mais, ou zebra com valor (chance do modelo > preço do app + 5 pontos). | 1% da banca | 5 por dia |

As regras da seção "Autocrítica" de [apostas.md](apostas.md) valem para os três (handicap contra favorito, Over com desconto, dupla chance, `aggregate` no mata-mata, dado faltando baixa a nota).

## Os bots propõem, o usuário decide (modo seguir)

Todo dia cada bot apresenta as **propostas** que ele faria: jogo, aposta, chance, quanto paga e quanto ele mesmo apostaria. A partir daí o usuário escolhe, sem obrigação:
- **Seguir um bot** (ou mais de um) no dia: copia as propostas dele.
- **Escolher apostas soltas** de bots diferentes.
- **Não jogar hoje**: "hoje não vou jogar". Os bots continuam apostando no dinheiro de mentira, e o placar segue.

Para cada aposta que escolher, **o usuário decide quanto quer colocar**. O pagamento é recalculado com o mesmo multiplicador da proposta (proposta paga 1,28x → apostando $50, recebe $64). Quem faz a aposta no app é sempre o usuário; a skill só registra o que ele disse que seguiu, para mostrar no placar a linha "Você" ao lado dos três bots.

Fluxo do dia (perguntar com botões, AskUserQuestion; sem a ferramenta, opções numeradas):
1. Mostre as propostas de cada bot (`bots.py offers`), cada bot falando em primeira pessoa.
2. Pergunte **"Hoje você quer:"** (multiSelect): Seguir o Chico · Seguir o Arnaldo · Seguir o Herman · Só acompanhar todos, sem gastar · Hoje não vou jogar. Em "Other" ele pode citar apostas soltas pelo número (#1, #3).
3. Para cada aposta escolhida, pergunte o valor: **"Quanto em cada aposta?"**: Mesmo valor do bot · $10 · $20 · Outro valor. Ele pode dar um valor diferente para cada aposta.
4. Registre com `bots.py follow --id N --amount X` (ou `--pass-day`) e confirme em uma linha por aposta: "Você segue #1 do Chico: Knicks vencem, aposta $50, recebe $64."
5. Se o usuário não estiver presente (tarefa agendada), só apresente as propostas e termine com: "Me diga qual bot quer seguir hoje e quanto em cada aposta, ou 'hoje não vou jogar'."

## Acompanhar sem gastar (modo simulado)

O usuário pode **seguir todos os bots (ou só alguns) sem colocar dinheiro**, só para acompanhar. Ele escolhe um **valor-base por aposta** (ex.: $100) e cada proposta do dia vira uma aposta simulada desse valor, com o mesmo multiplicador da proposta. O placar ganha a linha **"Você sim."**, separada da linha "Você" (apostas reais que ele disse que fez), para ele ver quanto teria ganhado ou perdido seguindo os bots.

- Ligar: `bots.py watch --amount 100` (todos os bots) ou `--bot chico` (só um). O valor-base fica salvo; nos dias seguintes basta `bots.py watch`.
- Uma aposta solta em modo simulado: `bots.py follow --id 3 --amount 50 --watch`.
- `settle` confere também as apostas simuladas.
- Com o modo ligado e frequência "todo dia sozinho", a tarefa diária roda `watch` depois das propostas e mostra a linha "Você sim." na mensagem.

## O usuário escolhe a banca e o limite de cada bot

Cada bot tem a sua própria banca inicial e o seu próprio limite diário, definidos pelo usuário:
- **Banca inicial** de cada bot (ex.: Chico $1.000, Arnaldo $500, Herman $200).
- **Limite de apostas por dia** (ex.: Herman no máximo 2).
- **Teto em dólar por dia**, opcional (ex.: Chico no máximo $30 por dia somando tudo). Se a aposta normal passar do teto, o valor é reduzido até caber; se o teto já foi usado, o bot para no dia.

## Vida própria: o bot pode passar o dia

Os bots não apostam por obrigação. Se nenhum jogo cabe nas regras, ou se o preço do app está ruim, o bot **passa o dia** e explica com as próprias palavras, no seu jeito de falar:
- **Chico** (calmo, paciente): "Hoje não tem jogo seguro, vou guardar a banca."
- **Arnaldo** (equilibrado, analítico): "Os favoritos de hoje estão caros no app. Não tem conta que feche."
- **Herman** (ousado, mas não burro): "Não achei combo que pague o risco. Amanhã eu volto."

Registre com `bots.py skip --bot NOME --reason "..."`. Passar o dia é uma decisão do bot e conta no placar (coluna "Passou"): um bot que passa muito e perde pouco também está mostrando algo.

Na mensagem do dia, cada bot fala em primeira pessoa: o que escolheu e por quê, ou por que passou. Discordar entre eles é normal (Chico passa, Herman entra no mesmo jogo).

## Bots como modelo para seguir

- Cada aposta sai num formato fácil de copiar no app: jogo, aposta, "aposta $X, recebe $Y" e a chance.
- Com o tempo, o placar mostra qual estilo combina com o usuário. Quem quiser pode seguir um bot, misturar os estilos ou criar o seu próprio.
- Seguir um bot com dinheiro de verdade é decisão só do usuário. Dinheiro de mentira não tem taxa nem emoção; com menos de ~30 apostas conferidas por bot, nada é conclusivo.

## Quando oferecer

- Uma vez, no fim da primeira entrega de palpites da conversa, numa linha: "Quer ligar os bots de teste (Chico, Arnaldo e Herman) para ver qual estilo ganha mais com dinheiro de mentira?"
- Sempre que o usuário disser "bots", "Chico", "Arnaldo", "Herman", "simulação" ou "dinheiro de mentira".
- Se o usuário disser não, não ofereça de novo na mesma conversa.

## Como ligar (perguntar com botões)

Chame AskUserQuestion (sem a ferramenta, mostre as opções numeradas):
1. **Quais bots** (multiSelect): Chico · Arnaldo · Herman.
2. **Banca** (header "Banca"): Mesma para todos ($1.000) · Escolher um valor para cada bot. No segundo caso, pergunte o valor de cada um em texto.
3. **Limite diário** (header "Limite"): Padrão (5 / 6 / 5 apostas) · Escolher para cada bot (número de apostas e, se quiser, teto em dólar).
4. **Frequência** (header "Quando"): Todo dia sozinho · Só quando eu pedir.

Depois rode `init` e um `config` por bot com o que ele escolheu, e mostre o resultado de `show`. O usuário pode mudar banca ou limite a qualquer hora ("muda o limite do Herman para 3").

## Comandos

```bash
B=~/.claude/skills/guessitup/scripts/bots.py
python3 $B init --bank 1000                                    # liga os três com a mesma banca
python3 $B config --bot herman --bank 200 --max-bets 2         # banca e limite próprios
python3 $B config --bot chico --max-dollars 30                 # teto em dólar por dia (0 tira o teto)
python3 $B show                                                # configuração atual
python3 $B rules                                               # regras e jeito de falar de cada um

python3 $B pending                                             # 1. conferir as de ontem
python3 $B settle --id 3 --result win                          #    win, loss ou void (adiado/cancelado)
python3 $B check --bot herman --type combo --legs 0.8,0.75,0.7,0.7   # 2. cabe nas regras?
python3 $B add --bot chico --sport nba --game "Knicks x Nets" --bet "Knicks vencem" \
    --type winner --legs 0.82 --price 0.78 --grade B           # 3. registrar
python3 $B skip --bot arnaldo --reason "Favoritos caros hoje"  #    ou passar o dia
python3 $B offers                                              # 4. propostas de cada bot
python3 $B follow --id 3 --amount 15                           # 5. o usuário segue a #3 com $15
python3 $B follow --pass-day                                   #    ou "hoje não vou jogar"
python3 $B watch --amount 100                                  #    ou acompanhar todos sem gastar (simulado)
python3 $B report                                              # 6. placar dos três + Você
```

- `--legs`: chances do modelo de cada perna (fração). `--price`: preço no app (0.78 = 78%); sem ele, usa a chance do modelo. Combo: preço = produto das pernas.
- `--type`: winner, combo, handicap, over, under ou underdog. `--edge`: vantagem em pontos para handicap/total.
- O script recusa apostas fora das regras do bot e acima dos limites do usuário. Combo só ganha se todas as pernas ganharem.
- `settle` de uma proposta também confere as cópias que o usuário seguiu.
- Tudo fica em `bots/` (fora do git, só no computador do usuário).

## Frequência "todo dia sozinho"

Se a sessão tiver ferramenta de tarefa agendada, crie uma tarefa diária (de manhã, no fuso do usuário) com um prompt completo: conferir as pendentes, cada bot escolher as apostas do dia pelas suas regras e limites (ou passar o dia), registrar com `bots.py` e mandar o relatório como notificação. Sem ferramenta de agendamento, diga que só roda quando o usuário pedir ("roda os bots").

## Mensagem do dia

No idioma da resposta (inglês por padrão, regra "Idioma" do SKILL.md). As falas dos bots acima são exemplos; traduza-as mantendo o jeito de cada um.

1. Resultado de ontem por bot (ganhou/perdeu, em dólar no formato do app: "aposta $20, recebe $26").
2. Placar dos três e do usuário ("Você"): banca, % de retorno, acertos e dias que passou (saída de `report`).
3. Cada bot fala em primeira pessoa: as propostas de hoje e o porquê, ou por que passou.
4. Pergunta final: qual bot seguir hoje, quanto em cada aposta, ou "hoje não vou jogar".
5. Às segundas: autocrítica da semana (o que funcionou, o que falhou, regra que vale mudar).
6. Lembrete: é dinheiro de mentira, e com menos de ~30 apostas por bot nada é conclusivo. Seguir um bot de verdade é decisão sempre do usuário.
