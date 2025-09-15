import spotipy
from spotipy.oauth2 import SpotifyOAuth
import PySimpleGUI as sg

# --- 認証情報をここに設定 ---
CLIENT_ID = 'd775870f54eb467d9b03fe11b971ba79'
CLIENT_SECRET = '733b3190bdfc40c684b5997f9927b6a5'
REDIRECT_URI = 'https://localhost:8888/callback'
USERNAME = '31tglh7tngxjtgd6nnxwgn3sqilaD'
PLAYLIST_ID = '0pmv65U0CFl1hdj7OKgCS1'
scope = 'playlist-modify-public'

# --- GUIのレイアウトを定義 ---
# 日本語に対応したフォントを指定
FONT = ("游ゴシック", 12)  # 他のフォント名も試せます（例: "Meiryo UI", "MS Gothic"）
# レイアウトを定義。サイズを調整し、見切れを解消
layout = [
    [sg.Text('Spotifyプレイリストに追加', font=FONT)], # <--- ここにfont=FONTを追加
    [sg.Text('曲名:', size=(12, 1), font=FONT), sg.Input(key='-TRACK-')], # sizeを調整
    [sg.Text('アーティスト名:', size=(12, 1), font=FONT), sg.Input(key='-ARTIST-')], # sizeを調整
    [sg.Button('追加', key='-ADD-BUTTON-', font=FONT), sg.Button('終了', font=FONT)],
    [sg.Text('', key='-MESSAGE-', font=FONT)]
]
# ウィンドウの作成
# タイトルバーのフォントを設定することで、文字化けやマークを修正
# "titlebar_font"は`sg.Window`では使用できないため、代わりに`font`で全体を設定するか、特別なオプションを使用します。
# 基本的な解決策として、タイトルをシンプルにすることをお勧めします。
window = sg.Window('Spotify', layout, font=FONT)
# window = sg.Window('Spotify プレイリスト追加アプリ', layout)

# --- イベントループ ---
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == '終了':
        break

    if event == '-ADD-BUTTON-':
        track_name = values['-TRACK-']
        artist_name = values['-ARTIST-']

        if not track_name or not artist_name:
            window['-MESSAGE-'].update('🚨 曲名とアーティスト名を入力してください。', text_color='red')
            continue

        # Spotify認証と曲の追加処理
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=scope,
                username=USERNAME
            ))

            results = sp.search(q=f'track:{track_name} artist:{artist_name}', type='track', limit=1)

            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                sp.playlist_add_items(playlist_id=PLAYLIST_ID, items=[track_uri])
                window['-MESSAGE-'].update(f'✅ "{track_name}" をプレイリストに追加しました！', text_color='green')
            else:
                window['-MESSAGE-'].update('🚨 曲が見つかりませんでした。', text_color='red')
        except Exception as e:
            window['-MESSAGE-'].update(f'🚨 エラーが発生しました: {e}', text_color='red')

window.close()