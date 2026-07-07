from flask import Blueprint,request,send_file,Response,abort,stream_with_context
from flask_jwt_extended import jwt_required,get_jwt_identity,verify_jwt_in_request,decode_token
from ...models import Stream
from ...utils.response import success, error
from ...extensions import db
from ...scheduler import load_tasks, stop_task
import os
import cv2
streams_bp = Blueprint('stream', __name__)

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

@streams_bp.route('/',methods=["GET"])
@jwt_required()
def index():
    user_id = get_jwt_identity()
    streams = Stream.query.filter_by(user_id=user_id).all()
    streams_list = []
    for stream in streams:
        streams_list.append(stream.to_dict())
    return success(streams_list)

@streams_bp.route('/add',methods=["POST"])
@jwt_required()
def add():
    user_id = get_jwt_identity()
    body = request.json
    try:
        stream = Stream(body["name"],body["rtsp_link"],user_id,body["prompt"],body["sec"],body["enable"])
        db.session.add(stream)
        db.session.commit()
        load_tasks(None)
    except Exception as e:
        return error(f"添加失败，错误:{str(e)}")

    return success()

@streams_bp.route('/delete',methods=["POST"])
@jwt_required()
def delete():
    user_id = get_jwt_identity()
    try:
        stream = Stream.query.filter_by(user_id=user_id,id=request.json["id"]).first()
        stop_task(stream.id)
        db.session.delete(stream)
        db.session.commit()
    except Exception as e:
        return error(f"删除失败，错误:{str(e)}")
    return success("删除成功")

@streams_bp.route('/edit',methods=["POST"])
@jwt_required()
def edit():
    user_id = get_jwt_identity()
    body = request.get_json()
    if "id" not in body.keys():
        return error("please set stream id")
    stream = Stream.query.filter_by(user_id=user_id,id=body["id"]).first()
    if not stream:
        return error("stream not found")
    allow_properties = {"name","rtsp_link","prompt","sec","enable"}
    for allow_property in allow_properties:
        if allow_property in body.keys():
            setattr(stream, allow_property, body[allow_property])
    db.session.commit()
    stop_task(stream.id)
    load_tasks(None)
    return success()

@streams_bp.route("/<id>/records",methods=["GET"])
@jwt_required()
def records(id):
    stream = Stream.query.filter_by(user_id=get_jwt_identity(),id=id).first()
    if not stream:
        return error("stream not found")
    records = stream.records.all()
    records_list = []
    for record in records:
        records_list.append(record.to_dict())
    return success(records_list)

@streams_bp.route("/<id>/records/image/<filename>",methods=["GET"])
@jwt_required()
def record_image(id,filename):
    return send_file(basedir + f"/data/images/{id}/{filename}")

@streams_bp.route("/<id>/live_stream",methods=["GET"])
def live_stream(id):
    token = request.args.get("token")
    if not token:
        verify_jwt_in_request()
    verify_jwt_in_request(optional=True, verify_type=False)
    stream = Stream.query.filter_by(user_id=decode_token(token)["sub"],id=id).first()
    def generate():
        cap = cv2.VideoCapture(stream.rtsp_link)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            ret, buf = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
    return Response(stream_with_context(generate()), mimetype='multipart/x-mixed-replace; boundary=frame')