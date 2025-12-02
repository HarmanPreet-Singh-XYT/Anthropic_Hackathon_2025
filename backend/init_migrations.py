"""
Initialize Alembic migrations for ScholarFit AI
Run this script once to set up the migration system
"""

import os
import sys
from pathlib import Path

def init_alembic():
    """Initialize Alembic migration environment"""
    
    print("🚀 Initializing Alembic migrations for ScholarFit AI")
    print("-" * 60)
    
    # Check if alembic directory already exists
    alembic_dir = Path("alembic")
    if alembic_dir.exists():
        response = input("⚠️  Alembic directory already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return False
    
    # Initialize Alembic
    print("\n📦 Running: alembic init alembic")
    os.system("alembic init alembic")
    
    # Update env.py to use our models
    env_py_path = alembic_dir / "env.py"
    if env_py_path.exists():
        print("\n📝 Updating alembic/env.py with database configuration...")
        
        env_content = '''from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import your models
from database import Base
from config.settings import settings

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        
        with open(env_py_path, 'w') as f:
            f.write(env_content)
        
        print("   ✓ Updated env.py")
    
    # Update alembic.ini to use environment variable
    alembic_ini_path = Path("alembic.ini")
    if alembic_ini_path.exists():
        print("\n📝 Updating alembic.ini...")
        
        with open(alembic_ini_path, 'r') as f:
            content = f.read()
        
        # Update sqlalchemy.url line
        lines = content.split('\n')
        updated_lines = []
        for line in lines:
            if line.startswith('sqlalchemy.url'):
                updated_lines.append('# sqlalchemy.url is set dynamically from settings.py')
                updated_lines.append('sqlalchemy.url = ')
            else:
                updated_lines.append(line)
        
        with open(alembic_ini_path, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("   ✓ Updated alembic.ini")
    
    print("\n" + "=" * 60)
    print("✅ Alembic initialization complete!")
    print("\nNext steps:")
    print("  1. Ensure PostgreSQL is running: docker-compose up -d")
    print("  2. Create initial migration: alembic revision --autogenerate -m 'Initial schema'")
    print("  3. Apply migration: alembic upgrade head")
    print("=" * 60)
    
    return True


def create_initial_migration():
    """Create the initial migration"""
    print("\n🔨 Creating initial migration...")
    
    # Check if database is accessible
    try:
        from config.settings import settings
        print(f"   Database URL: {settings.database_url}")
        
        # Test connection
        from database import DatabaseManager
        db_manager = DatabaseManager(settings.database_url)
        db = next(db_manager.get_session())
        print("   ✓ Database connection successful")
        db.close()
        
    except Exception as e:
        print(f"   ✗ Database connection failed: {e}")
        print("\n   Make sure PostgreSQL is running:")
        print("   docker-compose up -d")
        return False
    
    # Create migration
    print("\n📦 Running: alembic revision --autogenerate -m 'Initial schema'")
    result = os.system("alembic revision --autogenerate -m 'Initial schema'")
    
    if result == 0:
        print("\n   ✓ Migration created successfully")
        return True
    else:
        print("\n   ✗ Migration creation failed")
        return False


def apply_migrations():
    """Apply all pending migrations"""
    print("\n🚀 Applying migrations...")
    print("📦 Running: alembic upgrade head")
    
    result = os.system("alembic upgrade head")
    
    if result == 0:
        print("\n   ✓ Migrations applied successfully")
        return True
    else:
        print("\n   ✗ Migration application failed")
        return False


def full_setup():
    """Run full setup: init, create migration, apply"""
    print("=" * 60)
    print("   ScholarFit AI - Database Setup")
    print("=" * 60)
    
    # Step 1: Initialize Alembic
    if not init_alembic():
        return False
    
    # Step 2: Create initial migration
    input("\nPress Enter to create initial migration (make sure PostgreSQL is running)...")
    if not create_initial_migration():
        return False
    
    # Step 3: Apply migrations
    input("\nPress Enter to apply migrations...")
    if not apply_migrations():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Database setup complete!")
    print("\nYou can now start the API server:")
    print("   python api.py")
    print("=" * 60)
    
    return True


def show_menu():
    """Show interactive menu"""
    print("\n" + "=" * 60)
    print("   ScholarFit AI - Database Migration Setup")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Full setup (init + create migration + apply)")
    print("  2. Initialize Alembic only")
    print("  3. Create initial migration")
    print("  4. Apply migrations")
    print("  5. Exit")
    print("-" * 60)
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        full_setup()
    elif choice == '2':
        init_alembic()
    elif choice == '3':
        create_initial_migration()
    elif choice == '4':
        apply_migrations()
    elif choice == '5':
        print("Goodbye!")
        return
    else:
        print("Invalid option")
        show_menu()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'full':
            full_setup()
        elif command == 'init':
            init_alembic()
        elif command == 'create':
            create_initial_migration()
        elif command == 'apply':
            apply_migrations()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python init_migrations.py [full|init|create|apply]")
    else:
        show_menu()