import subprocess

steps = [
    "python -m crawlers.vbpl_crawler",
    "python -m crawlers.vbpl_processor",
    "python -m crawlers.vbpl_catalog",
    "python -m parsers.build_articles"
]

for step in steps:
    subprocess.run(step, shell=True, check=True)