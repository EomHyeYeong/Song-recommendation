from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

# 크롤링 임포트
import requests
from bs4 import BeautifulSoup
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

# db 임포트
from pymongo import MongoClient
client = MongoClient('DB_URL')
db = client.dbsparta

### 메인 페이지
@app.route('/')
def home():
   return render_template('index.html')

@app.route("/song", methods=["POST"])
def web_home_post():
    sample_receive = request.form['sample_give']
    print(sample_receive)
    return jsonify({'msg': 'POST 연결 완료!'})

@app.route("/song", methods=["GET"])
def web_home_get():
    all_users = list(db.music_list.find({}, {'_id': False}))
    return jsonify(all_users)





### 추천하기 페이지
@app.route('/recommend/')
def recommend():
   return render_template('recommend.html')

    #검색으로 찾기
@app.route('/recommend/rcm_song', methods=["POST"])
def recommend_post():
    search_receive = request.form['search_give']
    type_receive = request.form['type_give']
    music_list = []

    # 크롤링
    url = 'https://www.melon.com/search/total/index.htm?q=' + search_receive + '&section=&mwkLogType=T'
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    if type_receive == '제목으로 검색':
        # 제목+가수명 검색
        music = soup.select('#frm_searchSong > div > table > tbody > tr')

    elif type_receive == '가수이름으로 검색':
        # 가수명 검색
        music = soup.select('#frm_searchArtist > div > table > tbody > tr')

    else:
        # 제목+가수명 검색
        music = soup.select('#frm_songList > div > table > tbody > tr')

    for m in music:
        music_info = dict()
        r = m.select_one('td.no > div')

        music_info['rank'] = r.text
        music_info['title'] = m.select_one('td:nth-child(3) > div > div > a.fc_gray').text
        music_info['name'] = m.select_one('td:nth-child(4) > div > div').text.strip().split('\n')[0]
        music_info['code'] = m.select_one('td:nth-child(3) > div > div > a.fc_gray')['href'].split(';')[1].split(',')[1].strip(')')
        music_list.append(music_info)

    return jsonify(music_list)

@app.route("/recommend/rcm_song", methods=["GET"])
def recommend_get():


    return jsonify({'msg': 'GET 연결 완료!'})

    #멜론 top100에서 찾기
@app.route("/recommend/top100", methods=["GET"])
def top100_get():
    data = requests.get('https://www.melon.com/chart/index.htm', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    music_list=[]
    i = 0

    rank_list = soup.select('#lst50 > td:nth-child(2) > div > span.rank')
    title_list = soup.select('#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank01 > span > a')
    singer_list = soup.select('#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank02')

    for singer in singer_list:
        if i == 20:
            break

        music_info = dict()
        name = ''
        artist_list = singer.select('a')

        if (len(artist_list) / 2) != 1:
            for j in range(2):
                name += artist_list[j].text
                name += ', '

            if (len(artist_list) / 2) > 2:
                name += ' ...'

        else:
            name = singer.select_one('a').text.strip(', ')

        music_info['rank'] = rank_list[i].text
        music_info['title'] = title_list[i].text
        music_info['name'] = name
        music_info['code'] = title_list[i]['href'].split(',')[1].strip(');')
        music_list.append(music_info)
        i += 1

    return jsonify(music_list)

    #선택한 노래 정보
@app.route("/recommend/select_search", methods=["POST"])
def selectedmusic_post():
    code_receive = request.form['code_give']
    data = requests.get('https://www.melon.com/song/detail.htm?songId=' + code_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    music = soup.select_one('#downloadfrm > div > div')
    img = music.select_one('div.thumb > a > img')['src']
    singer = music.select_one('div.entry > div.info > div.artist').text.strip()

    doc = {
        'img':img,
        'name':singer
    }

    return jsonify(doc)

    # 등록하기 버튼
@app.route("/recommend/register", methods=["POST"])
def register_post():
    img_receive = request.form['img_give']
    title_receive = request.form['title_give']
    singer_receive = request.form['singer_give']
    nName_receive = request.form['nName_give']
    comment_receive = request.form['comment_give']
    print(title_receive, singer_receive)
    print(nName_receive, comment_receive)

    doc = {
        'img': img_receive,
        'title': title_receive,
        'singer': singer_receive,
        'nName': nName_receive,
        'comment': comment_receive
    }
    db.music_list.insert_one(doc)
    return jsonify('등록 완료!')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
