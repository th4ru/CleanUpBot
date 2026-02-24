# test_ssh_cleanup.py
import logging
from app import create_app, db
from models import SystemPC
from ssh_executor import SSHExecutor, CommandBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app and push app context
app = create_app()
with app.app_context():
    # Fetch your PC from the database
    system = SystemPC.query.filter_by(pc_name="MyLocalMachine").first()
    if not system:
        logger.error("System not found in database")
        exit(1)

    logger.info(f"Preparing SSH connection to {system.pc_name} ({system.ip_address})")

    executor_config = {
        "hostname": system.ip_address,
        "username": system.username,
        "password": system.password,
        "private_key_path": system.private_key_path,
        "port": system.ssh_port
    }

    executor = SSHExecutor(**executor_config)
    if executor.connect():
        logger.info(f"Connected to {system.pc_name} ({system.ip_address})")

        # Get system info
        code, out, err = executor.execute_command(CommandBuilder.get_system_info())
        print("\n--- SYSTEM INFO ---")
        print(out)
        if err:
            print("Error:", err)

        # Clean cache with sudo password
        code, out, err = executor.execute_command(CommandBuilder.clean_cache(), sudo_password=system.password)
        print("\n--- CLEAN CACHE ---")
        print("Return code:", code)
        print("Stdout:", out)
        print("Stderr:", err)

        executor.disconnect()
    else:
        logger.error("SSH connection failed")