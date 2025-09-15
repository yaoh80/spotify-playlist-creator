import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import ttk
import locale

# Tkinterが日本語を正しく扱えるように設定
locale.setlocale(locale.LC_ALL, 'C.UTF-8')

# --- 認証情報をここに設定 ---
CLIENT_ID = 'xxx'
CLIENT_SECRET = 'xxx'
REDIRECT_URI = 'https://localhost:8888/callback'
USERNAME = 'xxx'
PLAYLIST_ID = 'xxx'
scope = 'playlist-modify-public'

# --- 3. イベント処理の関数を定義 ---
def add_to_playlist():
    """「追加」ボタンが押された時の処理"""
    track_name = track_input.get()
    artist_name = artist_input.get()
    
    if not track_name or not artist_name:
        message_label.config(text='🚨 曲名とアーティスト名を入力してください。', fg='red')
        return

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
            message_label.config(text=f'✅ "{track_name}" をプレイリストに追加しました！', fg='green')
        else:
            message_label.config(text='🚨 曲が見つかりませんでした。', fg='red')
    except Exception as e:
        message_label.config(text=f'🚨 エラーが発生しました: {e}', fg='red')

def exit_app():
    """「終了」ボタンが押された時の処理"""
    window.destroy()

# --- 1. ウィンドウの作成 ---
window = tk.Tk()
window.title("Spotify PalylistCreator")
window.geometry("400x250")  # 高さを少し広げてメッセージを表示しやすくする

# --- 2. GUI要素の配置 ---
tk.Label(window, text="Spotifyプレイリストに追加", font=("游ゴシック", 14)).pack(pady=10)
tk.Label(window, text="曲名:", font=("游ゴシック", 12)).pack()
track_input = tk.Entry(window, width=30)
track_input.pack()

tk.Label(window, text="アーティスト名:", font=("游ゴシック", 12)).pack()
artist_input = tk.Entry(window, width=30)
artist_input.pack()

ttk.Button(window, text="追加", command=add_to_playlist).pack(pady=5)
ttk.Button(window, text="終了", command=exit_app).pack(pady=5)

message_label = tk.Label(window, text="", font=("游ゴシック", 10))
message_label.pack(pady=10)

# --- 4. ウィンドウの実行 ---
window.mainloop()