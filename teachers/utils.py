import re

def grade_key(name):
    if not name:
        return ''
    name = name.lower()
    m = re.search(r'(\d+)', name)
    if 'kindergarten' in name or name.startswith('kg'):
        return f'kg{m.group(1)}' if m else 'kg'
    return f'g{m.group(1)}' if m else name.strip()