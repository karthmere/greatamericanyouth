import sqlite3
import os
from datetime import timedelta
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, send
import hashlib
import json
import uuid
import logging
import subprocess

# Connect to the database
db = sqlite3.connect('../greatamericanyouth.db', check_same_thread=False)

app = Flask(__name__)
socket_ = SocketIO(app, cors_allowed_origins='*')
socket_.init_app(app, message_queue=None,
                 cors_allowed_origins="*", max_http_buffer_size=1024*1024*1024)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler('/var/www/greatamericanyouth/server/gay_server.log'),
                              logging.StreamHandler()])

app.config['JWT_SECRET_KEY'] = os.environ['JWT_TOKEN']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=90)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 * 1024
CORS(app)
jwt_manager = JWTManager(app)
cursor = db.cursor()

lock = threading.Lock()


def hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    hashed_password = hash(password)

    params = (username, hashed_password)
    cursor.execute(
        'SELECT * FROM Users WHERE username = ? AND password = ?', params)
    user = cursor.fetchone()

    if user:
        return jsonify({'status': 'success', 'role': user[2], 'token': create_access_token(identity={"username": username, "role": user[2]})})

    return jsonify({'status': 'error'})


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    role = "normie"
    hashed_password = hash(password)
    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    account = cursor.fetchone()
    # Username already exists
    if account:
        return jsonify({'status': 'error'})

    params = (username, hashed_password, role)

    cursor.execute('INSERT INTO Users (username, password, role) VALUES (?, ?, ?)',
                   params)
    db.commit()
    return jsonify({'status': 'success', 'role': "normie", 'token': create_access_token(identity={"username": username, "role": "normie"})})


@app.route('/messages', methods=['GET'])
def get_messages():
    senders = request.args.get("senders").split(",")
    quantity = request.args.get("quantity")
    length = request.args.get("length")
    token = request.args.get("token")
    if token is None:
        return jsonify({'status': 'unauthorized'})

    messages = []
    for sender in senders:
        cursor.execute(
            'SELECT * FROM Messages WHERE sender = ? AND LENGTH(content) >= 15 ORDER BY RANDOM() LIMIT ?', (sender, quantity))
        messages.append(cursor.fetchall())

    if messages:
        return jsonify(messages)

    return jsonify({'status': 'error'})


@app.route('/leaderboards', methods=['POST'])
def post_score():
    data = request.get_json()
    username = data["username"]
    score = data["score"]
    game = data["game"]

    cursor.execute(
        "SELECT * FROM Scores WHERE username = ? AND game = ?", (username, game))

    entry = cursor.fetchone()
    # update the score if the user already has an entry
    if entry:
        if score > int(entry[1]):
            cursor.execute("UPDATE Scores SET score = ? WHERE username = ? AND game = ?",
                           (score, username, game))
    else:
        cursor.execute("INSERT INTO Scores VALUES(?,?,?)",
                       (username, score, game))
    db.commit()

    return jsonify({'status': 'success'})


@app.route('/leaderboards', methods=['GET'])
def get_leaderboard():
    games = request.args.get("games").split(",")

    scores = {}
    for game in games:
        cursor.execute(
            'SELECT * FROM Scores WHERE game = ? ORDER BY score DESC', (game,))
        scores[game] = cursor.fetchall()

    if scores:
        return jsonify(scores)
    return jsonify({'status': 'error'})


@app.route('/article', methods=['GET'])
def get_articles():
    username = request.args.get("username")
    urlName = request.args.get("urlName")

    if username and urlName:
        return jsonify({'status': 'incorrect usage of endpoint'})

    with lock:
        if username:
            cursor.execute(
                'SELECT * FROM Articles WHERE username = ? ORDER BY date DESC', (username,))
        elif urlName:
            cursor.execute(
                'SELECT * FROM Articles WHERE urlName = ?', (urlName,))
        else:
            cursor.execute(
                'SELECT * FROM Articles ORDER BY date DESC')

        articles = cursor.fetchall()

        response = []
        for article in articles:
            response.append({attr[0]: val for (attr, val)
                            in zip(cursor.description, article)})

    return jsonify(response)


@app.route('/article-meta', methods=['GET'])
def get_article_metadata():
    urlName = request.args.get('urlName')
    getAll = request.args.get('getAll')
    with lock:
        if getAll:
            cursor.execute(
                'SELECT thumbnail, title, description, author, avatar FROM Articles WHERE urlName = ? ORDER BY date DESC', (urlName,))
            row = cursor.fetchone()
            response = {attr[0]: val for (
                attr, val) in zip(cursor.description, row)}
            return jsonify(response)
        cursor.execute(
            'SELECT thumbnail, title, description, author, avatar, urlName, audioUrl, published FROM Articles ORDER BY date DESC')
        rows = cursor.fetchall()
        articles = []
        for row in rows:
            articles.append({attr[0]: val for (
                attr, val) in zip(cursor.description, row)})
        response = articles
    return jsonify(response)
        
        

