from statemachine import StateMachine, State

class Q21FSM(StateMachine):
    q0State = State("Printing", initial = True)
    q1State = State("Stopped Printing")
    q2State = State("Moving to Wipe Position")
    q3State = State("Wiping")
    q4State = State("Nozzle Cooling")
    q5State = State("Loading Filament")
    q6State = State("Nozzle Heating")
    q7State = State("Moving to Saved Position")
    
    # TODO add outputs to states

    new_colour_req = q0State.to(q1State)
    new_filament_req = q0State.to(q1State)
    stopped = q1State.to(q2State)
    at_wipe_loc = q2State.to(q3State)
    wipe_complete = q3State.to(q4State)
    nozzle_cooled = q4State.to(q5State)
    filament_loaded = q5State.to(q6State)
    nozzle_heated = q6State.to(q7State)
    at_saved_loc = q7State.to(q0State)

def run_test_fsm(sequence: list[str])-> list[str]: 
    fsm = Q21FSM()
    state_sequence = []
    for input in sequence:
        fsm.send(input)
        state = fsm.current_state.id
        state_sequence.append(state)
    return state_sequence

if __name__=="__main__":
    test_sequences = [
                    ["new_colour_req","stopped",
                     "at_wipe_loc","wipe_complete",
                     "nozzle_cooled","filament_loaded",
                     "nozzle_heated","at_saved_loc"],

                    ["new_filament_req","stopped",
                     "at_wipe_loc","wipe_complete",
                     "nozzle_cooled","filament_loaded",
                     "nozzle_heated","at_saved_loc"],
                    ]

    assert run_test_fsm(test_sequences[0]) == ['q1State', 'q2State', 'q3State', 'q4State', 'q5State', 'q6State', 'q7State', 'q0State']
    assert run_test_fsm(test_sequences[1]) == ['q1State', 'q2State', 'q3State', 'q4State', 'q5State', 'q6State', 'q7State', 'q0State']
