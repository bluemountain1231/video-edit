#!/usr/bin/env python3
"""Create a lightweight semantic plan from koubo-edit transcript JSON.

This is an original bridge inspired by video-talkcraft's semantic planning
contract.  It does not import upstream code or models; it produces an
editable first pass that a director can correct before choosing visuals.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VOCAB = {
    "钩子", "论点", "例证", "数据", "对比", "列举", "定义", "步骤", "转折", "设问",
    "金句", "标题", "引用", "自我介绍", "介绍他人", "号召", "时间地点", "空间叙事",
    "机制", "选择", "过程演示", "章节", "转场", "强调", "氛围", "结尾",
}


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def infer(text: str, index: int, total: int) -> tuple[list[str], list[str], str]:
    sem: list[str] = []
    if index == 0:
        sem.append("钩子")
    if re.search(r"\d|百分之|几成|金额|分钟|小时|月份|年份", text):
        sem.append("数据")
    if "？" in text or "?" in text or has_any(text, ("吗", "为什么", "怎么", "如何", "难道")):
        sem.append("设问")
    if has_any(text, ("但是", "不过", "却", "然而", "其实", "反而")):
        sem.append("转折")
    if has_any(text, ("第一", "第二", "首先", "其次", "然后", "接着", "最后", "步骤", "先说", "下一步", "分三步")):
        sem.extend(["步骤", "列举"])
    if has_any(text, ("比如", "例如", "举个例子", "案例")):
        sem.append("例证")
    if has_any(text, ("是什么", "指的是", "所谓", "意思是", "定义")):
        sem.append("定义")
    if has_any(text, ("我叫", "我是", "我的名字")):
        sem.append("自我介绍")
    if has_any(text, ("他是", "她是", "这位", "某某", "账号", "作者")):
        sem.append("介绍他人")
    if has_any(text, ("停止", "保存", "不要", "别再", "请", "记住", "做到", "建议", "应该")):
        sem.append("号召")
    if index == total - 1:
        sem.append("结尾")
    if not sem:
        sem.append("论点")
    sem = list(dict.fromkeys(sem))

    if "数据" in sem:
        need = ["量化"]
    elif "例证" in sem or "引用" in sem or "介绍他人" in sem:
        need = ["证据"]
    elif "定义" in sem or "机制" in sem or "步骤" in sem:
        need = ["结构"]
    elif "对比" in sem:
        need = ["对比"]
    elif "强调" in sem:
        need = ["强调"]
    else:
        need = ["无"]
    weight = "sub" if len(text) <= 7 and index not in (0, total - 1) else "main"
    return sem, need, weight


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("transcript", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    args = ap.parse_args()
    source = json.loads(args.transcript.read_text(encoding="utf-8"))
    segments = source.get("segments") or []
    sentences = []
    for i, segment in enumerate(segments):
        text = str(segment.get("text") or "").strip()
        sem, need, weight = infer(text, i, len(segments))
        sentences.append({
            "i": i,
            "start_ms": int(segment.get("start_ms") or 0),
            "end_ms": int(segment.get("end_ms") or 0),
            "text": text,
            "shot": "",
            "sem": sem,
            "entities": [],
            "need": need,
            "weight": weight,
        })
    payload = {
        "version": 1,
        "source": {"transcript": str(args.transcript)},
        "vocab": sorted(VOCAB),
        "sentences": sentences,
        "review": "Heuristics are a first pass; verify semantic labels before rendering.",
    }
    for sentence in sentences:
        unknown = set(sentence["sem"]) - VOCAB
        if unknown:
            raise SystemExit(f"unknown semantic labels: {sorted(unknown)}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"semantic plan: {len(sentences)} sentences -> {args.out}")


if __name__ == "__main__":
    main()
