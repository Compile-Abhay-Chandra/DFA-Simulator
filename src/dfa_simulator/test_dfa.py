from dfa import DFA, parse_list

ENDS_IN_1 = DFA(
    states=["q0", "q1"],
    alphabet=["0", "1"],
    transitions={("q0", "0"): "q0", ("q0", "1"): "q1",
                 ("q1", "0"): "q0", ("q1", "1"): "q1"},
    start="q0",
    accept={"q1"},
)

EVEN_ZEROS = DFA(
    states=["e", "o"],
    alphabet=["0", "1"],
    transitions={("e", "0"): "o", ("o", "0"): "e",
                 ("e", "1"): "e", ("o", "1"): "o"},
    start="e",
    accept={"e"},
)


def test_ends_in_1():
    assert ENDS_IN_1.accepts("1")
    assert ENDS_IN_1.accepts("0101")
    assert not ENDS_IN_1.accepts("10")
    assert not ENDS_IN_1.accepts("")  # start state is not accepting


def test_even_zeros():
    assert EVEN_ZEROS.accepts("")  # start state is accepting
    assert EVEN_ZEROS.accepts("1010")
    assert not EVEN_ZEROS.accepts("0")


def test_symbol_outside_alphabet_is_rejected():
    steps, accepted = ENDS_IN_1.trace("1x1")
    assert not accepted
    assert steps[-1] == ("q1", "x", None)


def test_trace_steps():
    steps, _ = ENDS_IN_1.trace("01")
    assert steps == [("q0", "0", "q0"), ("q0", "1", "q1")]


def test_validate_reports_missing_transition():
    broken = DFA(["a"], ["0", "1"], {("a", "0"): "a"}, "a", {"a"})
    assert any("Missing transition" in e for e in broken.validate())


def test_validate_reports_bad_start_and_accept():
    broken = DFA(["a"], ["0"], {("a", "0"): "a"}, "z", {"y"})
    errors = broken.validate()
    assert any("Start state" in e for e in errors)
    assert any("Accepting state" in e for e in errors)


def test_json_round_trip():
    assert DFA.from_dict(ENDS_IN_1.to_dict()) == ENDS_IN_1


def test_parse_list():
    assert parse_list(" q0, q1 ,,q0, q2 ") == ["q0", "q1", "q2"]