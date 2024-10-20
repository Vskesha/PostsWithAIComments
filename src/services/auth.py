import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.conf.config import settings
from src.database.db import get_db
from src.database.redis import redis_db
from src.repository.users import db_user_repo, redis_user_repo


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


class AuthService:
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a new access token.

        Args:
            self: Refer to the current instance of a class
            data (dict): A dictionary containing the claims to be encoded in the JWT.
            expires_delta (Optional[float]): An optional parameter specifying how long, in seconds,
            the access token should last before expiring. If not specified, it defaults to 15 minutes.

        Returns:
            A jwt token
        """
        to_encode = data.copy()
        expires_delta = expires_delta or 60 * 60
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

        :param self: Make the function a method of the class
        :param data: dict: Pass in the user's id, which is used to create a unique refresh token for each user
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token
        """
        to_encode = data.copy()
        expires_delta = expires_delta or 7 * 24 * 60 * 60
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        The decode_refresh_token function is used to decode the refresh token.
            The function will first try to decode the refresh token using JWT. If it succeeds,
            then it will check if the scope of that token is 'refresh_token'. If so, then we know
            that this is a valid refresh token and we can return its email address (which was stored in sub).

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that we want to decode
        :return: The email of the user associated with the refresh token
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.INVALID_SCOPE,
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.COULD_NOT_VALIDATE_CREDENTIALS,
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            if it's valid, or raises an HTTPException with status code 401 if not.

        :param self: Make the function a method of the class
        :param token: str: Get the token from the authorization header
        :param db: Session: Get the database session
        :return: The user object of the logged in user
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.COULD_NOT_VALIDATE_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

        # blocked = await self.token_is_blocked(token)
        # if blocked:
        #     raise credentials_exception

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as err:
            raise credentials_exception

        # user = await redis_user_repo.get_user_by_email(email, redis_db)
        # if user is None:
        #     user = await db_user_repo.get_user_by_email(email, db)
        #     if user is None:
        #         raise credentials_exception
        #     body = {"email": email, "user": user}
        #     await redis_user_repo.create_user(body, redis_db)
        #
        # if not user.status_active:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail=messages.USER_IS_BANNED,
        #     )

        user = await db_user_repo.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def block_token(self, token: str) -> None:
        """
        Blocks a token by adding it to a Redis set.
        """
        await redis_db.set(token, True)
        await redis_db.expire(token, 7 * 24 * 60 * 60)

    async def token_is_blocked(self, token: str) -> bool:
        """
        Checks if token is in blocked list.
        """
        result = await redis_db.get(token)
        return bool(result)


    # def create_email_token(self, data: dict):
    #     """
    #     The create_email_token function takes a dictionary of data and returns a JWT token.
    #     The token is encoded with the SECRET_KEY and ALGORITHM defined in the class, as well as an expiration date 7 days from now.
    #     The scope of this token is &quot;email_token&quot;.
    #
    #     :param self: Make the function a method of the user class
    #     :param data: dict: Pass in the data that will be encoded into a jwt
    #     :return: A token that is encoded with the user's email and a scope of &quot;email_token&quot;
    #     """
    #     to_encode = data.copy()
    #     expire = datetime.utcnow() + timedelta(days=7)
    #     to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
    #     token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    #     return token
    #
    # def get_email_from_token(self, token: str):
    #     """
    #     The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
    #     It does this by decoding the JWT using our secret key, then checking to make sure it's a valid email verification token.
    #     If so, it returns the email address from the payload.
    #
    #     :param self: Represent the instance of the class
    #     :param token: str: Pass the token that is sent to the user's email address
    #     :return: The email address of the user who is trying to verify their account
    #     """
    #     try:
    #         payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
    #         if payload["scope"] == "email_token":
    #             email = payload["sub"]
    #             return email
    #     except JWTError as e:
    #         # print(e)
    #         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #                             detail="Invalid token for email verification")
    #
    # async def token_check(self, payload: dict, token_type: str = 'access_token') -> str:
    #     """
    #     The token_check function is used to validate the token that was sent with the request.
    #         It will check if it's an access_token or a refresh_token, and then return the email address of
    #         who owns that token. If it fails to find an email address, or if there is no scope in the payload,
    #         then we raise a 401 Unauthorized error.
    #
    #     :param self: Represent the instance of the class
    #     :param payload: dict: Pass in the token payload
    #     :param token_type: str: Check if the token is an access_token or a refresh_token
    #     :return: The email address of the user
    #     :doc-author: Trelent
    #     """
    #     if payload['scope'] == token_type:
    #         email = payload['sub']
    #         if email is None:
    #             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    #     else:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    #
    #     return email
    #
    # async def logout_user(self,
    #         token: str = Depends(oauth2_scheme),
    #         db: Session = Depends(get_db)
    # ) -> None:
    #     try:
    #         payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
    #         email = await self.token_check(payload, token_type='access_token')
    #         print("Before invalidation:", self.invalid_tokens)
    #         await self.invalidate_token(token)
    #         print("After invalidation:", self.invalid_tokens)
    #     except:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    #
    #     now = datetime.timestamp(datetime.now())
    #     time_delta = payload['exp'] - now + 300
    #     self.r.set(token, 'True')
    #     self.r.expire(token, int(time_delta))
    #
    #     user = await repository_users.get_user_by_email(email, db)
    #     user.refresh_token = None
    #     db.commit()
    #     db.refresh(user)
    #
    # async def clear_user_cash(self, user_email) -> None:
    #     """
    #     The clear_user_cash function deletes the user's cash from the Redis database.
    #         Args:
    #             user_email (str): The email of the user whose cash is to be deleted.
    #
    #     :param self: Represent the instance of the class
    #     :param user_email: Identify the user in the database
    #     :return: None
    #     :doc-author: Trelent
    #     """
    #     self.r.delete(f"user:{user_email}")


password_manager = PasswordManager()
auth_service = AuthService()
