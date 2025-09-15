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
scope = 'playlist-modify-public playlist-read-private playlist-modify-private'

# --- イベント処理の関数を定義 ---
def add_podcast_episodes():
    """「追加開始」ボタンが押された時の処理"""
    show_id = show_id_entry.get()

    if not show_id:
        messagebox.showerror("入力エラー", "ポッドキャストIDを入力してください。")
        return

    message_label.config(text='ポッドキャスト情報を取得しています...', fg='blue')
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
        
        # 1. ポッドキャストの情報を取得
        podcast_info = sp.show(show_id)
        playlist_title = podcast_info['name']
        
        # 2. ポッドキャスト名で新しいプレイリストを作成
        new_playlist = sp.user_playlist_create(user=USERNAME, name=playlist_title, public=True)
        playlist_id = new_playlist['id']

        # 3. ポッドキャストの全エピソードを取得
        podcast_episodes = []
        results = sp.show_episodes(show_id=show_id, limit=50)
        podcast_episodes.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            podcast_episodes.extend(results['items'])
            
        new_episode_uris = [episode['uri'] for episode in podcast_episodes]
        
        if not new_episode_uris:
            message_label.config(text='✅ エピソードが見つかりませんでした。', fg='green')
            progressbar.pack_forget()
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
            window.update_idletasks()
            
        message_label.config(text=f'"{playlist_title}"プレイリストを新規作成し、\n{total_to_add}件のエピソードを追加しました！', fg='green')
        progressbar.pack_forget()

    except Exception as e:
        message_label.config(text=f'エラーが発生しました: {e}', fg='red')
        progressbar.pack_forget()

def exit_app():
    """「終了」ボタンが押された時の処理"""
    window.destroy()

# --- ウィンドウの作成 ---
window = tk.Tk()
window.title("Spotify PlaylistCreator")
window.geometry("400x300")

# --- GUI要素の配置 ---
tk.Label(window, text="ポッドキャストから新規プレイリストを作成", font=("游ゴシック", 14)).pack(pady=10)

tk.Label(window, text="ポッドキャストID:", font=("游ゴシック", 12)).pack(pady=(10, 0))
show_id_entry = tk.Entry(window, width=40)
show_id_entry.pack()

ttk.Button(window, text="作成開始", command=add_podcast_episodes).pack(pady=15)
ttk.Button(window, text="終了", command=exit_app).pack()

progressbar = ttk.Progressbar(window, orient='horizontal', length=300, mode='determinate')
progressbar.pack_forget()

message_label = tk.Label(window, text="", font=("游ゴシック", 10))
message_label.pack(pady=10)

# --- ウィンドウの実行 ---
window.mainloop()