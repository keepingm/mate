from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from config.config import config


@dataclass(frozen=True)
class DatasetLoader:
    dataset_name: str
    dataset_root: Path
    config_path: Path

    srs_path: Path
    uml_class_path: Path
    uml_sequence_path: Path

    srs_text: str
    uml_class_text: str
    uml_sequence_text: str

    config: Dict[str, Any]


def load_dataset(
    dataset_name: str,
    *,
    encoding: str = "utf-8",
    strict: bool = True,
) -> DatasetLoader:
    """
    读取 <global_prefix>/<dataset_name>/config.json，并加载 PRD、UML_class 文件内容。

    参数:
      - dataset_name: 数据集目录名（例如 "dior", "rsod"）
      - global_prefix: 所有数据集所在的根目录（全局前缀）
      - encoding: 文件编码
      - strict: True 时，缺失 key / 文件不存在会抛异常；False 时会用空字符串兜底

    返回:
      DatasetDocs: 包含 prd/uml_class 的文本内容、实际路径、以及完整 config
    """
    global_prefix = Path(config['dataset']['root_path'])
    dataset_root = Path(global_prefix).expanduser().resolve() / dataset_name
    config_path = dataset_root / "config.json"

    if strict and not config_path.exists():
        raise FileNotFoundError(f"config.json not found: {config_path}")

    # 读取并解析 config.json
    try:
        config_obj: Dict[str, Any] = json.loads(config_path.read_text(encoding=encoding))
    except FileNotFoundError:
        if strict:
            raise
        config_obj = {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {config_path}: {e}") from e

    # 取 srs / UML_class 的相对路径
    srs_rel = config_obj.get("SRS")
    uml_class_rel = config_obj.get("UML_class")
    uml_sequence_rel = config_obj.get("UML_sequence")

    if strict:
        if not srs_rel:
            raise KeyError(f'Missing or empty key "PRD" in {config_path}')
        if not uml_class_rel:
            raise KeyError(f'Missing or empty key "UML_class" in {config_path}')

    srs_path = (dataset_root / srs_rel).resolve() if srs_rel else (dataset_root / "MISSING_PRD")
    uml_class_path = (dataset_root / uml_class_rel).resolve() if uml_class_rel else (dataset_root / "MISSING_UML_class")
    uml_sequence_path = (dataset_root / uml_sequence_rel).resolve() if uml_sequence_rel else (dataset_root / "MISSING_UML_class")

    # 读取文件内容
    def _read_text(p: Path) -> str:
        if p.exists():
            return p.read_text(encoding=encoding)
        if strict:
            raise FileNotFoundError(f"File not found: {p}")
        return ""

    srs_text = _read_text(srs_path)
    uml_class_text = _read_text(uml_class_path)
    uml_sequence_text = _read_text(uml_sequence_path)

    return DatasetLoader(
        dataset_name=dataset_name,
        dataset_root=dataset_root,
        config_path=config_path,
        srs_path=srs_path,
        uml_class_path=uml_class_path,
        uml_sequence_path=uml_sequence_path,
        srs_text=srs_text,
        uml_class_text=uml_class_text,
        uml_sequence_text=uml_sequence_text,
        config=config_obj,
    )


# ---- 使用示例 ----
if __name__ == "__main__":

    docs = load_dataset(
        "hone",
        strict=True,
    )
    print("PRD path:", docs.srs_path)
    print("UML_class path:", docs.uml_class_path)
    print("PRD content preview:", docs.srs_text)
