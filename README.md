# Task 3

This task is a group project aimed at creating a Python script that handles CSV and JSON data within a complex directory structure.

### Directory Structure & Task Requirements

The script operates on a nested directory structure with four levels:
1. Directories named after **months** (e.g., January, February).
2. Subdirectories named after **days of the week** (e.g., Monday, Tuesday).
3. Subdirectories representing **morning/evening**.
4. Actual **data files** in CSV or JSON format.

### Options

The user is able to specify:
- **Months:** Choose one or more months.
- **Days:** Define a range of days for each month.
- **Time of Day:** Specify either morning or evening (morning is default).
- **Operation Mode:** Choose reading (default) or creation (`--create`).
- **File Format:** Choose CSV (default) or JSON (`--json`).

For each specified combination of month, day, and time, the script generates an appropriate directory structure and reads/creates data files.

### Example Use
`python3 main.py --months Jan Mar Feb --days Mon-Wed Fri Tue-Sat --times m m e --create`

### Division of Responsibilities
- **Person 1 (Wiktor Kotala):**
  - Implementation of script-level logic, handling **parameters** using `argparse` library.
  - Debugging and synchronization of individual functions.
- **Person 2 (Tymoteusz Ziarek):**
  - Generating **directory paths**.
  - Delegating creating/reading data files at those paths to other functions.
- **Person 3 (Piotr Stolarczyk):**
  - Implementation of **CSV** file writing and reading logic.
  - Creation and management of the GitHub repository.
- **Person 4 (Antoni Sierka):**
  - Implementation of **JSON** file writing and reading logic.
