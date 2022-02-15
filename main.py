import subprocess
import sys
import os
import time
import base64
import hashlib
import hmac
import rich
import random
import shutil
import stat
import signal
from get import DC_CON

from rich import print
from rich import box
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
console = Console()
dccon = DC_CON()

def main():
    console.log(dccon.getList("광대콘"))
    console.log(dccon.getImageCDN("17221"))
    return 0

def sigint_handler(signal, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    try:
        main()
    except Exception as ex:
        console.log(ex)
        console.log("[bold][red][Important][/red][/bold] 처리되지 않은 오류가 발생했습니다.")
        exit(0)