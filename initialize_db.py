from app import app, db, User  # Import app, db, and the User model

# Initialize the database and add a default user
with app.app_context():
    db.create_all()  # Create all tables
    if not User.query.filter_by(username='seizer').first():  # Avoid duplicate users
        new_user = User(username='seizer', email='nathanasif@gmail.com')
        db.session.add(new_user)
        db.session.commit()
    print("Database initialized and user added!")