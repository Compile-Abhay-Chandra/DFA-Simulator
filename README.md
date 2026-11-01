# DFA Simulator

A small web app for building a deterministic finite automaton (DFA), running strings through it, and watching the run step by step. Built with Python and Streamlit.

## Features

- Define states, an alphabet, a start state, and accepting states from the sidebar
- Fill in the transition table with dropdowns, so the DFA is always complete
- Run any input string and step through it with a slider
- See the state diagram, with the current state highlighted
- Read a step-by-step trace table and a clear accept or reject result
- Save a DFA to JSON and load it again later
- Starts with an example DFA (binary strings that end in `1`)

## Requirements

- Python 3.10 or newer
- `streamlit`
- `pytest` (only for running the tests)

## Setup

```bash
pip install streamlit pytest
```

## Run the app

From this folder:

```bash
streamlit run app.py
```

Streamlit prints a local address (usually http://localhost:8501) and opens it in your browser.

## How to use it

1. In the sidebar, enter your states and alphabet as comma-separated lists, for example `q0, q1, q2` and `0, 1`. Each symbol must be a single character.
2. Choose the start state and the accepting states.
3. In the transition table, pick the next state for every state and symbol pair. Each cell defaults to staying in the same state.
4. Type a string under **Run it on a string**. The empty string is allowed.
5. Drag the **Step** slider to move through the run. The highlighted state in the diagram shows where the DFA is at that step.
6. Use **Save DFA as JSON** in the sidebar to download your DFA, and **Load a saved DFA** to bring it back.

If you change the list of states or the alphabet, the start, accepting, and transition choices reset, because they depend on those lists.

## Project structure

| File | Purpose |
| --- | --- |
| `dfa.py` | DFA logic: validation, running a string, Graphviz output, JSON conversion. No Streamlit code. |
| `app.py` | The Streamlit interface. |
| `test_dfa.py` | Tests for the logic in `dfa.py`. |

## Run the tests

```bash
pytest
```

The tests cover accepting and rejecting strings, symbols outside the alphabet, validation errors, trace output, and the JSON round trip.

## Saved file format

A saved DFA is a JSON file with this shape (this one accepts binary strings ending in `1`):

```json
{
  "states": ["q0", "q1"],
  "alphabet": ["0", "1"],
  "start": "q0",
  "accept": ["q1"],
  "transitions": [
    ["q0", "0", "q0"],
    ["q0", "1", "q1"],
    ["q1", "0", "q0"],
    ["q1", "1", "q1"]
  ]
}
```

Each transition is `[from state, symbol, to state]`. Every state needs one transition for every symbol, or the file is rejected on load.

## Limitations

- DFAs must be complete. There is no implicit dead state, so add one yourself if you need it.
- Alphabet symbols are single characters. Multi-character symbols are not supported.
- State names should not contain commas or double quotes.
- A symbol outside the alphabet rejects the string immediately.

## Ideas for next steps

- Convert an NFA to a DFA (subset construction)
- DFA minimization
- Regular expression to DFA
- Check whether two DFAs accept the same language