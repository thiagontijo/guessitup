# guessitup

[English](README.md) · [Português](README.pt-BR.md) · **Español**

**[⬇️ Descargar la skill (ZIP)](https://github.com/thiagontijo/guessitup/archive/refs/heads/main.zip)**

Una skill para Claude ([app](https://claude.ai) y [Claude Code](https://claude.com/claude-code)) que hace **pronósticos deportivos con estadística, no con corazonadas**, para cualquier deporte: fútbol, NBA, NFL, MLB, NHL, tenis, MMA/UFC, F1, vóley, esports y más.

Para cada partido o pelea, la skill busca datos actuales en la web y arma un informe con:

- forma en cinco ventanas: carrera, temporada, último mes, últimos 5 partidos y contexto (local/visitante, superficie, descanso);
- historial de enfrentamientos directos, ponderado por el tamaño de la muestra;
- lesiones y contexto;
- probabilidades calculadas para los dos lados (Poisson/Dixon-Coles, Elo, distribución normal para deportes de puntos), comparadas con el precio del mercado sin margen;
- un pronóstico con nivel de confianza, el precio justo, qué cambiaría el pronóstico y los datos que faltan;
- un resumen final de todos los pronósticos, ordenados por confianza;
- opciones de apuesta y combinadas (segura, equilibrada, arriesgada) para la app que elijas (Hard Rock, FanDuel, DraftKings, bet365, Kalshi, Betano...), con el pago mínimo para que valga la pena y qué app paga más;
- un plan de cobertura (hedge) en dólares: cuánto apostar al otro lado y cuánta ganancia queda asegurada;
- modo asesor en vivo: sigue tus apuestas y dice "mantener" o "considera cobrar" según la probabilidad en vivo (la decisión siempre es tuya).

Cada pedido abre un menú de botones: **App** (Kalshi, Hard Rock, FanDuel, DraftKings u otra), **Tipo de apuesta** (simple, combinada o ambas), **Cobertura** (activada o no) y **Mercados** (ganador, hándicap, más/menos, con una simulación de 10.000 partidos). Cada partido sale en una **ficha completa**: números de la temporada, contexto, simulación y una nota de confianza de A a D.

### Bots de prueba (opcional): Chico, Arnaldo y Herman

¿Quieres probar antes de apostar dinero real? Activa tres bots que apuestan **dinero ficticio** con los pronósticos de la skill:

- **Chico** (seguro): ganadores con 70% o más, combinadas de hasta 2 partidos, 2% de la banca por apuesta.
- **Arnaldo** (moderado): ganadores con 60% o más, combinadas de 2 a 3 partidos, hándicap y más/menos solo con ventaja, 3% de la banca.
- **Herman** (agresivo): combinadas de 4 a 6 partidos que pagan 3x o más y underdogs con valor, 1% de la banca.

Di "activa los bots" y elige **cuánto dinero recibe cada bot**, **el límite diario de cada uno** (número de apuestas y, si quieres, un tope en dólares) y si funcionan solos todos los días o solo cuando tú lo pidas.

Los bots tienen **vida propia**: cada uno elige apuestas dentro de su estilo y, cuando nada vale la pena, se toma el día libre y explica por qué ("hoy no hay partido seguro, guardo la banca"). Son modelos para seguir: cada día cada bot muestra las apuestas que haría y **tú eliges** si sigues a Chico, a Arnaldo, a Herman, solo algunas apuestas o si hoy no juegas. **Tú decides cuánto poner en cada apuesta.** O solo **mira sin gastar**: sigue a todos los bots con un monto simulado (por ejemplo, $100 por apuesta) y ve cuánto habrías ganado o perdido. El marcador muestra los tres bots y una línea "Tú" con el resultado de lo que elegiste seguir: banca, % de retorno, aciertos y días sin jugar. Todo queda en tu computadora (`bots/ledger.csv`). Detalles en [references/bots.md](references/bots.md).

> **Brasil:** las apuestas deportivas están prohibidas en Brasil desde el 25/09/2026 (Medida Provisoria 1.394/2026, aún en análisis en el Congreso). Para usuarios en Brasil, la skill entrega el análisis y los bots de dinero ficticio, pero no arma apuestas en casas brasileñas.

> Son probabilidades, no garantías. Ningún modelo garantiza un resultado y apostar implica riesgo. La skill nunca hace apuestas ni entra en tus cuentas de apuestas.

## Instalación

### En la app de Claude (web, escritorio o celular)

1. Descarga el **[ZIP de la skill](https://github.com/thiagontijo/guessitup/archive/refs/heads/main.zip)** (es lo mismo que el botón verde **Code → Download ZIP**).
2. En Claude, abre **Configuración → Capacidades → Skills** (o **Personalizar → Skills**) y sube el ZIP.
3. Pide: "guessitup, partidos de hoy, responde en español".

### En Claude Code

Necesita Python 3 (solo la biblioteca estándar).

```bash
git clone https://github.com/thiagontijo/guessitup ~/.claude/skills/guessitup
```

Para actualizar después:

```bash
cd ~/.claude/skills/guessitup && git pull
```

### Idioma

La skill responde en **inglés** por defecto. Para español, pídelo ("responde en español") o escríbele en español: seguirá en español hasta que pidas otro idioma. Los montos salen en el formato de la app: "apuesta $20, cobras $38".

### Ejemplos de pedidos

- `/guessitup partidos de LaLiga de este fin de semana`
- "¿quién gana Real Madrid vs Barcelona? dame las probabilidades de los dos lados"
- "pronósticos de la cartelera de UFC del sábado"
- "arma combinadas para esta noche en Hard Rock y compara con otras apps"
- "sigue mis apuestas y avísame si debo mantener o cobrar"
- "activa los bots con $500 cada uno, Herman máximo 2 apuestas por día"

## Estructura

```
guessitup/
├── SKILL.md                 instrucciones de la skill (flujo, reglas, formato del informe)
├── references/esportes.md   métricas, fuentes y modelo por deporte
├── references/apostas.md    Kalshi, combinadas, cobertura, modo asesor y lecciones aprendidas
├── references/ficha-jogo.md formato de la ficha completa del partido
├── references/handicap-total.md  hándicap y más/menos con la simulación de 10.000 partidos
├── references/bots.md       bots de prueba Chico, Arnaldo y Herman (dinero ficticio)
├── scripts/model.py         herramientas numéricas (solo biblioteca estándar)
└── scripts/bots.py          bots de prueba: reglas, límites, propuestas, modo seguir, marcador
```

La lista completa de comandos de `scripts/model.py` y `scripts/bots.py` está en el [README en inglés](README.md#structure).

## Fuentes e inspiración

Técnicas reescritas desde cero, inspiradas en proyectos abiertos: [penaltyblog](https://github.com/martineastwood/penaltyblog), [Kairos](https://github.com/m1r4g3-code/kairos) y [GoallineIQ](https://github.com/gmalbert/world-cup).

## Licencia

MIT
