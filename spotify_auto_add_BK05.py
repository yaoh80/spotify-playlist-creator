import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import ttk
import locale

# Tkinterが日本語を正しく扱えるように設定
locale.setlocale(locale.LC_ALL, 'C.UTF-8')

# --- 認証情報をここに設定 ---
CLIENT_ID = 'd775870f54eb467d9b03fe11b971ba79'
CLIENT_SECRET = '733b3190bdfc40c684b5997f9927b6a5'
REDIRECT_URI = 'https://localhost:8888/callback'
USERNAME = '31tglh7tngxjtgd6nnxwgn3sqilaD'
PLAYLIST_ID = '0pjDxy2z73nyNKRmcxbxoc'  # あなたの再生リストID
scope = 'playlist-modify-public playlist-read-private' # 新たに`playlist-read-private`を追加

# --- ポッドキャスト情報をここに設定 ---
SHOW_ID = '3RISImZEzphLc5yBwRJ80v' 

# --- 2. イベント処理の関数を定義 ---
def add_podcast_episodes():
    """「追加開始」ボタンが押された時の処理"""
    message_label.config(text='ポッドキャストエピソードの重複を確認し、追加を開始します...', fg='blue')
    window.update_idletasks()

    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=scope,
            username=USERNAME
        ))
        
        # 1. 既存の再生リストのエピソードを取得
        current_episodes = sp.playlist_items(playlist_id=PLAYLIST_ID, fields='items(track(uri))')
        current_uris = {item['track']['uri'] for item in current_episodes['items']}
        
        # 2. ポッドキャストの全エピソードを取得
        podcast_episodes = []
        results = sp.show_episodes(show_id=SHOW_ID, limit=50)
        podcast_episodes.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            podcast_episodes.extend(results['items'])
            
        # 3. 新規エピソードを特定
        new_episode_uris = []
        for episode in podcast_episodes:
            if episode['uri'] not in current_uris:
                new_episode_uris.append(episode['uri'])
        
        # 4. 新規エピソードのみを再生リストに追加
        if new_episode_uris:
            # SpotifyのAPIは一度に最大100件のアイテムを追加可能
            # 念のためチャンクに分けて処理する
            for i in range(0, len(new_episode_uris), 100):
                chunk = new_episode_uris[i:i+100]
                sp.playlist_add_items(playlist_id=PLAYLIST_ID, items=chunk)
            
            message_label.config(text=f'✅ {len(new_episode_uris)}件の新規エピソードをプレイリストに追加しました！', fg='green')
        else:
            message_label.config(text='✅ 再生リストは最新です。新規エピソードはありませんでした。', fg='green')

    except Exception as e:
        message_label.config(text=f'🚨 エラーが発生しました: {e}', fg='red')

def exit_app():
    """「終了」ボタンが押された時の処理"""
    window.destroy()

# --- 1. ウィンドウの作成 ---
window = tk.Tk()
window.title("Spotify ポッドキャスト追加アプリ")
window.geometry("400x200")

# --- 2. GUI要素の配置 ---
tk.Label(window, text="ポッドキャストの全エピソードを\nプレイリストに追加します", font=("游ゴシック", 14)).pack(pady=10)

ttk.Button(window, text="追加開始", command=add_podcast_episodes).pack(pady=5)
ttk.Button(window, text="終了", command=exit_app).pack(pady=5)

message_label = tk.Label(window, text="", font=("游ゴシック", 10))
message_label.pack(pady=10)

# --- 4. ウィンドウの実行 ---
window.mainloop()