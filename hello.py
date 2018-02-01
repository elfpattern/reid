# -*- coding: utf-8 -*-
import psycopg2
from psycopg2 import sql
from flask import Flask, render_template, jsonify, request, send_file
from io import BytesIO
import numpy as np
from tqdm import tqdm
import pickle

app = Flask(__name__, template_folder='templates', static_folder='static')

tracks = []
l2_matrix = None
black_list = set()
fp = set()
merges = {}
pos_i = -1
pos_j = -1

class Track:
    def __init__(self, feature, track_id, length):
        self.feature = feature
        self.track_id = track_id
        self.length = length
        

def connect_db():
    addr = "dbname=harpy user=harpy host=postgres password=harpy"
    conn = psycopg2.connect(addr)
    cur = conn.cursor()
    return cur


def img_urls(video_id, track_id, list_frame_id):
    imgs = []
    for i in range(len(list_frame_id)):
        imgs.append('/image?video_id=' + str(video_id) + '&frame_id=' + str(list_frame_id[i]) + '&track_id=' + str(track_id))
    return imgs

def get_track_id(cur, video_id):
    cur.execute("select track_id from " + "\"" + str(video_id) + "\"")

    track_id = cur.fetchall()
    res = []
    for i in track_id:
        for j in i:
            res.append('{}_{}'.format(video_id,j))
    res = set(res)
    res = list(res)
    return res


def get_track_feature(cur, track_id,video_id,):
    cur.execute("select feature from " + "\"" + str(video_id) + "\"" " where track_id = {}".format(track_id))
    features = cur.fetchall()
    res = []
    for feature in features:
        if feature[0] is not None:
            start = feature[0].find('(')
            end = feature[0].find(')')
            res.append(list(map(float, feature[0][start + 1:end].split(','))))
        else:
            res.append(None)
    length = len(res)
    col_mean = np.array(res).mean(axis=0)
    return col_mean, length


def get_featMatrix(cur, video_id):   #video_id 是一个列表
    global tracks
    row2id = {}
    for i in range(len(video_id)):
        res = get_track_id(cur, video_id[i])
        for j in range(len(res)):
            col_mean, length = get_track_feature(cur, res[j].split('_')[1], video_id[i])
            track = Track(col_mean, res[j], length)
            tracks.append(track)
    return tracks


def matrix_compute(tracks):
    length = len(tracks)
    l2_matrix = []
    dis = np.zeros((length, length))
    for i in tqdm(range(length)):
        for j in tqdm(range(i+1, length)):
            dis[i, j] = np.sqrt(((tracks[i].feature - tracks[j].feature)**2).sum())
            dis[j, i] = dis[i, j]
    for i in range(length):
        dis[i][i] = float("inf")  #设置对角线为一个无穷大的数
    return dis


def get_min():
    global l2_matrix, tracks, black_list, pos_i, pos_j
    length = len(tracks)
    dmin = 100
    for i in range(length):
        for j in range(i+1, length):
            if l2_matrix[i, j] < dmin and (i, j) not in black_list and i not in fp and j not in fp:
                dmin = l2_matrix[i, j]
                pos_i = i
                pos_j = j
    if dmin < 100:
        black_list.add((pos_i, pos_j))
        print((pos_i, pos_j))
        return tracks[pos_i], tracks[pos_j]
    else:
        return (None, None)


