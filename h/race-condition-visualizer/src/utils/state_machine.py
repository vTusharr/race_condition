"""
State machine for modeling concurrent process execution and state transitions.
Used to generate state graphs for visualization.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum


class ProcessState(Enum):
    """States a process can be in"""

    IDLE = "IDLE"
    READING = "READING"
    WRITING = "WRITING"
    WAITING = "WAITING"
    CRITICAL = "CRITICAL"


@dataclass
class SystemState:
    """Represents a system state in concurrent execution"""

    p1_state: ProcessState
    p2_state: ProcessState
    counter: int
    flag1: bool = False
    flag2: bool = False
    turn: int = 0

    def __hash__(self):
        return hash(
            (
                self.p1_state.value,
                self.p2_state.value,
                self.counter,
                self.flag1,
                self.flag2,
                self.turn,
            )
        )

    def __eq__(self, other):
        return (
            self.p1_state == other.p1_state
            and self.p2_state == other.p2_state
            and self.counter == other.counter
            and self.flag1 == other.flag1
            and self.flag2 == other.flag2
            and self.turn == other.turn
        )

    def is_race_condition(self) -> bool:
        """Check if this state represents a race condition"""
        return self.p1_state in [
            ProcessState.READING,
            ProcessState.WRITING,
        ] and self.p2_state in [ProcessState.READING, ProcessState.WRITING]

    def is_mutual_exclusion_violated(self) -> bool:
        """Check if mutual exclusion is violated"""
        return (
            self.p1_state == ProcessState.CRITICAL
            and self.p2_state == ProcessState.CRITICAL
        )

    def to_label(self, include_peterson: bool = False) -> str:
        """Generate label for visualization"""
        label = f"P1: {self.p1_state.value}\nP2: {self.p2_state.value}\nCounter: {self.counter}"
        if include_peterson:
            label += f"\nflag1={self.flag1}, flag2={self.flag2}\nturn={self.turn}"
        return label


@dataclass
class Transition:
    """Represents a state transition"""

    from_state: SystemState
    to_state: SystemState
    action: str
    process: int  # Which process (1 or 2)


class RaceConditionStateMachine:
    """State machine for race condition scenario"""

    def __init__(self):
        self.states: List[SystemState] = []
        self.transitions: List[Transition] = []
        self._generate_states()

    def _generate_states(self):
        """Generate all possible states for race condition scenario"""
        # Initial state
        s0 = SystemState(ProcessState.IDLE, ProcessState.IDLE, 0)

        # P1 reads first
        s1 = SystemState(ProcessState.READING, ProcessState.IDLE, 0)
        s2 = SystemState(ProcessState.WRITING, ProcessState.IDLE, 1)
        s3 = SystemState(ProcessState.IDLE, ProcessState.IDLE, 1)

        # P2 reads first
        s4 = SystemState(ProcessState.IDLE, ProcessState.READING, 0)
        s5 = SystemState(ProcessState.IDLE, ProcessState.WRITING, 1)

        # Both read (RACE!)
        s6 = SystemState(ProcessState.READING, ProcessState.READING, 0)
        s7 = SystemState(ProcessState.WRITING, ProcessState.READING, 0)
        s8 = SystemState(ProcessState.WRITING, ProcessState.WRITING, 1)  # Lost update!
        s9 = SystemState(ProcessState.IDLE, ProcessState.WRITING, 1)

        self.states = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]

        # Define transitions
        self.transitions = [
            Transition(s0, s1, "P1 reads counter", 1),
            Transition(s1, s2, "P1 writes counter", 1),
            Transition(s2, s3, "P1 done", 1),
            Transition(s0, s4, "P2 reads counter", 2),
            Transition(s4, s5, "P2 writes counter", 2),
            Transition(s5, s3, "P2 done", 2),
            # Race condition path
            Transition(s0, s6, "BOTH read (same value!)", 0),
            Transition(s6, s7, "P1 writes", 1),
            Transition(s7, s9, "P2 writes (overwrites P1!)", 2),
            Transition(s6, s8, "BOTH write", 0),
        ]

    def get_race_states(self) -> List[SystemState]:
        """Return states where race condition occurs"""
        return [s for s in self.states if s.is_race_condition()]


class PetersonStateMachine:
    """State machine for Peterson's algorithm"""

    def __init__(self):
        self.states: List[SystemState] = []
        self.transitions: List[Transition] = []
        self._generate_states()

    def _generate_states(self):
        """Generate states showing Peterson's algorithm correctness"""
        # Initial state
        s0 = SystemState(ProcessState.IDLE, ProcessState.IDLE, 0, False, False, 0)

        # P1 requests entry
        s1 = SystemState(ProcessState.WAITING, ProcessState.IDLE, 0, True, False, 1)
        s2 = SystemState(ProcessState.CRITICAL, ProcessState.IDLE, 1, True, False, 1)
        s3 = SystemState(ProcessState.IDLE, ProcessState.IDLE, 1, False, False, 1)

        # P2 requests entry
        s4 = SystemState(ProcessState.IDLE, ProcessState.WAITING, 0, False, True, 0)
        s5 = SystemState(ProcessState.IDLE, ProcessState.CRITICAL, 1, False, True, 0)

        # Both request (mutual exclusion preserved!)
        s6 = SystemState(ProcessState.WAITING, ProcessState.WAITING, 0, True, True, 0)
        s7 = SystemState(ProcessState.WAITING, ProcessState.WAITING, 0, True, True, 1)
        s8 = SystemState(ProcessState.WAITING, ProcessState.CRITICAL, 1, True, True, 0)
        s9 = SystemState(ProcessState.CRITICAL, ProcessState.WAITING, 1, True, True, 1)

        self.states = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]

        # Define transitions (no mutual exclusion violation possible)
        self.transitions = [
            Transition(s0, s1, "P1 sets flag, turn=2", 1),
            Transition(s1, s2, "P1 enters CS", 1),
            Transition(s2, s3, "P1 exits", 1),
            Transition(s0, s4, "P2 sets flag, turn=1", 2),
            Transition(s4, s5, "P2 enters CS", 2),
            Transition(s5, s3, "P2 exits", 2),
            # Contention scenarios
            Transition(s1, s6, "P2 requests (turn=1)", 2),
            Transition(s4, s7, "P1 requests (turn=2)", 1),
            Transition(s6, s8, "P2 enters (P1 waits)", 2),
            Transition(s7, s9, "P1 enters (P2 waits)", 1),
        ]

    def verify_mutual_exclusion(self) -> bool:
        """Verify no state violates mutual exclusion"""
        return all(not s.is_mutual_exclusion_violated() for s in self.states)


def generate_execution_trace(
    state_machine, path_indices: List[int]
) -> List[Tuple[SystemState, str]]:
    """
    Generate an execution trace following a specific path through the state machine.

    Args:
        state_machine: Either RaceConditionStateMachine or PetersonStateMachine
        path_indices: Indices of transitions to follow

    Returns:
        List of (state, action) tuples
    """
    trace = [(state_machine.states[0], "Initial state")]
    current_state = state_machine.states[0]

    for idx in path_indices:
        transition = state_machine.transitions[idx]
        if transition.from_state == current_state:
            trace.append((transition.to_state, transition.action))
            current_state = transition.to_state

    return trace
