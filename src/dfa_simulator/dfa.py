"""Core DFA logic. No Streamlit imports, so it is easy to test."""
from dataclasses import dataclass


def parse_list(text: str) -> list[str]:
    """Turn 'q0, q1,q2' into ['q0', 'q1', 'q2'] (trimmed, no blanks, no duplicates)."""
    seen, items = set(), []
    for raw in text.split(","):
        item = raw.strip()
        if item and item not in seen:
            seen.add(item)
            items.append(item)
    return items


@dataclass
class DFA:
    states: list[str]
    alphabet: list[str]
    transitions: dict[tuple[str, str], str]  # (state, symbol) -> next state
    start: str
    accept: set[str]

    def validate(self) -> list[str]:
        """Return a list of problems. An empty list means the DFA is valid and complete."""
        errors = []
        if not self.states:
            errors.append("Add at least one state.")
        if not self.alphabet:
            errors.append("Add at least one input symbol.")
        if self.start not in self.states:
            errors.append(f"Start state '{self.start}' is not in the state list.")
        for a in sorted(self.accept - set(self.states)):
            errors.append(f"Accepting state '{a}' is not in the state list.")
        for s in self.states:
            for c in self.alphabet:
                target = self.transitions.get((s, c))
                if target is None:
                    errors.append(f"Missing transition for ({s}, {c}).")
                elif target not in self.states:
                    errors.append(f"Transition ({s}, {c}) points to unknown state '{target}'.")
        return errors

    def trace(self, string: str):
        """Run the DFA on a string.

        Returns (steps, accepted), where steps is a list of
        (state, symbol, next_state). next_state is None if the symbol is not
        in the alphabet; the run stops there and the string is rejected.
        """
        state = self.start
        steps = []
        for ch in string:
            nxt = self.transitions.get((state, ch)) if ch in self.alphabet else None
            steps.append((state, ch, nxt))
            if nxt is None:
                return steps, False
            state = nxt
        return steps, state in self.accept

    def accepts(self, string: str) -> bool:
        return self.trace(string)[1]

    def to_dot(self, current: str | None = None) -> str:
        """Graphviz DOT source. The current state is filled in gold."""
        lines = ["digraph DFA {", "  rankdir=LR;", "  __start [shape=point];"]
        for s in self.states:
            shape = "doublecircle" if s in self.accept else "circle"
            fill = ", style=filled, fillcolor=gold" if s == current else ""
            lines.append(f'  "{s}" [shape={shape}{fill}];')
        lines.append(f'  __start -> "{self.start}";')
        # Merge parallel edges: one arrow labelled "0,1" instead of two arrows.
        grouped: dict[tuple[str, str], list[str]] = {}
        for (s, c), t in self.transitions.items():
            grouped.setdefault((s, t), []).append(c)
        for (s, t), symbols in grouped.items():
            lines.append(f'  "{s}" -> "{t}" [label="{",".join(symbols)}"];')
        lines.append("}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "states": self.states,
            "alphabet": self.alphabet,
            "start": self.start,
            "accept": sorted(self.accept),
            "transitions": [[s, c, t] for (s, c), t in self.transitions.items()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DFA":
        return cls(
            states=list(data["states"]),
            alphabet=list(data["alphabet"]),
            transitions={(s, c): t for s, c, t in data["transitions"]},
            start=data["start"],
            accept=set(data["accept"]),
        )