def get_all_frame_id(cur, track_id1, track_id2):
    video_id1 = track_id1.split('_')[0]
    track_id1 = track_id1.split('_')[1]
    cur.execute("select frame_id from " + "\"" + str(video_id1) + "\"" + "where track_id = {}".format(track_id1))
    frame_id1 = cur.fetchall()

    list_frame_id1 = []
    for i in frame_id1:
        for j in i:
            list_frame_id1.append(j)
    video_id2 = track_id2.split('_')[0]
    track_id2 = track_id2.split('_')[1]
    cur.execute("select frame_id from " + "\"" + str(video_id2) + "\"" + "where track_id = {}".format(track_id2))
    frame_id2 = cur.fetchall()

    list_frame_id2 = []
    for i in frame_id2:
        for j in i:
            list_frame_id2.append(j)
    return video_id1, track_id1, list_frame_id1, video_id2, track_id2, list_frame_id2


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/begin', methods=['POST'])
def begin():
    global tracks, l2_matrix, black_list, merges, fp, pos_i, pos_j
    tracks = []
    l2_matrix = None
    black_list = set()
    fp = set()
    merges = {}
    pos_i = -1
    pos_j = -1
    cur = connect_db()
    tracks = get_featMatrix(cur, ['1', '8'])
    l2_matrix = matrix_compute(tracks)
    return jsonify(get_next(cur))


def merge():
    global tracks, pos_i, pos_j, black_list, merges
    tracks[pos_i].feature = (tracks[pos_i].feature * tracks[pos_i].length + 
            tracks[pos_j].feature * tracks[pos_j].length) / (tracks[pos_i].length + tracks[pos_j].length)
    tracks[pos_i].length = tracks[pos_i].length + tracks[pos_j].length
    length = len(tracks)
    merges[pos_j] = pos_i
    for i in range(length):
        if pos_j < i:
            black_list.add((pos_j, i))
        else:
            black_list.add((i, pos_j))


def get_next(cur):
    track_i, track_j = get_min()
    if track_i is not None and track_j is not None:
        video_id1, track_id1, list_frame_id1, video_id2, track_id2, list_frame_id2 = get_all_frame_id(cur, track_i.track_id, track_j.track_id)
        img1 = img_urls(video_id1, track_id1, list_frame_id1)
        img2 = img_urls(video_id2, track_id2, list_frame_id2)
        t = {
            'img1': img1,
            'img2': img2,
        }
        return t

@app.route('/yes', methods=['POST'])
def yes():
    cur = connect_db()
    merge()
    return jsonify(get_next(cur))


@app.route('/no', methods=['POST'])
def no():
    cur = connect_db()
    return jsonify(get_next(cur))


@app.route('/fpl', methods=['POST'])
def fpl():
    global fp, pos_i
    cur = connect_db()
    fp.add(pos_i)
    return jsonify(get_next(cur))


@app.route('/fpr', methods=['POST'])
def fpr():
    global fp, pos_j
    cur = connect_db()
    fp.add(pos_j)
    return jsonify(get_next(cur))


@app.route('/fpa', methods=['POST'])
def fpa():
    global fp, pos_i, pos_j
    cur = connect_db()
    fp.add(pos_i)
    fp.add(pos_j)
    return jsonify(get_next(cur))


@app.route('/reset', methods=['POST'])
def reset():
    global tracks, l2_matrix, black_list, merges, fp, pos_i, pos_j
    tracks = []
    l2_matrix = None
    black_list = set()
    fp = set()
    merges = {}
    pos_i = -1
    pos_j = -1
    return jsonify({'img1':[], 'img2': []})


@app.route('/save', methods=['POST'])
def save():
    global tracks, l2_matrix, black_list, merges, fp, pos_i, pos_j
    f = open('save.pkl', 'wb')
    pickle.dump((tracks, black_list, merges, fp), f)
    f.close()
    return jsonify({'success': 1})


@app.route("/image", methods=['GET'])
def get_reid_image():
    video_id = request.args.get('video_id')
    frame_id = request.args.get('frame_id')
    track_id = request.args.get('track_id')
    cur = connect_db()
    image = get_image(cur, video_id, frame_id, track_id)
    return send_file(BytesIO(image), mimetype='image/jpeg')


def get_image(cur, video_id, frame_id, track_id):
    query = sql.SQL("SELECT image FROM {} \
            WHERE frame_id = %s and track_id = %s;").format(sql.Identifier(video_id))
    cur.execute(query, (frame_id, track_id))
    image = cur.fetchone()[0]
    return image


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