@app.route('/article', methods=['POST'])
@jwt_required()
def post_article():
    data = request.form
    urlName = data["urlName"]
    title = data["title"]
    author = data["author"]
    description = data["description"]
    date = data["date"]
    username = data["username"]
    avatarName = data["avatarName"]
    thumbnailName = data["thumbnailName"]
    avatar = request.files['avatar']
    thumbnail = request.files['thumbnail']
    tags = request.form.getlist('tags')
    sections = request.form.getlist('sections')

    cursor.execute('SELECT * FROM Articles WHERE urlName = ?', (urlName,))

    if cursor.fetchone():
        return jsonify({'status': 'duplicate'})

    media_dir = os.path.join('article-media', urlName)

    if not os.path.exists(media_dir):
        os.mkdir(media_dir)

    avatar_ext = avatarName.split('.')[1]
    avatar_path = os.path.join(media_dir, 'avatar.' + avatar_ext)
    avatar.save(avatar_path)

    thumbnail_ext = thumbnailName.split('.')[1]
    thumbnail_path = os.path.join(media_dir, 'thumbnail.' + thumbnail_ext)
    thumbnail.save(thumbnail_path)

    tags_text = ""
    if tags:
        tags_text = json.dumps(tags)

    sections_text = []

    for (i, section) in enumerate(sections):
        section_text = {'content': section, 'media': []}

        j = 0
        while True:
            field_name = "sections[" + str(i) + "][" + str(j) + "]"
            if field_name not in request.files:
                break
            media = request.files[field_name]
            name = data["names[" + str(i) + "][" + str(j) + "]"]
            text = data["texts[" + str(i) + "][" + str(j) + "]"]

            hash_ = str(uuid.uuid4())[:8]
            split_ = name.split(".")

            path = os.path.join(media_dir, split_[0] + hash_ + "." + split_[1])
            media.save(path)

            section_text['media'].append({
                'path': path,
                'text': text
            })

            j += 1

        sections_text.append(section_text)

    sections_text = json.dumps(sections_text)

    cursor.execute('INSERT INTO Articles VALUES(?,?,?,?,?,?,?,?,?,?,?)', (urlName, title, author,
                   date, description, 1, username, thumbnail_path, avatar_path, tags_text, sections_text))

    db.commit()

    return jsonify({'status': 'success'})


@app.route('/chat-messages', methods=['GET'])
def get_chat_messages():
    pass
    # cursor.execute('SELECT * FROM ChatMessages')
    # messages = cursor.fetchall()
    # return jsonify(messages)


@app.route('/model', methods=['POST'])
def post_model():
    data = request.form
    username = data["username"]
    modelName = data["modelName"]
    video = request.files["video"]

    cursor.execute('SELECT * FROM Models WHERE model = ?', (modelName,))
    if cursor.fetchone():
        return jsonify({'status': 'duplicate'})

    hash_ = str(uuid.uuid4())[:8]
    tmp_path = "tmp" + hash_ + ".mp4"
    video.save(tmp_path)

    subprocess.run(["python3", "ai-graphics/process.py", tmp_path,
                   "ai-graphics/models/" + modelName + ".json"], check=True)

    os.remove(tmp_path)

    cursor.execute('INSERT INTO Models VALUES(?, ?)', (modelName, username))
    db.commit()

    return jsonify({'status': 'success'})


@app.route('/model', methods=['GET'])
def get_model_metadata():
    with lock:
        cursor.execute(
            'SELECT * FROM Models')
        models = cursor.fetchall()
        response = []
        for model in models:
            response.append({attr[0]: val for (attr, val)
                            in zip(cursor.description, model)})

    return jsonify(response)


@socket_.on('message')
def on_message(data):

    match data['type']:
        case 'media':
            sender = data['sender']
            time = data['time']
            month = data['month']
            buffer = data['buffer']
            name = data['name']
            fileType = data['fileType']

            sender_dir = os.path.join('chat-media', sender)
            if not os.path.exists(sender_dir):
                os.mkdir(sender_dir)

            chat_media_dir = os.path.join(sender_dir, month)
            if not os.path.exists(chat_media_dir):
                os.mkdir(chat_media_dir)

            hash_ = str(uuid.uuid4())[:8]
            split_ = name.split(".")
            hashed_name = split_[0] + '_' + hash_ + '.' + split_[1]

            path = os.path.join(chat_media_dir, hashed_name)
            with open(path, "wb") as file:
                file.write(buffer)

            send({'type': data['type'], 'sender': sender,
                 'time': time, 'name': hashed_name, 'path': path,
                  'fileType': fileType}, broadcast=True)
        case 'user-message':
            send(data, broadcast=True)

    # with lock:
    #     cursor.execute('INSERT INTO ChatMessages VALUES(?,?,?,?)',
    #                    (sender, time, content, media))
    #     db.commit()


if __name__ == "__main__":
    socket_.run(app, allow_unsafe_werkzeug=True, debug=True)
