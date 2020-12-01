import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
root.addHandler(handler)
