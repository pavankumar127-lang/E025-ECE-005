# ECE-005: Prepaid IoT SIM Pooled Data Pack Engine

import os
from datetime import datetime
from engine import PooledDataEngine

# Create the engine
engine = PooledDataEngine()

# Get the project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read_commands(filename):
    """Read commands from commands.txt."""

    commands = []
    file_path = os.path.join(BASE_DIR, filename)

    with open(file_path, "r", encoding="utf-8-sig") as file:
        for line_no, line in enumerate(file, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split("|")
            commands.append((line_no, parts))

    return commands


def load_input_files(commands):
    """Load all input CSV files before processing commands."""

    for line_no, command in commands:
        action = command[0]

        if action == "LOAD_ACCOUNTS":
            engine.load_accounts(
                os.path.join(BASE_DIR, command[1])
            )
            print("Accounts loaded successfully!")

        elif action == "LOAD_SIMS":
            engine.load_sims(
                os.path.join(BASE_DIR, command[1])
            )
            print("SIMs loaded successfully!")

        elif action == "LOAD_PACK_TYPES":
            engine.load_pack_types(
                os.path.join(BASE_DIR, command[1])
            )
            print("Pack types loaded successfully!")

        elif action == "LOAD_USAGE":
            engine.load_usage(
                os.path.join(BASE_DIR, command[1])
            )
            print("Usage records loaded successfully!")


def get_command_date(action, command):
    """Return the date associated with a command."""

    if action == "BUY_PACK":
        return command[3]

    elif action in ("ACTIVATE", "SUSPEND", "RESUME"):
        return command[2]

    elif action == "REGISTER_SIM":
        return command[4]

    return None


def execute_command(line_no, command):
    """Execute one dated command."""

    action = command[0]

    try:
        if action == "BUY_PACK":
            engine.buy_pack(
                command[1],
                command[2],
                command[3],
                line_no
            )

        elif action == "ACTIVATE":
            engine.activate_sim(
                command[1],
                command[2]
            )

        elif action == "SUSPEND":
            engine.suspend_sim(command[1], command[2], line_no)

        elif action == "RESUME":
            engine.resume_sim(
                command[1],
                command[2]
            )

        elif action == "REGISTER_SIM":
            engine.register_sim(
                command[1],
                command[2],
                command[3],
                command[4]
            )

        else:
            engine.add_error(
                "commands.txt",
                line_no,
                "UNKNOWN_COMMAND"
            )

    except (ValueError, IndexError, KeyError) as error:
        engine.add_error(
            "commands.txt",
            line_no,
            str(error)
        )


def process_commands(commands):
    """Process commands and usage in chronological order."""

    dated_commands = []
    statement_commands = []

    # Separate dated commands and statement commands.
    for line_no, command in commands:

        action = command[0]

        if action.startswith("LOAD_"):
            continue

        elif action == "STATEMENT":
            statement_commands.append((line_no, command))

        else:
            command_date = get_command_date(action, command)

            if command_date:
                dated_commands.append(
                    (command_date, line_no, command)
                )

            else:
                engine.add_error(
                    "commands.txt",
                    line_no,
                    "UNKNOWN_COMMAND"
                )

    # Collect all dates from commands and usage records.
    processing_dates = set()

    for command_date, line_no, command in dated_commands:
        processing_dates.add(command_date)

    for row in engine.pending_usage:
        processing_dates.add(row["date"])

    # Process each date in chronological order.
    for current_date in sorted(processing_dates):

        print("\nProcessing date:", current_date)

        # Execute all commands for this date first.
        for command_date, line_no, command in dated_commands:

            if command_date == current_date:
                execute_command(line_no, command)

        # Process that day's usage and create pool logs.
        engine.process_day(current_date)

    # Generate statements after all usage has been processed.
    for line_no, command in statement_commands:

        try:
            engine.create_statement(
                command[1],
                command[2],
                command[3]
            )

        except (ValueError, IndexError, KeyError) as error:
            engine.add_error(
                "commands.txt",
                line_no,
                str(error)
            )


def export_output_files():
    """Generate all required output CSV files."""

    engine.export_sim_states(
        os.path.join(BASE_DIR, "sim_states.csv")
    )

    engine.export_errors(
        os.path.join(BASE_DIR, "errors.csv")
    )

    engine.export_pool_log(
        os.path.join(BASE_DIR, "pool_log.csv")
    )

    engine.export_statements(
        os.path.join(BASE_DIR, "statements.csv")
    )


def main():

    print("======================================")
    print(" ECE-005 Pooled Data Pack Engine")
    print("======================================")

    # Read the command file.
    commands = read_commands("commands.txt")

    # Load the input files.
    load_input_files(commands)

    # Execute commands and process daily usage.
    process_commands(commands)

    # Export the final output files.
    export_output_files()

    print("\n======================================")
    print(" APPLICATION COMPLETED SUCCESSFULLY")
    print("======================================")


if __name__ == "__main__":
    main()