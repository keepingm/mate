from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Iterator


# ---------- 基础数据结构 ----------

@dataclass(frozen=True)
class Feature:
    name: str
    methods: List[str]
    requirements: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Module:
    module_id: str
    name: str
    classes: List[str]
    responsibility_summary: str
    reasons: Dict[str, Any]
    features: List[Feature]

    def iter_methods(self) -> Iterator[str]:
        """遍历该模块下所有方法"""
        for feature in self.features:
            for method in feature.methods:
                yield method

    def to_dict(self) -> Dict[str, Any]:
        """
        返回 Module 的 dict 表示（可 JSON 序列化）
        """
        return {
            "module_id": self.module_id,
            "name": self.name,
            "classes": self.classes,
            "responsibility_summary": self.responsibility_summary,
            "reasons": self.reasons,
            "features": [f.to_dict() for f in self.features],
        }

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        返回 Module 的 JSON 字符串表示
        """
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
        )

    def __str__(self) -> str:
        """
        类似 Java 的 toString()
        """
        return self.to_json()

# ---------- Memory 管理类 ----------

class Memory:
    """
    管理 modules.json 的内存表示
    支持：
      - 纯 JSON 文件
      - Markdown 文件（自动提取 ```json ... ``` 中的内容）
    """

    def __init__(self, json_path: str|Path):
        self.json_path = Path(json_path).resolve()
        self._modules: List[Module] = []

        self._load()

    def _load(self) -> None:
        if not self.json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.json_path}")

        # 读取整个文件内容为字符串
        text = self.json_path.read_text(encoding="utf-8")

        # 尝试 1：直接解析为 JSON（适用于纯 JSON 文件）
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            # 尝试 2：从 Markdown 的 ```json ... ``` 中提取 JSON
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
            if not match:
                raise ValueError(
                    f"File is not valid JSON and does not contain a ```json code block: {self.json_path}"
                )
            json_str = match.group(1).strip()
            if not json_str:
                raise ValueError(f"Empty JSON code block in file: {self.json_path}")
            try:
                raw = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON inside ```json block in {self.json_path}: {e}") from e

        # 验证结构
        modules_raw = raw.get("modules", [])
        if not isinstance(modules_raw, list):
            raise ValueError(f'"modules" must be a list in {self.json_path}')

        self._modules = [self._parse_module(m) for m in modules_raw]

    def _parse_module(self, data: Dict[str, Any]) -> Module:
        features = [
            Feature(
                name=f["name"],
                methods=f.get("methods", []),
                requirements=f.get("requirements", "")
            )
            for f in data.get("features", [])
        ]

        return Module(
            module_id=data["module_id"],
            name=data["name"],
            classes=data.get("classes", []),
            responsibility_summary=data.get("responsibility_summary", ""),
            reasons=data.get("reasons", {}),
            features=features
        )

    # ---------- 对外接口 ----------

    @property
    def modules(self) -> List[Module]:
        return self._modules

    def get_module_by_id(self, module_id: str) -> Module | None:
        return next((m for m in self._modules if m.module_id == module_id), None)

    def iter_modules(self) -> Iterator[Module]:
        return iter(self._modules)

    def iter_all_features(self) -> Iterator[Feature]:
        for module in self._modules:
            for feature in module.features:
                yield feature

    def iter_all_methods(self) -> Iterator[str]:
        for module in self._modules:
            yield from module.iter_methods()


if __name__ == '__main__':
    memory = Memory('/home/mgh/dev/projects/python_projects/mate/memory/working_memory/test_plan.json')
    modules = memory.modules
    for module in modules:
        print(module.__str__())

