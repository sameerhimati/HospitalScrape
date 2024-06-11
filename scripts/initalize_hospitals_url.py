from src.database import Session, HospitalUrl

def initialize_hospital_urls(engine):
    session = Session(bind=engine)
    try:
        # Insert hospital URLs into the database
        session.add_all([
            HospitalUrl(hospital_name='Hospital A', hospital_url='https://www.hospitalA.com'),
            HospitalUrl(hospital_name='Hospital B', hospital_url='https://www.hospitalB.com'),
            # Add more hospitals as needed
        ])
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()