#!/usr/bin/env python
# src/research_crew/main.py
import os
from pathlib import Path

from dotenv import load_dotenv


os.makedirs('output', exist_ok=True)

CURRENT = Path(__file__).resolve()
ROOT_DIR = CURRENT.parents[2]  # 确保找到根目录
load_dotenv(ROOT_DIR / ".env")
from agent import TestAgentApp
from config import config






if __name__ == "__main__":
    app=TestAgentApp(dataset_name='login')
    for _ in app.stream_run(debug=True):
        pass

