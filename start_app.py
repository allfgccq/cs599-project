"""启动 TravAgent 应用"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "chainlit", "run", "app.py", "-w"], 
                   cwd="d:\\trae\\TravAgent",
                   shell=True)
