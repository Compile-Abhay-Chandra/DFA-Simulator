import json

import streamlit as st

from dfa import DFA, parse_list

st.set_page_config(page_title="DFA Simulator", layout="wide")

# Example loaded on first visit: binary strings that end in 1.
EXAMPLE = DFA(
    states=["q0", "q1"],
    alphabet=["0", "1"],
    transitions={("q0", "0"): "q0", ("q0", "1"): "q1",
                 ("q1", "0"): "q0", ("q1", "1"): "q1"},
    start="q0",
    accept={"q1"},
)


# Widget keys include the state/alphabet names. When those change, the
# dependent widgets get fresh keys and reset instead of holding stale values.
def state_sig(states):
    return "|".join(states)


def table_sig(states, alphabet):
    return state_sig(states) + "::" + "|".join(alphabet)


def load_into_state(dfa: DFA):
    """Push a DFA into session state. Call before the widgets are drawn."""
    st.session_state["states_text"] = ", ".join(dfa.states)
    st.session_state["alphabet_text"] = ", ".join(dfa.alphabet)
    st.session_state[f"start::{state_sig(dfa.states)}"] = dfa.start
    st.session_state[f"accept::{state_sig(dfa.states)}"] = sorted(dfa.accept)
    tsig = table_sig(dfa.states, dfa.alphabet)
    for (s, c), t in dfa.transitions.items():
        st.session_state[f"t::{tsig}::{s}::{c}"] = t


if "states_text" not in st.session_state:
    load_into_state(EXAMPLE)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Define your DFA")

    uploaded = st.file_uploader("Load a saved DFA (JSON)", type="json")
    if uploaded is not None:
        try:
            loaded = DFA.from_dict(json.loads(uploaded.getvalue()))
            problems = loaded.validate()
        except Exception:
            loaded, problems = None, ["That file is not a DFA saved by this app."]
        if problems:
            st.error("\n".join(problems))
        elif st.session_state.get("loaded_marker") != (uploaded.name, uploaded.size):
            load_into_state(loaded)
            st.session_state["loaded_marker"] = (uploaded.name, uploaded.size)

    states = parse_list(st.text_input("States (comma-separated)", key="states_text"))
    alphabet = parse_list(st.text_input("Alphabet (single characters, comma-separated)",
                                        key="alphabet_text"))

    if not states or not alphabet:
        st.error("Enter at least one state and one input symbol.")
        st.stop()
    if any(len(c) != 1 for c in alphabet):
        st.error("Each input symbol must be a single character.")
        st.stop()

    ssig = state_sig(states)
    st.session_state.setdefault(f"start::{ssig}", states[0])
    st.session_state.setdefault(f"accept::{ssig}", [])
    start = st.selectbox("Start state", states, key=f"start::{ssig}")
    accept = st.multiselect("Accepting states", states, key=f"accept::{ssig}")

# ------------------------------------------------------- transition table
st.title("DFA Simulator")
st.subheader("Transition table")
st.caption("→ marks the start state and * marks an accepting state. "
           "Pick where each state goes on each symbol.")

tsig = table_sig(states, alphabet)
header = st.columns(len(alphabet) + 1)
header[0].markdown("**State**")
for col, c in zip(header[1:], alphabet):
    col.markdown(f"**{c}**")

transitions = {}
for s in states:
    row = st.columns(len(alphabet) + 1)
    row[0].markdown(f"`{'→' if s == start else ''}{'*' if s in accept else ''}{s}`")
    for col, c in zip(row[1:], alphabet):
        key = f"t::{tsig}::{s}::{c}"
        st.session_state.setdefault(key, s)  # default: stay in the same state
        transitions[(s, c)] = col.selectbox(
            f"From {s} on {c}", states, key=key, label_visibility="collapsed")

dfa = DFA(states, alphabet, transitions, start, set(accept))
errors = dfa.validate()
if errors:
    st.error("\n".join(errors))
    st.stop()

st.sidebar.download_button("Save DFA as JSON", json.dumps(dfa.to_dict(), indent=2),
                           file_name="dfa.json", mime="application/json")

# ------------------------------------------------------------- simulation
st.subheader("Run it on a string")
text = st.text_input("Input string", "0101")
steps, accepted = dfa.trace(text)

if steps:
    step = st.slider("Step", 0, len(steps), len(steps))
else:
    step = 0
    st.caption("The empty string is accepted only if the start state is accepting.")

current = dfa.start if step == 0 else steps[step - 1][2]
bad = next((s for s in steps[:step] if s[2] is None), None)

left, right = st.columns([3, 2])
with left:
    st.graphviz_chart(dfa.to_dot(current))
with right:
    if bad:
        st.warning(f"'{bad[1]}' is not in the alphabet, so the string is rejected.")
    elif step == len(steps):
        if accepted:
            st.success(f"Accepted: the run ends in {current}, an accepting state.")
        else:
            st.error(f"Rejected: the run ends in {current}, which is not accepting.")
    else:
        st.info(f"Step {step} of {len(steps)}. Current state: {current}.")

    if steps[:step]:
        st.dataframe(
            [{"Step": i + 1, "From": a, "Symbol": b, "To": c or "—"}
             for i, (a, b, c) in enumerate(steps[:step])],
            hide_index=True,
        )