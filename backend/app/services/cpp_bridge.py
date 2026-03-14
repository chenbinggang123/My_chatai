import json
import os
import subprocess
from pathlib import Path


def extract_features(chat_log: str, mode: str) -> dict:
    bin_path = os.getenv("CPP_FEATURE_BIN", "")# 这个环境变量 CPP_FEATURE_BIN 应该在部署环境中设置，指向 C++ 特征提取二进制文件的位置。它允许我们在 Python 代码中调用这个 C++ 程序来处理聊天记录并提取特征。
    if not bin_path:
        return {}

    target = Path(__file__).resolve().parents[3] / bin_path#这里什么意思？# 这行代码的意思是：从当前文件（cpp_bridge.py）的路径开始，向上回退三层目录，然后在那个目录下找到名为 bin_path 的可执行文件。也就是说，它构建了一个指向 C++ 特征提取二进制文件的完整路径。
    if not target.exists():
        return {}

    payload = {"chat_log": chat_log, "mode": mode}
    #这个chat_log是什么格式，里面的内容
    # chat_log 是一个字符串，通常包含用户与宠物之间的对话记录。它可能是一个多行文本，每行代表一次交流，例如：
    try:
        proc = subprocess.run(
            [str(target)],
            input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=5,
        )
        return json.loads(proc.stdout.decode("utf-8"))
    except (subprocess.SubprocessError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
