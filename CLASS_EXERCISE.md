# Class Exercise: Installing and Observing a Python Package

Goal: understand what changes when a project is installed as a package, where code is imported from, and how virtualenv and Docker isolate Python environments.

## Part 1: Inspect the Project

Open these files and answer:

- `pyproject.toml`: What is the package name on install?
- `src/dir_monitor_exellenteam/__init__.py`: What does this package expose as its public API?
- `src/dir_monitor_exellenteam/__main__.py`: Why can we run the package with `python -m dir_monitor_exellenteam`?
- `src/dir_monitor_exellenteam/import_examples.py`: Which imports are relative, and which are absolute?

## Part 2: Local Editable Install

Run:

```bash
./scripts/install_local.sh
```

Look for this section in the output:

```text
=== Installation Location Comparison ===
```

Answer:

- Where is `dir_monitor_exellenteam` imported from?
- Where are `humanize` and `colorama` imported from?
- What does `direct_url.json` tell us about the local package?

Key idea: with `pip install -e .`, package metadata lives in the virtualenv, but the package code is imported from this repo's `src/` folder.

## Part 2B: External Install Picker Script

Run:

```bash
python scripts/install_picker_and_show_paths.py --mode local-dev
```

Answer:

- Which virtualenv did the script create?
- Where is the console command installed?
- Which paths belong to this local package, and which paths belong to packages downloaded from PyPI?

Key idea: an external script can create a virtualenv, install the package, and inspect the installed paths without being part of the import package itself.

## Part 3: Change Code and Observe Editable Behavior

Activate the local virtualenv:

```bash
source .venv/bin/activate
```

Run:

```bash
dir-monitor-exellenteam --version
python examples/04_relative_vs_absolute_imports.py
```

Now edit this line in `src/dir_monitor_exellenteam/import_examples.py`:

```python
f"Relative import used .formatting: {relative_human_duration(3)}",
```

Change the text to something obvious, for example:

```python
f"Relative import from local editable source: {relative_human_duration(3)}",
```

Run again:

```bash
python examples/04_relative_vs_absolute_imports.py
```

Question:

- Did the output change without reinstalling?

Expected result: yes. Editable installs point Python back to the local source files.

## Part 4: Non-Editable Virtualenv Install

Run:

```bash
./scripts/demo_virtualenv_install.sh
```

This creates `.venv-compare` and installs with:

```bash
python -m pip install .
```

Activate it:

```bash
source .venv-compare/bin/activate
```

Check where the package is imported from:

```bash
python -c "import dir_monitor_exellenteam; print(dir_monitor_exellenteam.__file__)"
```

Question:

- Is it importing from `src/`, or from `.venv-compare/.../site-packages`?

Now change the same line in `src/dir_monitor_exellenteam/import_examples.py` again and run:

```bash
python -c "from dir_monitor_exellenteam import describe_import_styles; print(*describe_import_styles(), sep='\n')"
```

Question:

- Did the output change immediately?

Expected result: no. A regular install copies/builds the package into `site-packages`. You must reinstall to pick up source changes:

```bash
python -m pip install .
```

## Part 5: Docker Install

Run:

```bash
./scripts/demo_docker_install.sh
```

Find the `pip show` output.

Answer:

- Where is the package installed inside the container?
- Which Python executable is used inside the container?
- How is that different from a virtualenv?

Key idea: virtualenv isolates Python packages on your computer. Docker isolates a fuller runtime environment, including its own filesystem and Python interpreter.

## Part 6: Logging Behavior

Run:

```bash
source .venv/bin/activate
rm -f changes.log watched_demo/student-log-test.txt
dir-monitor-exellenteam ./watched_demo --timeout 10 --interval 0.5 --log-level DEBUG --log-file changes.log
```

While it runs, create or edit a file inside `watched_demo`. For example, in a second terminal:

```bash
printf "student change\n" > watched_demo/student-log-test.txt
```

If you want a one-terminal version for practice, run this instead:

```bash
rm -f changes.log watched_demo/student-log-test.txt
(sleep 1; printf "student change\n" > watched_demo/student-log-test.txt) &
dir-monitor-exellenteam ./watched_demo --timeout 5 --interval 0.5 --log-level DEBUG --log-file changes.log
```

Then inspect:

```bash
cat changes.log
```

Answer:

