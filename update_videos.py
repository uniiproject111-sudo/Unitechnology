import re
from pathlib import Path

ROOT = Path(r"f:\year4\finale\code")
APP_PY = ROOT / "app.py"
TEMPLATES = ROOT / "templates"

REQUESTED_COUNTS = {
    "word": 5, "excel": 3, "powerpoint": 2, "teams": 1, "outlook": 1, 
    "onenote": 2, "access": 2, "photoshop": 3, "ilustrator": 1, "canva": 2, 
    "indesign": 1, "premiere": 1, "capcut": 4, "filmora": 2, "lightroom": 1, 
    "panoramamaker": 1, "audacity": 2, "audition": 1, "wordpress": 5, 
    "googleclassroom": 2, "googledrive": 2, "googleforms": 2, "googlesites": 1, 
    "claudeai": 5, "klingai": 2, "openread": 1, "notebooklm": 1, "flowai": 1, 
    "لهجاتي": 1, "figma": 5
}

BASE_MULTIPLIER = {
    "word": 10, "excel": 11, "powerpoint": 12, "teams": 13, "outlook": 14,
    "onenote": 15, "access": 16, "photoshop": 17, "ilustrator": 18, "canva": 19,
    "indesign": 20, "premiere": 21, "capcut": 22, "filmora": 23, "lightroom": 24,
    "panoramamaker": 25, "audacity": 26, "audition": 27, "wordpress": 28,
    "googleclassroom": 29, "googledrive": 30, "googleforms": 31, "googlesites": 32,
    "claudeai": 33, "klingai": 34, "openread": 35, "notebooklm": 36, "flowai": 37,
    "لهجاتي": 38, "figma": 39
}

PAGE_MAP = {
    "word": "MicrosoftWord", "excel": "MicrosoftExcel", "powerpoint": "powerpoint",
    "teams": "MicrosoftTeams", "outlook": "MicrosoftOutlook", "onenote": "MicrosoftOneNote",
    "access": "MicrosoftAccess", "photoshop": "Photoshop", "ilustrator": "Ilustrator",
    "canva": "Canva", "indesign": "InDesign", "premiere": "premiere", "capcut": "CapCut",
    "filmora": "Filmora", "lightroom": "Lightroom", "panoramamaker": "PanoramaMaker",
    "audacity": "Audacity", "audition": "Audition", "wordpress": "WordPress",
    "googleclassroom": "googleclassroom", "googledrive": "Googledrive", "googleforms": "GoogleForms",
    "googlesites": "GoogleSites", "claudeai": "claudeai", "klingai": "KlingAI",
    "openread": "Openread", "notebooklm": "NotebookLM", "flowai": "FlowAI",
    "لهجاتي": "لهجاتي", "figma": "figma"
}

def get_ids(pkg):
    base = BASE_MULTIPLIER[pkg]
    count = REQUESTED_COUNTS[pkg]
    return [base * 10 + i + 1 for i in range(count)]

def update_app_py():
    with open(APP_PY, 'r', encoding='utf-8') as f:
        content = f.read()

    new_dict_str = "COURSE_VIDEO_IDS = {\n"
    for pkg in REQUESTED_COUNTS:
        ids = get_ids(pkg)
        new_dict_str += f'    "{pkg}": {ids},\n'
    new_dict_str = new_dict_str.rstrip(",\n") + "\n}"
    
    pattern = re.compile(r'COURSE_VIDEO_IDS\s*=\s*\{.*?\n\}', re.DOTALL)
    new_content = pattern.sub(new_dict_str, content)
    
    with open(APP_PY, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated app.py")

def update_htmls():
    for pkg, count in REQUESTED_COUNTS.items():
        page_name = PAGE_MAP[pkg]
        html_file = TEMPLATES / f"{page_name}.html"
        
        if not html_file.exists():
            print(f"Skipping {html_file.name} - not found")
            continue
            
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        ids = get_ids(pkg)
        
        videos_jinja = "{% set videos = [\n"
        for i, vid in enumerate(ids):
            videos_jinja += f"        {{'id': {vid}, 'yt_id': 'dQw4w9WgXcQ'}}"
            if i < len(ids) - 1:
                videos_jinja += ",\n"
            else:
                videos_jinja += "\n"
        videos_jinja += "    ] %}"
        
        pattern = re.compile(r'{%\s*set\s+videos\s*=\s*\[.*?\]\s*%}', re.DOTALL)
        
        if not pattern.search(content):
            print(f"Could not find video block in {html_file.name}")
            continue
            
        new_content = pattern.sub(videos_jinja, content)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {html_file.name}")

if __name__ == '__main__':
    update_app_py()
    update_htmls()
