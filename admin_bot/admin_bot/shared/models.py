from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class DiscordMessage(Base):
    __tablename__ = "messages"
    time = Column(Integer, primary_key=True)
    username = Column(String(80))
    content = Column(String(2000))
    channel = Column(String(40))

    def __repr__(self):
        return f'{self.username} published "{self.content}" in {self.channel} at {self.time}'
