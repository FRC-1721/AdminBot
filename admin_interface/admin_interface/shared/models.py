from flask_sqlalchemy import SQLAlchemy

# Alchemy DB
db = SQLAlchemy()


class DiscordMessage(db.Model):
    time = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    content = db.Column(db.String(2000))
    channel = db.Column(db.String(40))

    def __repr__(self):
        return f'{self.username} published "{self.content}" in {self.channel} at {self.time}'
