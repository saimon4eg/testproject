from sqlalchemy import Column, Integer


class IntIdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)
