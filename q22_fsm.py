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


def run_fsm(test_sequence):
    fsm = Q22FSM()
    state_sequence = []
    for input in test_sequence:
        fsm.send(input)
        state = fsm.current_state.id
        state_sequence.append(state)
    return state_sequence

def loop_sequences(test_sequences)-> list[list[str]]:
    output_state_sequences = []
    for test_sequence in test_sequences:
        state_sequence = run_fsm(test_sequence)
        output_state_sequences.append(state_sequence)
    return output_state_sequences

if __name__=="__main__":
    test_sequences = [["H0","V0"],["H1","V1","H1", "H0", "V1", "V0"]]
    state_sequences = loop_sequences(test_sequences)
    assert state_sequences[0] == ['q1State', 'q3State']
    assert state_sequences[1] == ['q0State', 'q0State','q0State', 'q1State','q1State', 'q3State']






