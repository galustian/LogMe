import subprocess
import time

while True:
    st = subprocess.getoutput('./get_window.sh')
    print(st.strip())
    time.sleep(1)