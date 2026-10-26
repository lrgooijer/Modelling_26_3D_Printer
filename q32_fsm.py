from statemachine import StateMachine, State

class Q32_SQUARE_FSM(StateMachine):
    q0State = State("BottomLeft", initial = True)
    q1State = State("BottomRight")
    q2State = State("TopRight")
    q3State = State("TopLeft")
    q4State = State( "Done",final = True)

    
    event1 = q0State.to(q1State)
    event2 = q1State.to(q2State) 
    event3 = q2State.to(q3State) 
    event4 = q3State.to(q4State)
