from flask import current_app
from website.models import User
from website import db
from getpass import getpass
from datetime import datetime


@current_app.cli.command("create_admin")
def create_admin():
    email = input("Enter email address: ")
    password = getpass("Enter password: ")
    confirm_password = getpass("Enter password again: ")
    username = input("Enter username: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    if password != confirm_password:
        print("Passwords don't match")
    else:
        try:
            user = User(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_admin=True,
                is_confirmed=True,
                confirmed_on=datetime.now(),
            )
            db.session.add(user)
            db.session.commit()
            print(f"Admin with email {email} created successfully!")
        except Exception:
            print("Couldn't create admin user.")
