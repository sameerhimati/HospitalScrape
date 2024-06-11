from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from .config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

logger = logging.getLogger(__name__)

Base = declarative_base()

class HospitalUrl(Base):
    __tablename__ = 'hospital_urls'
    id = Column(Integer, primary_key=True)
    hospital_name = Column(String, nullable=False)
    hospital_url = Column(Text, nullable=False)
    last_fetched = Column(DateTime)
    status = Column(String(50))

class WebPage(Base):
    __tablename__ = 'web_pages'
    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey('hospital_urls.id'), nullable=False)
    page_url = Column(Text, nullable=False)
    content = Column(Text)
    relevance_score = Column(Float)
    fetched_at = Column(DateTime, nullable=False)

class WaitTime(Base):
    __tablename__ = 'wait_times'
    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey('hospital_urls.id'), nullable=False)
    wait_time = Column(Integer, nullable=False)
    fetched_at = Column(DateTime, nullable=False)

url = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
engine = create_engine(url)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def drop_tables():
    Base.metadata.drop_all(engine)

def save_web_page(hospital_id, page_url, content, relevance_score):
    session = Session()
    try:
        web_page = WebPage(
            hospital_id=hospital_id,
            page_url=page_url,
            content=content,
            relevance_score=relevance_score,
            fetched_at=datetime.now()
        )
        session.add(web_page)
        session.commit()
    except Exception as e:
        logger.error(f"Failed to save web page: {e}")
        session.rollback()
    finally:
        session.close()

def update_last_fetched(hospital_id):
    session = Session()
    try:
        hospital_url = session.query(HospitalUrl).filter(HospitalUrl.id == hospital_id).one()
        hospital_url.last_fetched = datetime.now()
        session.commit()
    except Exception as e:
        logger.error(f"Failed to update last fetched: {e}")
        session.rollback()
    finally:
        session.close()

def get_unprocessed_urls():
    session = Session()
    try:
        urls = session.query(HospitalUrl.id, HospitalUrl.hospital_url).filter(HospitalUrl.last_fetched == None).all()
        return urls
    except Exception as e:
        logger.error(f"Failed to fetch unprocessed URLs: {e}")
        return []
    finally:
        session.close()

def save_wait_time(hospital_id, wait_time):
    session = Session()
    try:
        wait_time_record = WaitTime(
            hospital_id=hospital_id,
            wait_time=wait_time,
            fetched_at=datetime.now()
        )
        session.add(wait_time_record)
        session.commit()
    except Exception as e:
        logger.error(f"Failed to save wait time: {e}")
        session.rollback()
    finally:
        session.close()
