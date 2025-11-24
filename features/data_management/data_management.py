
import csv
import json
import os
import shutil
import time
from datetime import datetime

from rich.console import Console
import questionary
from rich.prompt import Prompt

# Define project structure paths
DATABASE_DIR = "database"
TRANSACTIONS_FILE = os.path.join(DATABASE_DIR, "transactions.txt")
BUDGETS_FILE = os.path.join(DATABASE_DIR, "budgets.txt")
EXPORT_DIR = "exports"
BACKUP_DIR = "backups"

console = Console()



def _get_transactions():
    """Reads and returns all transactions from the file."""
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    with open(TRANSACTIONS_FILE, "r") as f:
        # Filter out empty lines before trying to parse JSON
        lines = [line for line in f if line.strip()]
        transactions = [json.loads(line) for line in lines]
    return transactions


def export_transactions_csv():
    """Exports all transactions to a CSV file."""
    transactions = _get_transactions()
    if not transactions:
        console.print("[yellow]No transactions to export.[/yellow]")
        return

    os.makedirs(EXPORT_DIR, exist_ok=True)
    file_path = os.path.join(EXPORT_DIR, f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        # Ensure all fieldnames are captured from all transactions
        fieldnames = set()
        for t in transactions:
            fieldnames.update(t.keys())

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(list(fieldnames)))
            writer.writeheader()
            writer.writerows(transactions)
        console.print(
            f"[green]Successfully exported transactions to {file_path}[/green]"
        )
    except IOError as e:
        console.print(f"[red]Error exporting to CSV: {e}[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")


def export_transactions_json():
    """Exports all transactions to a JSON file."""
    transactions = _get_transactions()
    if not transactions:
        console.print("[yellow]No transactions to export.[/yellow]")
        return

    os.makedirs(EXPORT_DIR, exist_ok=True)
    file_path = os.path.join(EXPORT_DIR, f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=4)
        console.print(
            f"[green]Successfully exported transactions to {file_path}[/green]"
        )
    except IOError as e:
        console.print(f"[red]Error exporting to JSON: {e}[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")


def import_transactions_csv():
    """Imports transactions from a CSV file."""
    file_path = Prompt.ask("Enter the path to the CSV file containing transactions")

    if not os.path.exists(file_path):
        console.print(f"[red]Error: File not found at '{file_path}'[/red]")
        return

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            new_transactions = [row for row in reader]
    except Exception as e:
        console.print(f"[red]An error occurred while reading the CSV file: {e}[/red]")
        return

    if not new_transactions:
        console.print("[yellow]No transactions found in the specified file.[/yellow]")
        return

    # --- Validation ---
    validated_transactions = []
    for i, t in enumerate(new_transactions, 1):
        if "amount" not in t or "description" not in t or "category" not in t or "type" not in t:
            console.print(
                f"[red]Invalid format in row {i}: Each transaction must have 'amount', 'description', 'category', and 'type'.[/red]"
            )
            return
        try:
            # Convert amount to paisa/cents
            t['amount'] = int(float(t['amount']) * 100)
        except (ValueError, TypeError):
            console.print(f"[red]Invalid amount in row {i}: '{t['amount']}' is not a valid number.[/red]")
            return
        # Add a default date if not present
        if 'date' not in t or not t['date']:
            t['date'] = datetime.now().strftime('%Y-%m-%d')
        validated_transactions.append(t)

    # --- Duplicate Check ---
    try:
        existing_transactions = _get_transactions()
        # Create a set of tuples for efficient duplicate checking
        existing_signatures = {
            (trans['date'], trans['description'], trans['amount'])
            for trans in existing_transactions
        }
    except Exception as e:
        console.print(f"[red]Could not read existing transactions for duplicate check: {e}[/red]")
        return
        
    unique_new_transactions = []
    for t in validated_transactions:
        signature = (t['date'], t['description'], t['amount'])
        if signature not in existing_signatures:
            unique_new_transactions.append(t)

    if not unique_new_transactions:
        console.print("[yellow]No new unique transactions found to import.[/yellow]")
        return

    console.print(f"Found [bold blue]{len(unique_new_transactions)}[/bold blue] new transactions to import.")
    
    confirmed = Prompt.ask("Do you want to proceed with the import?", choices=["y", "n"], default="y")
    
    if confirmed.lower() == 'y':
        try:
            with open(TRANSACTIONS_FILE, "a", encoding="utf-8") as f:
                for t in unique_new_transactions:
                    f.write(json.dumps(t) + "\n")
            console.print(
                f"[green]Successfully imported [bold]{len(unique_new_transactions)}[/bold] transactions.[/green]"
            )
        except IOError as e:
            console.print(f"[red]Error writing to the transactions file: {e}[/red]")



def backup_data():
    """Creates a timestamped backup of the data files."""
    if not os.path.exists(DATABASE_DIR):
        console.print("[red]Database directory not found. Nothing to back up.[/red]")
        return
        
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename_base = os.path.join(BACKUP_DIR, f"backup_{timestamp}")

    try:
        shutil.make_archive(backup_filename_base, 'zip', DATABASE_DIR)
        console.print(f"[green]Successfully created backup at [bold]{backup_filename_base}.zip[/bold][/green]")
    except Exception as e:
        console.print(f"[red]Error creating backup: {e}[/red]")
        return

    # --- Auto-cleanup old backups (keep last 10) ---
    try:
        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.endswith(".zip")],
            key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)),
            reverse=True,
        )
        if len(backups) > 10:
            num_to_delete = len(backups) - 10
            for old_backup in backups[10:]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))
            console.print(f"Removed {num_to_delete} old backup(s) to keep the last 10.")
    except Exception as e:
        console.print(f"[yellow]Could not clean up old backups: {e}[/yellow]")

