import urllib.request
import base64
import re
import os

# 目标源 URL 和输出文件名
SOURCE_URL = "http://rihou.cc:555/gggg.nzk"
OUTPUT_FILE = "playlist.m3u"

def fetch_content(url):
    """获取网络内容，伪装 User-Agent 以防被屏蔽"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read()

def convert_to_m3u(raw_bytes):
    """解析并转换为标准的 M3U8 格式"""
    # 尝试使用不同的编码解码
    try:
        text = raw_bytes.decode('utf-8')
    except UnicodeDecodeError:
        text = raw_bytes.decode('gbk', errors='ignore')

    # 检测是否为 Base64 编码 (如果没有明显的分隔符且长度较长，尝试解码)
    if not re.search(r'[\s,]', text) and len(text) > 50:
        try:
            text = base64.b64decode(text).decode('utf-8')
        except Exception:
            pass # 如果解码失败，继续使用原文本

    # 如果已经是 m3u 格式，直接返回
    if text.strip().startswith('#EXTM3U'):
        return text

    # 解析常见的 '频道名,URL' 格式
    m3u_lines = ['#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"']
    current_group = "未分类"

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
            
        # 识别分组标签 (通常格式为: 分组名,#genre#)
        if '#genre#' in line:
            current_group = line.split(',')[0].strip()
        elif ',' in line:
            parts = line.split(',', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                url = parts[1].strip()
                # 过滤掉无效的空行或非 HTTP 开头的无效内容
                if url.startswith('http') or url.startswith('rtmp') or url.startswith('p3p'):
                    m3u_lines.append(f'#EXTINF:-1 group-title="{current_group}",{name}')
                    m3u_lines.append(url)

    return '\n'.join(m3u_lines)

def main():
    print(f"开始抓取直播源: {SOURCE_URL}")
    try:
        raw_bytes = fetch_content(SOURCE_URL)
        print("抓取成功，开始解析转换...")
        
        m3u_content = convert_to_m3u(raw_bytes)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
            
        print(f"转换成功！文件已保存至: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"发生错误: {e}")
        exit(1) # 抛出非零退出码，让 GitHub Actions 标记为失败

if __name__ == '__main__':
    main()
