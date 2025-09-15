import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- 1. あなたの認証情報をここに設定 ---
# 手順1で取得したClient IDとClient Secretを貼り付けてください
CLIENT_ID = "d775870f54eb467d9b03fe11b971ba79"
CLIENT_SECRET = "733b3190bdfc40c684b5997f9927b6a5"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

# --- 2. ターゲットの情報を設定 ---
USERNAME = "31tglh7tngxjtgd6nnxwgn3sqilaD"
PLAYLIST_ID = "0pmv65U0CFl1hdj7OKgCS1"
# ユーザーIDとプレイリストIDは、SpotifyのプロフィールやプレイリストのURLから取得できます
# 例: https://open.spotify.com/user/ユーザーID/playlist/プレイリストID

# --- 3. 追加したい曲の情報を設定 ---
# 今回は例として、"My Chemical Romance"の"Welcome to the Black Parade"を追加します
TRACK_NAME = "Welcome to the Black Parade"
ARTIST_NAME = "My Chemical Romance"

# --- 4. スクリプトの実行 ---
# プレイリストを編集するための権限を設定
scope = "playlist-modify-public"

# ユーザーに認証を要求
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope,
        username=USERNAME,
    )
)

# 曲を検索
# `q`パラメータで検索クエリを指定
results = sp.search(q=f"track:{TRACK_NAME} artist:{ARTIST_NAME}", type="track", limit=1)

# 検索結果が存在するか確認
if results["tracks"]["items"]:
    track_uri = results["tracks"]["items"][0]["uri"]
    print(
        f'見つかった曲: {results["tracks"]["items"][0]["name"]} - {results["tracks"]["items"][0]["artists"][0]["name"]}'
    )

    # プレイリストに曲を追加
    sp.playlist_add_items(playlist_id=PLAYLIST_ID, items=[track_uri])
    print(f"✅ プレイリストに曲を追加しました！")
else:
    print("🚨 指定された曲が見つかりませんでした。")
