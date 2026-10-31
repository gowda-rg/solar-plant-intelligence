# SEMANTIC — ORM foundation
# All persistent tables inherit from this Base so one `create_all()` can build the schema.
# IN:  SQLAlchemy model classes (PlantReading, QualityEvent, …)
# OUT: PostgreSQL tables matching those class definitions
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