def restore_data():
    """Restores data from a backup."""
    if not os.path.exists(BACKUP_DIR) or not os.listdir(BACKUP_DIR):
        console.print("[yellow]No backup directory found. Nothing to restore.[/yellow]")
        return

    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".zip")],
        key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)),
        reverse=True,
    )

    if not backups:
        console.print("[yellow]No backup files (.zip) found in the backup directory.[/yellow]")
        return

    selected_backup = questionary.select(
        "Choose a backup to restore (newest first):", choices=backups
    ).ask()

    if not selected_backup:
        console.print("Restore operation cancelled.")
        return

    backup_path = os.path.join(BACKUP_DIR, selected_backup)

    confirmed = questionary.confirm(
        f"This will ERASE all current data and replace it with the backup from '{selected_backup}'. This cannot be undone. Are you sure?",
        default=False
    ).ask()

    if confirmed:
        try:
            # Ensure the target directory is clean and exists
            if os.path.exists(DATABASE_DIR):
                shutil.rmtree(DATABASE_DIR)
            os.makedirs(DATABASE_DIR)

            # Extract the backup
            shutil.unpack_archive(backup_path, DATABASE_DIR, 'zip')
            console.print(f"[green]Successfully restored data from [bold]{selected_backup}[/bold][/green]")
        except Exception as e:
            console.print(f"[red]An error occurred during restore: {e}[/red]")
    else:
        console.print("Restore operation cancelled.")


def validate_data():
    """
    Validates the integrity of transaction and budget data files.
    Checks for valid JSON, required fields, and correct data types.
    Also offers to remove corrupted entries.
    """
    console.print("\n[bold cyan]Starting Data Integrity Check...[/bold cyan]")
    total_errors = 0
    
    # --- Validate Transactions File ---
    console.print(f"\n[bold]Checking [green]{TRANSACTIONS_FILE}[/green]...[/bold]")
    if not os.path.exists(TRANSACTIONS_FILE) or os.path.getsize(TRANSACTIONS_FILE) == 0:
        console.print("[yellow]Transaction file is missing or empty. Skipping.[/yellow]")
    else:
        valid_lines = []
        errors_in_file = 0
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                is_valid = True
                try:
                    data = json.loads(line)
                    required = ["date", "description", "amount", "category", "type"]
                    if not all(field in data for field in required):
                        errors_in_file += 1
                        console.print(f"  [red]Error L{i}:[/red] Missing required fields. Found: {list(data.keys())}")
                        is_valid = False
                    if not isinstance(data.get("amount"), int):
                        errors_in_file += 1
                        console.print(f"  [red]Error L{i}:[/red] 'amount' must be an integer. Found: {type(data.get('amount'))}")
                        is_valid = False
                    try:
                        if data.get("date"):
                            datetime.strptime(data["date"], "%Y-%m-%d")
                    except (ValueError, TypeError):
                        errors_in_file += 1
                        console.print(f"  [red]Error L{i}:[/red] 'date' is not a valid YYYY-MM-DD string. Found: {data.get('date')}")
                        is_valid = False
                except json.JSONDecodeError:
                    errors_in_file += 1
                    console.print(f"  [red]Error L{i}:[/red] Line is not valid JSON.")
                    is_valid = False
                
                if is_valid:
                    valid_lines.append(line)
        
        if errors_in_file > 0:
            total_errors += errors_in_file
            if questionary.confirm(f"Found {errors_in_file} errors in transactions. Remove corrupt entries?").ask():
                with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
                    f.writelines(valid_lines)
                console.print(f"[green]Removed {errors_in_file} corrupt entries from transactions.[/green]")

    # --- Validate Budgets File ---
    console.print(f"\n[bold]Checking [green]{BUDGETS_FILE}[/green]...[/bold]")
    if not os.path.exists(BUDGETS_FILE) or os.path.getsize(BUDGETS_FILE) == 0:
        console.print("[yellow]Budgets file is missing or empty. Skipping.[/yellow]")
    else:
        valid_lines = []
        errors_in_file = 0
        with open(BUDGETS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                is_valid = True
                try:
                    data = json.loads(line)
                    required = ["category", "amount"]
                    if not all(field in data for field in required):
                        errors_in_file += 1
                        console.print(f"  [red]Error L{i}:[/red] Missing required fields. Found: {list(data.keys())}")
                        is_valid = False
                    if not isinstance(data.get("amount"), int):
                        errors_in_file += 1
                        console.print(f"  [red]Error L{i}:[/red] 'amount' must be an integer. Found: {type(data.get('amount'))}")
                        is_valid = False
                except json.JSONDecodeError:
                    errors_in_file += 1
                    console.print(f"  [red]Error L{i}:[/red] Line is not valid JSON.")
                    is_valid = False
                
                if is_valid:
                    valid_lines.append(line)

        if errors_in_file > 0:
            total_errors += errors_in_file
            if questionary.confirm(f"Found {errors_in_file} errors in budgets. Remove corrupt entries?").ask():
                with open(BUDGETS_FILE, "w", encoding="utf-8") as f:
                    f.writelines(valid_lines)
                console.print(f"[green]Removed {errors_in_file} corrupt entries from budgets.[/green]")
    
    # --- Summary ---
    console.print("\n[bold cyan]Validation Complete.[/bold cyan]")
    if total_errors == 0:
        console.print("[bold green]✅ All data files appear to be valid.[/bold green]")
    else:
        console.print(f"[bold yellow]Finished with {total_errors} errors found.[/bold yellow]")
