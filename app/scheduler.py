from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime,timedelta
import cv2
import os
import mimetypes
import base64
from openai import OpenAI
from .models import StreamRecord,User,Stream
from .extensions import db
from flask import Flask

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_app = None

def image_to_data_url(image_path):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    with open(image_path, "rb") as f:
        image_data = f.read()

    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None or not mime_type.startswith('image/'):
        mime_type = 'image/png'

    base64_encoded = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded}"

class RTSPTask:
    def __init__(self,id,user,sec,rtsp_url,prompt):
        self.id = id
        self.prompt = prompt
        self.user = user
        self.llm_baseurl = self.user.llm_baseurl
        self.llm_apikey = self.user.llm_apikey
        self.llm_modelname = self.user.llm_modelname
        if not self.llm_apikey:
            print("[ERR] LLM API key not set")
            return
        self.client = OpenAI(base_url=self.llm_baseurl,api_key=self.llm_apikey)
        self.running = False
        self.sec = sec
        self.rtsp_url = rtsp_url
        self.scheduler = BackgroundScheduler()
        if not os.path.exists(basedir + f"/data/images/{self.id}"):
            os.makedirs(basedir + f"/data/images/{self.id}", exist_ok=True)

    def _resize_frame(self, frame, max_dim=1080):
        h, w = frame.shape[:2]
        if max(h, w) <= max_dim:
            return frame
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    def run(self):
        if not self.llm_apikey:
            print("[ERR] LLM API key not set")
            return
        self.running = True
        self.scheduler.start()
        self.scheduler.add_job(
            func=self.task,
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=self.sec),
            id=f'rtsp_{self.id}',
            replace_existing=True
        )
    def stop(self):
        self.running = False
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
    def task(self):
        print(f"[SCHEDULER] Stream ID {self.id}: timer task started.")
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
        ret, frame = cap.read()
        if ret:
            current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            img_path = basedir + f"\\data\\images\\{self.id}\\AIHWCAP_{self.id}_{current_time_str}.png"
            frame = self._resize_frame(frame)
            result, buf = cv2.imencode('.png', frame)
            with open(img_path, 'wb') as f:
                f.write(buf.tobytes())
            print(f"[SCHEDULER] Stream ID {self.id}: image saved to {img_path}")
            with _app.app_context():
                llm_reponse = self.client.chat.completions.create(model=self.llm_modelname,messages=[
                    {
                        "role":"system",
                        "content":f"""## 基本定义
                你是一个图片识别助手，你要根据用户给出的图片，判断图片是否满足用户给出的条件。
                ## 输出格式
                你的输出只能有两行。
                第一行：输出你判断是否成立的理由，简短，在一行内输出，不要超过20字。
                第二行：输出用户给出的条件是否成立，成立返回”yes“，不成立返回”no“。
                """
                    },
                    {
                        "role":"user",
                        "content":[
                            {"type":"text", "text":self.prompt},
                            {"type":"image_url","image_url":{"url":image_to_data_url(img_path)}}
                        ]
                    }
                ],stream=False,extra_body={"thinking":{"type":"disabled"}})
                llm_reponse_content = llm_reponse.choices[0].message.content
                llm_reponse_reason = llm_reponse_content.split("\n")[0]
                llm_reponse_status = True if llm_reponse_content.split("\n")[1] == "yes" else False
                record = StreamRecord(self.id, llm_reponse_status, llm_reponse_reason, f"AIHWCAP_{self.id}_{current_time_str}.png")
                db.session.add(record)
                db.session.commit()
                print(f"[SCHEDULER] Stream ID {self.id} LLM Result: Status: {"OK" if llm_reponse_status else "NO"}   Reason: {llm_reponse_reason}")
                self.scheduler.add_job(
                    func=self.task,
                    trigger='date',
                    run_date=datetime.now() + timedelta(seconds=self.sec),
                    id=f'rtsp_{self.id}',
                    replace_existing=True
                )
                print(f"[SCHEDULER] Stream ID {self.id}: timer task succeeded.")
        else:
            print(f"[ERR] Stream ID {self.id}: failed to read frame from RTSP stream, stop task")

        cap.release()


tasks = []

def load_tasks(app: Flask):
    global tasks, _app
    if app:
        _app = app
        app_ctx = app.app_context()
        app_ctx.push()
    try:
        print("[SCHEDULER] Loading tasks")
        for stream in Stream.query.all():
            if stream.enable:
                flag = False
                for task in tasks:
                    if task.id == stream.id:
                        flag = True
                        break
                if flag:
                    continue
                tasks.append(RTSPTask(stream.id, stream.user, stream.sec, stream.rtsp_link, stream.prompt))
                tasks[-1].run()
                print(f"[SCHEDULER] Task ID {stream.id} created.")
    except Exception as e:
        print(f"[ERR] Failed to load tasks: {e}")
    finally:
        if app:
            app_ctx.pop()

def stop_task(stream_id):
    global tasks
    for i, task in enumerate(tasks):
        if task.id == stream_id:
            task.stop()
            tasks.pop(i)
            print(f"[SCHEDULER] Stream ID {stream_id} task stopped.")
            break

def stop_all_tasks():
    global tasks
    print(f"[SCHEDULER] Stopping all tasks")
    for task in tasks:
        task.stop()
        tasks.pop(task.id)
        print(f"[SCHEDULER] Task ID {task.id} stopped.")

