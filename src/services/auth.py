import secrets
import string

from passlib.context import CryptContext


class PasswordManager:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Represent the instance of the class
        :param plain_password: Store the password that is entered by the user
        :param hashed_password: Compare the hashed password in the database with the plaintext password entered by a user
        :return: A boolean value
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Get the password that is being hashed
        :return: A string that is the hashed password
        """
        return self.pwd_context.hash(password)

    def get_new_password(
        self, password_length: int = 12, meeting_limit: int = 3
    ) -> str:
        """
        The get_new_password function generates a random password of length 12 characters.
        The password must contain at least 3 digits and 1 special character.


        :param self: Refer to the instance of the class
        :param password_length: int: Set the length of the password
        :param meeting_limit: int: Set the minimum number of digits that must be present in the password
        :return: A new password that meets the following criteria:
        :doc-author: Trelent
        """
        letters = string.ascii_letters
        digits = string.digits
        special_chars = string.punctuation
        alphabet = letters + digits + special_chars

        while True:
            pwd = "".join(secrets.choice(alphabet) for _ in range(password_length))

            if (
                any(char in special_chars for char in pwd)
                and sum(char in digits for char in pwd) >= meeting_limit
            ):
                break

        return pwd


password_manager = PasswordManager()
