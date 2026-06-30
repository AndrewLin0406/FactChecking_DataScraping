import subprocess, sys, time
from datetime import datetime
from pathlib import Path

# Run everything relative to the repository root.
PROJECT_ROOT = Path(__file__).resolve().parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
run_log_dir = LOG_DIR / run_timestamp
run_log_dir.mkdir(parents=True, exist_ok=True)

combined_log_path = run_log_dir / "pipeline.log"

PIPELINE_STEPS = [
    [
        sys.executable,
        "SCRIPTS/PolitiFact_RawScrape.py",
        "--limit",
        "-1"
    ],
    [
        sys.executable,
        "SCRIPTS/PolitiFact_ScrapeData.py"
    ]
]

def write_combined_log(message: str) -> None:
    """Write a message to both the terminal and the combined log."""
    print(message, flush=True)

    with combined_log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def run_step(step_number: int, command: list[str]) -> None:
    script_name = Path(command[1]).stem
    step_log_path = run_log_dir / f"{step_number:02d}_{script_name}.log"

    command_string = " ".join(command)
    start_time = time.time()

    write_combined_log("")
    write_combined_log("=" * 80)
    write_combined_log(f"Starting step {step_number}: {script_name}")
    write_combined_log(f"Command: {command_string}")
    write_combined_log(f"Step log: {step_log_path}")
    write_combined_log("=" * 80)

    with step_log_path.open("w", encoding="utf-8") as step_log:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        assert process.stdout is not None

        for line in process.stdout:
            print(line, end="", flush=True)
            step_log.write(line)
            step_log.flush()

            with combined_log_path.open("a", encoding="utf-8") as combined_log:
                combined_log.write(f"[{script_name}] {line}")
                combined_log.flush()

        return_code = process.wait()

    elapsed_time = time.time() - start_time

    if return_code != 0:
        write_combined_log(
            f"FAILED: {script_name} returned exit code {return_code} "
            f"after {elapsed_time:.1f} seconds."
        )
        raise subprocess.CalledProcessError(return_code, command)

    write_combined_log(
        f"Completed: {script_name} in {elapsed_time:.1f} seconds."
    )


def main() -> int:
    pipeline_start = time.time()

    write_combined_log(f"Pipeline started: {datetime.now().isoformat()}")
    write_combined_log(f"Project root: {PROJECT_ROOT}")
    write_combined_log(f"Python executable: {sys.executable}")
    write_combined_log(f"Logs: {run_log_dir}")

    try:
        for step_number, command in enumerate(PIPELINE_STEPS, start=1):
            run_step(step_number, command)

    except subprocess.CalledProcessError as error:
        write_combined_log("")
        write_combined_log("Pipeline stopped because a step failed.")
        write_combined_log(f"Failed command: {' '.join(error.cmd)}")
        return error.returncode

    elapsed_time = time.time() - pipeline_start

    write_combined_log("")
    write_combined_log(
        f"Pipeline completed successfully in {elapsed_time:.1f} seconds."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())