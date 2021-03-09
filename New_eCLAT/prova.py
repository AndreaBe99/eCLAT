import re

with open('test.eclat', "r") as f:
    text_input = f.read()
for line_num, line in enumerate(text_input.splitlines(), 0):
    if line.strip():
        if not line.startswith("#"):
            print((1+line_num), line)
