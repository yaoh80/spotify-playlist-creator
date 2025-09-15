import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import ttk, messagebox
import locale

# Tkinterが日本語を正しく扱えるように設定
locale.setlocale(locale.LC_ALL, 'C.UTF-8')

# --- 認証情報をここに設定 ---
CLIENT_ID = 'd775870f54eb467d9b03fe11b971ba79'
CLIENT_SECRET = '733b3190bdfc40c684b5997f9927b6a5'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
USERNAME = '31tglh7tngxjtgd6nnxwgn3sqilaD'
scope = 'playlist-modify-public playlist-read-private'

# --- イベント処理の関数を定義 ---
def add_podcast_episodes():
    """「追加開始」ボタンが押された時の処理"""
    playlist_id = playlist_id_entry.get()
    show_id = show_id_entry.get()

    if not playlist_id or not show_id:
        messagebox.showerror("入力エラー", "再生リストIDとポッドキャストIDの両方を入力してください。")
        return

    message_label.config(text='ポッドキャストエピソードの重複を確認し、追加を開始します...', fg='blue')
    window.update_idletasks()
    
    # プログレスバーを初期化し、表示
    progressbar['value'] = 0
    progressbar.pack(pady=5)
    
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=scope,
            username=USERNAME
        ))
        
        # 1. 既存の再生リストのエピソードを取得
        current_episodes_data = sp.playlist_items(playlist_id=playlist_id, fields='items(track(uri))')
        current_uris = {item['track']['uri'] for item in current_episodes_data['items']}
        
        # 2. ポッドキャストの全エピソードを取得
        podcast_episodes = []
        results = sp.show_episodes(show_id=show_id, limit=50)
        podcast_episodes.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            podcast_episodes.extend(results['items'])
            
        # 3. 新規エピソードを特定
        new_episode_uris = []
        for episode in podcast_episodes:
            if episode['uri'] not in current_uris:
                new_episode_uris.append(episode['uri'])
        
        if not new_episode_uris:
            message_label.config(text='✅ 再生リストは最新です。新規エピソードはありませんでした。', fg='green')
            progressbar.pack_forget() # プログレスバーを非表示
            return

        total_to_add = len(new_episode_uris)
        added_count = 0
        
        # 4. 新規エピソードを100件ずつ再生リストに追加
        for i in range(0, total_to_add, 100):
            chunk = new_episode_uris[i:i+100]
            sp.playlist_add_items(playlist_id=playlist_id, items=chunk)
            added_count += len(chunk)
            
            # プログレスバーを更新
            progress_percent = (added_count / total_to_add) * 100
            progressbar['value'] = progress_percent
            window.update_idletasks() # ウィンドウを更新
            
        message_label.config(text=f'{total_to_add}件の新規エピソードをプレイリストに追加しました！', fg='green')
        progressbar.pack_forget() # プログレスバーを非表示

    except Exception as e:
        message_label.config(text=f'エラーが発生しました: {e}', fg='red')
        progressbar.pack_forget() # プログレスバーを非表示

def exit_app():
    """「終了」ボタンが押された時の処理"""
    window.destroy()

# --- ウィンドウの作成 ---
window = tk.Tk()
window.title("Spotify PlaylistCreator")
window.geometry("400x350")

# --- GUI要素の配置 ---
tk.Label(window, text="ポッドキャストエピソードをプレイリストに追加", font=("游ゴシック", 14)).pack(pady=10)

tk.Label(window, text="再生リストID:", font=("游ゴシック", 12)).pack()
playlist_id_entry = tk.Entry(window, width=40)
playlist_id_entry.pack()

tk.Label(window, text="ポッドキャストID:", font=("游ゴシック", 12)).pack(pady=(10, 0))
show_id_entry = tk.Entry(window, width=40)

show_id_entry.pack()

ttk.Button(window, text="追加開始", command=add_podcast_episodes).pack(pady=15)
ttk.Button(window, text="終了", command=exit_app).pack()

progressbar = ttk.Progressbar(window, orient='horizontal', length=300, mode='determinate')
progressbar.pack_forget() # 初期状態では非表示

message_label = tk.Label(window, text="", font=("游ゴシック", 10))
message_label.pack(pady=10)

# --- ウィンドウの実行 ---
window.mainloop()