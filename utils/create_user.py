import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

root_dir = Path(__file__).parent.parent  # Получаем путь к project/
sys.path.append(str(root_dir))

from database.core import crud, db, User


def create_user(username='admin', password='admin'):
    with db.connection_context():
        if crud.check_exists()(db, User, "username", username):
            raise Exception("Username already exists")
        try:
            user_id = crud.create()(db, User, {"username": username,
                                               "hashed_password":
                                                   generate_password_hash(
                                                       password)})
            return {"message": "User created", "user_id": user_id}
        except Exception as e:
            raise Exception(e)


if __name__ == "__main__":
    create_user()
