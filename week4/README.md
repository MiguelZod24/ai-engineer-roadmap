# Semana 4 — LangGraph: Agentes con Estado

## ¿Qué es LangGraph?
Framework que permite construir agentes con flujo controlado mediante grafos de estado.
En lugar de dejar al agente decidir todo solo, tú defines exactamente cómo fluye la lógica.

## Conceptos clave
- **Estado**: paquete de datos que viaja entre nodos
- **Nodos**: funciones Python que transforman el estado
- **Edges**: conexiones entre nodos (fijas o condicionales)
- **Checkpointer**: guarda el estado para memoria persistente o pausas

## Archivos

| Archivo | Concepto |
|---|---|
| `01_primer_grafo.py` | Grafo mínimo sin LLM |
| `02_grafo_con_llm.py` | Grafo con Claude dentro del nodo |
| `03_agente_react.py` | Patrón ReAct: Claude decide si usar herramientas |
| `04_memoria_persistente.py` | MemorySaver: el agente recuerda entre sesiones |
| `05_flujos_condicionales.py` | El grafo toma caminos distintos según el mensaje |
| `06_human_in_the_loop.py` | El agente se pausa y espera confirmación humana |

## Flujo del agente ReAct


## Stack
- `langgraph` — grafos de estado
- `langchain-anthropic` — conector con Claude
- `MemorySaver` — memoria persistente
