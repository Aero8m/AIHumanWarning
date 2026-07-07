from app import create_app,load_tasks
import os

basedir = os.path.abspath(os.path.dirname(__file__))

def init():
    if not os.path.exists(basedir + "/data/images"):
        os.mkdir(basedir + "/data/images")

app = create_app("development")

if __name__ == '__main__':
    init()
    if os.environ.get('WERKZEUG_RUN_MAIN'):
        load_tasks(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
