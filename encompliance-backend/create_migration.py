import os
import sys
import subprocess
from datetime import datetime

def create_migration():
    """Create a new Alembic migration for the database schema changes"""
    
    # Generate a timestamp for the migration message
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Migration message
    message = f"add_user_settings_table_{timestamp}"
    
    # Run alembic revision command
    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("Migration file created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e}")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_migration() 