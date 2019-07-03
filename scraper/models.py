#pylint: disable=invalid-name
'''
models.py
'''
from sqlalchemy import Column, Integer, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TweetData(Base):
    '''
    Tweet
    '''
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    tweet_data = Column(JSON)

    def __init__(self, tweet_json):
        self.tweet_data = tweet_json


if __name__ == '__main__':
    engine = create_engine('sqlite:///twitter_db', echo=True)
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
