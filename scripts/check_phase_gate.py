"""check_phase_gate.py — Validate phase-gate FSM transitions.

Purpose:
    Given a current FSM state and an event, determine whether the transition
    is valid per the FSM definition in data/phase-gate-fsm.yml.

Inputs:
    --state STATE       Current FSM state name (required unless --list-states)
    --event EVENT       Event to check against the state's transitions (optional)
    --list-states       Print all valid state names and exit
    --fsm-file PATH     Path to the FSM YAML file (default: data/phase-gate-fsm.yml)

Outputs:
    VALID:   <state> --[<event>]--> <next_state>
    INVALID: state <state> has no transition for event <event>
    Or a list of events/states when no event is provided.

Usage examples:
    uv run python scripts/check_phase_gate.py --state PHASE_RUNNING --event phase_deliverable_returned
    uv run python scripts/check_phase_gate.py --state INIT
    uv run python scripts/check_phase_gate.py --list-states
    uv run python scripts/check_phase_gate.py --fsm-file path/to/fsm.yml --list-states

Exit codes:
    0  Valid transition, successful listing, or list-states ok
    1  Invalid transition or unknown state
    2  FSM file not found
"""

import argparse
import sys
from pathlib import Path

import yaml

DEFAULT_FSM_FILE = "data/phase-gate-fsm.yml"


def load_fsm(fsm_file: str) -> dict:
    """Load and return the FSM definition from the YAML file."""
    path = Path(fsm_file)
    if not path.exists():
        print(f"ERROR: FSM file not found: {fsm_file}", file=sys.stderr)
        sys.exit(2)
    with path.open() as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(
                f"ERROR: Failed to parse FSM YAML file {fsm_file}: {e}",
                file=sys.stderr,
            )
            sys.exit(2)
    if not isinstance(data, dict):
        print(
            f"ERROR: FSM YAML file {fsm_file} must contain a mapping at the top level.",
            file=sys.stderr,
        )
        sys.exit(2)
    return data


def get_states(fsm_data: dict) -> dict:
    """Return the states dict from the FSM definition."""
    return fsm_data.get("fsm", {}).get("states", {})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate phase-gate FSM transitions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--state",
        metavar="STATE",
        help="Current FSM state name",
    )
    parser.add_argument(
        "--event",
        metavar="EVENT",
        help="Event to check against the state's transitions",
    )
    parser.add_argument(
        "--list-states",
        action="store_true",
        help="Print all valid state names and exit 0",
    )
    parser.add_argument(
        "--fsm-file",
        metavar="PATH",
        default=DEFAULT_FSM_FILE,
        help=f"Path to the FSM YAML file (default: {DEFAULT_FSM_FILE})",
    )
    args = parser.parse_args()

    fsm_data = load_fsm(args.fsm_file)
    states = get_states(fsm_data)

    # --list-states: print all state names and exit 0
    if args.list_states:
        for state_name in states:
            print(state_name)
        sys.exit(0)

    if not args.state:
        parser.print_help()
        sys.exit(1)

    state_name = args.state
    if state_name not in states:
        print(f"INVALID: unknown state '{state_name}'", file=sys.stderr)
        sys.exit(1)

    state_def = states[state_name]
    transitions = state_def.get("transitions") or []

    # --state only (no --event): list all valid events for that state
    if not args.event:
        if not transitions:
            print(f"State '{state_name}' has no outgoing transitions (terminal state).")
        else:
            print(f"Valid events for state '{state_name}':")
            for t in transitions:
                event = t.get("event", "<unknown>")
                next_state = t.get("next_state", "<unknown>")
                guard = t.get("guard")
                guard_note = f"  [guard: {guard}]" if guard else ""
                print(f"  {event} --> {next_state}{guard_note}")
        sys.exit(0)

    # --state + --event: check if transition exists
    event_name = args.event
    for t in transitions:
        if t.get("event") == event_name:
            next_state = t.get("next_state", "<unknown>")
            guard = t.get("guard")
            if guard:
                print(f"VALID: {state_name} --[{event_name}]--> {next_state}  [guard: {guard}]")
            else:
                print(f"VALID: {state_name} --[{event_name}]--> {next_state}")
            sys.exit(0)

    print(f"INVALID: state '{state_name}' has no transition for event '{event_name}'")
    sys.exit(1)


if __name__ == "__main__":
    main()
