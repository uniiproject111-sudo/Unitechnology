import re
from pathlib import Path

TEMPLATES = Path(r"f:\year4\finale\code\templates")

fallback_html = '<a href="https://youtu.be/{{ v.yt_id }}" target="_blank" style="display:inline-block; margin-bottom:12px; color:#fff; text-decoration:underline; font-size:14px; font-weight:600; background:rgba(0,0,0,0.2); padding:6px 12px; border-radius:8px;">🔗 إذا كان الفيديو غير متاح، اضغط هنا لمشاهدته على يوتيوب</a><br>\n      '

count = 0
for html_file in TEMPLATES.glob("*.html"):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '<div class="video-actions"><button class="btn-complete' in content:
        new_content = content.replace(
            '<div class="video-actions"><button class="btn-complete',
            f'<div class="video-actions">\n      {fallback_html}<button class="btn-complete'
        )
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1
        print(f"Patched {html_file.name}")

print(f"Total files patched: {count}")
