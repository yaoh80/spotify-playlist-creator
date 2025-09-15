import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import locale

# Tkinterの文字化け対策
# sys.platformでOSを判定し、Windowsの場合のみctypesを使用
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        locale.setlocale(locale.LC_ALL, '') # システムのロケールを使用
    except (ImportError, AttributeError):
        pass
else:
    # Linux環境（WSLを含む）の場合
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

# --- 認証情報をここに設定 ---
CLIENT_ID = 'd775870f54eb467d9b03fe11b971ba79'
CLIENT_SECRET = '733b3190bdfc40c684b5997f9927b6a5'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
scope = 'playlist-modify-public playlist-read-private playlist-modify-private'
# USERNAMEは認証したユーザー自身のIDを自動で取得するため不要

# --- イベント処理の関数を定義 ---
def create_and_add_podcast_episodes():
    """「作成開始」ボタンが押された時の処理"""
    show_id = show_id_entry.get()

    if not show_id:
        messagebox.showerror("エラー", "ポッドキャストIDを入力してください。")
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
            scope=scope
        ))
        
        # 1. ポッドキャストの情報を取得
        try:
            podcast_info = sp.show(show_id)
            playlist_title = podcast_info['name']
        except spotipy.exceptions.SpotifyException:
            messagebox.showerror("エラー", "指定されたポッドキャストIDが見つかりませんでした。")
            progressbar.pack_forget()
            return
        
        # 2. 既存のプレイリストをチェックし、重複があれば作成しない
        playlists = sp.current_user_playlists()
        existing_playlist_names = [p['name'] for p in playlists['items']]
        if playlist_title in existing_playlist_names:
            messagebox.showinfo("情報", f'「{playlist_title}」というプレイリストは既に存在します。')
            progressbar.pack_forget()
            return
            
        # 3. 新しいプレイリストを作成
        new_playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_title, public=True)
        playlist_id = new_playlist['id']

        # 4. ポッドキャストの全エピソードを取得
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
        
        # 5. エピソードを100件ずつ再生リストに追加
        for i in range(0, total_to_add, 100):
            chunk = new_episode_uris[i:i+100]
            sp.playlist_add_items(playlist_id=playlist_id, items=chunk)
            added_count += len(chunk)
            
            # プログレスバーを更新
            progress_percent = (added_count / total_to_add) * 100
            progressbar['value'] = progress_percent
            window.update_idletasks()
            
        message_label.config(text=f'✅ "{playlist_title}"プレイリストを新規作成し、\n{total_to_add}件のエピソードを追加しました！', fg='green')
        progressbar.pack_forget()

    except Exception as e:
        messagebox.showerror("エラー", f"予期せぬエラーが発生しました。\n詳細: {e}")
        progressbar.pack_forget()

def exit_app():
    """「終了」ボタンが押された時の処理"""
    window.destroy()

# --- ウィンドウの作成 ---
window = tk.Tk()
window.title("Spotify PlaylistCreator")
window.geometry("400x300")
window.resizable(False, False)

# --- GUI要素の配置 ---
tk.Label(window, text="ポッドキャストから新規プレイリストを作成", font=("游ゴシック", 14)).pack(pady=(10, 5))

tk.Label(window, text="ポッドキャストID:", font=("游ゴシック", 12)).pack(pady=(10, 0))
show_id_entry = tk.Entry(window, width=40)
show_id_entry.pack(pady=(0, 10))

ttk.Button(window, text="作成開始", command=create_and_add_podcast_episodes).pack(pady=5)
ttk.Button(window, text="終了", command=exit_app).pack(pady=5)

progressbar = ttk.Progressbar(window, orient='horizontal', length=300, mode='determinate')
progressbar.pack_forget()

message_label = tk.Label(window, text="", font=("游ゴシック", 10))
message_label.pack(pady=(5, 10))

# --- ウィンドウの実行 ---
window.mainloop()