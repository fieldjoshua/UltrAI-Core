import os
import sys

print("START", flush=True)
sys.stdout.write("STDOUT TEST\n")
sys.stderr.write("STDERR TEST\n")
os.write(1, b"DIRECT STDOUT TEST\n")
os.write(2, b"DIRECT STDERR TEST\n")
print("END", flush=True)
