import re
import sys

filepath = r"c:\Users\minec\OneDrive\Documents\AAST\code\templates\courses.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# We need to find each package-body and prepend the enroll button
# The package ID is in the id="..." of the package-section
def replacer(match):
    pkg_id = match.group(1)
    body_start = match.group(2)
    
    enroll_form = f"""
      <div style="text-align: center; margin-bottom: 20px;">
        {{% if user_name %}}
            {{% if '{pkg_id}' in enrolled_packages %}}
                <button class="btn-register" disabled style="background: #ccc; cursor: not-allowed; box-shadow: none;">تم التسجيل</button>
            {{% else %}}
                <form action="{{{{ url_for('enroll', package_id='{pkg_id}') }}}}" method="POST" style="display: inline;">
                   <button type="submit" class="btn-register" style="font-size: 16px; padding: 12px 36px;">سجل في هذه الحزمة لتبدأ التعلم</button>
                </form>
            {{% endif %}}
        {{% else %}}
            <a href="{{{{ url_for('login') }}}}" class="btn-register">سجل دخول للاشتراك</a>
        {{% endif %}}
      </div>
    """
    return f'<div class="package-section" id="{pkg_id}">\n{match.group(3)}\n{body_start}\n{enroll_form}'

# Regex logic: 
# 1. Match package-section id
# 2. Match everything until <div class="package-body">
pattern = re.compile(r'<div class="package-section"\s+id="([^"]+)">\s*(.*?(?:<div\s+class="package-body">|<div class="package-body">))', re.DOTALL)

new_content = pattern.sub(replacer, content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)
    
print("Updated courses.html")
