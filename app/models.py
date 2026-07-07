from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask import url_for
import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    streams = db.relationship('Stream', backref='user', lazy='dynamic')
    stream_records = db.relationship('StreamRecord', backref='user', lazy='dynamic')
    llm_baseurl = db.Column(db.String(256), nullable=False,default="https://api-inference.modelscope.cn/v1")
    llm_apikey = db.Column(db.String(256),nullable=False,default="sk-xxxxxxxxxxxxxxxxxxxx")
    llm_modelname = db.Column(db.String(256), nullable=False,default="Qwen/Qwen3.5-122B-A10B")
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'llm_baseurl': self.llm_baseurl,
            'llm_apikey': self.llm_apikey,
            'llm_modelname': self.llm_modelname
        }
    def get_token(self):
        return create_access_token(identity=str(self.id))

class Stream(db.Model):
    __tablename__ = 'streams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rtsp_link = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt = db.Column(db.String(80), nullable=False)
    records = db.relationship('StreamRecord', backref='stream', lazy='dynamic')
    sec = db.Column(db.Integer, nullable=False)
    enable = db.Column(db.Boolean, default=True)
    def __init__(self, name, rtsp_link, user_id, prompt, sec,enable):
        self.name = name
        self.rtsp_link = rtsp_link
        self.user_id = user_id
        self.prompt = prompt
        self.sec = sec
        self.enable = enable
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rtsp_link': self.rtsp_link,
            'user_id': self.user_id,
            'prompt': self.prompt,
            'sec': self.sec,
            'enable': self.enable,
        }
class StreamRecord(db.Model):
    __tablename__ = 'stream_records'
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('streams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    reason = db.Column(db.String(80), nullable=False)
    image_url = db.Column(db.String(256), nullable=False)
    time = db.Column(db.DateTime, nullable=False,default=datetime.datetime.now)
    def __init__(self, stream_id, status, reason, image_name):
        self.stream_id = stream_id
        self.user_id = Stream.query.get(stream_id).user_id
        self.prompt = Stream.query.get(stream_id).prompt
        self.status = status
        self.reason = reason
        self.image_url = image_name
    def to_dict(self):
        return {"id":self.id,
                "stream_id": self.stream_id,
                "user_id": self.user_id,
                "prompt": self.prompt,
                "status": self.status,
                "reason": self.reason,
                "image_url": url_for('v1.stream.record_image', id=self.stream_id, filename=self.image_url, _external=True),
                "time": datetime.datetime.timestamp(self.time),
                }
