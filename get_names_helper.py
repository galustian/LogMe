import subprocess
import time

while True:
    st = subprocess.getoutput('./get_window.sh')
    print(st.strip())
    print(len(st.strip().split()))
    print()
    time.sleep(1)