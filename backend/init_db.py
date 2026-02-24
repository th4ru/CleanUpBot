from app import db, create_app
from models import SystemPC  # assuming your models file is models.py

app = create_app()  # make sure this returns your Flask app instance

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ All tables created successfully!")

    # Check if your PC is already added
    existing_pc = SystemPC.query.filter_by(pc_name="MyLocalMachine").first()
    if not existing_pc:
        # Add your PC
        my_pc = SystemPC(
            pc_name="MyLocalMachine",
            ip_address="10.20.10.168",
            ssh_port=22,
            username="dcs-user",
            password="CompUser123@",
            status="offline"
        )
        db.session.add(my_pc)
        db.session.commit()
        print("✅ PC added successfully!")
    else:
        print("ℹ️ PC already exists.")