- Which log levels appear?
- What changes when you run with `--log-level WARNING`?
- Does the log file contain the same events that appeared in the terminal?

## Stretch

Run one test layer at a time:

```bash
./scripts/run_tests.sh -m unit
./scripts/run_tests.sh -m integration
./scripts/run_tests.sh -m system
```

Question:

- Which tests use mocks?
- Which tests use the real filesystem?
- Which tests run the package through a subprocess like a real user?

## Part 7: Debugging Tests and Understanding Mocks

Goal: see what mocks replace, what real behavior remains, and how a failing test points you to the problem.

Before starting, make sure the baseline is green:

```bash
./scripts/run_tests.sh
```

### Debug 1: Break a Pure Unit Test

Open `src/dir_monitor_exellenteam/monitor.py`.

Temporarily change this line inside `ChangeEvent.to_log_line()`:

```python
return f"{self.event_type.upper():8} {item_type}: {self.path}"
```

to:

```python
return f"{self.event_type} {item_type}: {self.path}"
```

Run:

```bash
./scripts/run_tests.sh -m unit
```

Questions:

- Which test failed?
- Did this test need real files on disk?
- Why is this a unit test?

Restore the original line before continuing.

### Debug 2: See What a Mock Replaces

Open `tests/unit/test_monitor.py`.

Find:

```python
with patch("dir_monitor_exellenteam.monitor.iter_directory_changes", return_value=iter([event])) as changes:
```

This mock replaces the real polling loop. The test does not wait for files to change; it supplies one fake event.

Temporarily change:

```python
event = ChangeEvent("created", tmp_path / "created.txt")
```

to:

```python
event = ChangeEvent("deleted", tmp_path / "created.txt")
```

Run:

```bash
./scripts/run_tests.sh tests/unit/test_monitor.py::test_monitor_directory_logs_events_from_mocked_iterator
```

Expected result: this test still passes, because the fake event supplied by the mock changed too.

Questions:

- Did the test touch the real filesystem to delete a file?
- Why did the logged event change anyway?
- What does the mock control?

Restore the original event type before continuing.

### Debug 3: Break CLI Argument Passing

Open `src/dir_monitor_exellenteam/cli.py`.

Temporarily change:

```python
recursive=not args.non_recursive,
```

to:

```python
recursive=True,
```

Run:

```bash
./scripts/run_tests.sh tests/unit/test_cli.py::test_main_passes_parsed_arguments_to_library_api
```

Questions:

- Why does this test fail without monitoring a real directory?
- What function is mocked?
- What does `assert_called_once_with(...)` prove?

Restore the original line before continuing.

### Debug 4: Compare Mocked Tests with Integration Tests

Run this integration test:

```bash
./scripts/run_tests.sh tests/integration/test_monitor_integration.py::test_iter_directory_changes_detects_file_lifecycle
```

Questions:

- Does this test use real files?
- Why does it use `tmp_path`?
- Why is it slower than the unit tests?

Now compare it with:

```bash
./scripts/run_tests.sh tests/unit/test_monitor.py::test_monitor_directory_logs_events_from_mocked_iterator
```

Question:

- Which test gives more confidence about the real directory monitor?
- Which test is easier to debug when the logging code breaks?

### Debug 5: System Test as a Real User

Run:

```bash
./scripts/run_tests.sh tests/system/test_cli_system.py::test_cli_writes_event_log_file_for_created_file
```

Questions:

- Why does this test use `subprocess.Popen`?
- What makes it a system test?
- Which parts are real: CLI parsing, logging, filesystem, process boundary?

### Debug 6: Mock the Installer Script

Open `tests/system/test_install_picker_system.py`.

Find:

```python
with patch.object(subprocess, "run", side_effect=fake_run) as run:
```

Question:

- Why do we mock `subprocess.run` here?

Answer: because the test wants to verify which commands would be run without actually creating virtualenvs or reinstalling packages.

Temporarily add this line inside `fake_run`:

```python
print(command)
```

Run:

```bash
./scripts/run_tests.sh tests/system/test_install_picker_system.py::test_install_picker_local_dev_mode_runs_commands_in_order -s
```

Question:

- Which commands would the script have run?

Remove the temporary `print(command)` when done.

### Final Check

After restoring all temporary changes:

```bash
./scripts/run_tests.sh
```

Expected result:

```text
32 passed
```
