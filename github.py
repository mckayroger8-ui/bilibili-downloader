import requests
import os
cookies = """your_cookie_here"""

def video_url(bv):
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bv}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        'Referer': 'https://www.bilibili.com/',
        'Cookie': cookies
    }
    response = requests.get(url,headers=headers,timeout=10)
    data = response.json()
    if data["code"] != 0:
        print(f'获取视频信息失败: {data["code"]}')
        return None
    cid = data["data"]["cid"]
    title = data["data"]["title"]
    play_url = f'https://api.bilibili.com/x/player/playurl?bvid={bv}&cid={cid}&qn=116&type=mp4&platform=pc'
    response_play = requests.get(play_url,headers=headers,timeout=10)
    data_play = response_play.json()
    if data_play["code"] != 0:
        print(f'获取播放地址失败: {data_play["message"]}')
        return None
    video_url = data_play["data"]["durl"][0]["url"]
    return video_url,title
def download_video(video_url,save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.bilibili.com/'
    }
    temp_file = save_path + ".tmp"
    existing_size = 0
    if os.path.exists(temp_file):
        existing_size = os.path.getsize(temp_file)
        print(f'发现未完成的下载，已下载 {existing_size} 字节，正在续传...')
        headers['Range'] = f'bytes={existing_size}-'
    try:
        response = requests.get(video_url,headers=headers,stream=True,timeout=20)
        response.raise_for_status()
        total_size = existing_size + int(response.headers.get("content-length",0))
        print(f'文件总大小：{total_size/1024/1024:.1f}MB')
        with open(temp_file,"ab") as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    existing_size += len(chunk)
                    progress = existing_size/total_size * 100
                    print(f'\r下载进度：{progress:.1f}%',end='')
        print(f'✅ 视频已保存到: {save_path}')
    except Exception as e:
        print(f'下载请求失败: {e}')
        return
if __name__ == "__main__":
    bv = input('请输入B站视频BV号（比如BV1xxx）: ')
    video_url,title = video_url(bv)
    if video_url:
        save_path = os.path.join(os.path.expanduser("~"), "Desktop", f"{title}.mp4")
        download_video(video_url,save_path)