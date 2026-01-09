import os
from typing import Optional, Type

import datetime
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WriteFileInput(BaseModel):
    """输入 schema: 要写入的文件路径和内容。"""
    path: str = Field(..., description="目标文件绝对路径")
    code: str = Field(..., description="要写入的 Python 代码内容")
    overwrite: Optional[bool] = Field(False, description="是否覆盖已有文件 (True = 覆盖, False = 追加)")


class WritePythonFileTool(BaseTool):
    name: str = "write_python_file"
    description: str = "Write given Python code to the specified file path."
    args_schema: Type[BaseModel] = WriteFileInput

    def _run(self, path: str, code: str, overwrite: bool = False) -> str:
        # 确保目录存在
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        mode = "w" if overwrite else "a"
        with open(path, mode, encoding="utf-8") as f:
            f.write(code)
            if not code.endswith("\n"):
                f.write("\n")
        log_entry = (
            f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Write to file: {path}\n"
            f"Overwrite: {overwrite}\n"
            f"{'-' * 50}\n"
        )
        # 日志文件路径：与当前脚本同目录下的 log.txt
        log_path = "log/log.txt"
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
        print('写入日志')
        return f"Wrote code to {path} (overwrite={overwrite})"
