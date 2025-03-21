import os
import tempfile
from typing import List
from uuid import UUID

import pytest
from fastapi import Depends, FastAPI
from pydantic.types import PositiveInt
from starlette.testclient import TestClient

from tests.repositories import InMemoryBookRepository
from tests.schemas import Book, BookInDB
from tests.services import BookPaginationService


@pytest.fixture()
def a_book() -> Book:
    return Book(title="A nice title", author="John Smith")


@pytest.fixture()
def another_book() -> Book:
    return Book(title="Another nice title", author="Jane Boo")


@pytest.fixture
def app():
    app = FastAPI()

    @app.get("/", name="books:get-all-books")
    def get_all_books(
            books_repo: InMemoryBookRepository = Depends(InMemoryBookRepository),
    ) -> List[Book]:
        books = books_repo.list()
        return books

    @app.get("/{book_id}/", name="books:get-book-by-id")
    def get_book_by_id(
            book_id: UUID,
            books_repo: InMemoryBookRepository = Depends(InMemoryBookRepository),
    ) -> BookInDB | None:
        book = books_repo.get(book_id=book_id)
        return book

    @app.get("/books")
    def get_paginated_books(
            page_num: PositiveInt = 1,
            book_pagination: BookPaginationService = Depends(BookPaginationService)
    ):
        paginated_books = book_pagination.get_page(num=page_num)
        return paginated_books

    @app.post("/", name="books:create-book", status_code=201, response_model=BookInDB)
    def create_new_book(
            book: Book,
            books_repo: InMemoryBookRepository = Depends(InMemoryBookRepository)
    ) -> BookInDB:
        print(book)
        book_db = books_repo.add(book)
        return book_db

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(scope="session")
def tmp_settings_dir():
    yield tempfile.mkdtemp()


@pytest.fixture
def tmp_settings_file(tmp_settings_dir):
    file_path = os.path.join(tmp_settings_dir, 'dummy.env')
    with open(file_path, "w") as f:
        f.write("SECRET_KEY=secret key\n")
    yield file_path


@pytest.fixture
def dummy_env(tmp_settings_dir):
    file_path = os.path.join(tmp_settings_dir, 'dummy_test.env')
    with open(file_path, "w") as f:
        f.write("SECRET_KEY=another secret key\n")
    os.environ["DUMMY_ENV_FOR_TEST"] = "dummy_test"
    try:
        yield
    finally:
        del os.environ["DUMMY_ENV_FOR_TEST"]
