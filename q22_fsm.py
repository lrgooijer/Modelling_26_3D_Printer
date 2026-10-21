from statemachine import StateMachine, State

class Q22FSM(StateMachine):
    q0State = State("q0", initial = True)
    q1State = State("q1")
    q2State = State("q2")
    q3State = State("q3")

    H0 = q0State.to(q1State) | q1State.to(q1State) | q2State.to(q3State) | q3State.to(q3State)
    V0 = q0State.to(q2State) | q2State.to(q2State) | q1State.to(q3State) | q3State.to(q3State)
    H1 = q0State.to(q0State) | q2State.to(q2State) | q3State.to(q2State) | q1State.to(q0State)
    V1 = q0State.to(q0State) | q1State.to(q1State) | q3State.to(q1State) | q2State.to(q0State)

fsm = Q22FSM()
test_sequences = [["H0","V0"],["H1","V1","H1", "H0", "V1", "V0"]]
def run_test(test_sequence):
    for input in test_sequence:
        fsm.send(input)
        print(fsm.current_state.id)
        final_state = fsm.final_states
    return final_state
for test_sequence in test_sequences:
    final_test_state = run_test(test_sequence)
    assert final_test_state[0] == "q3State"






