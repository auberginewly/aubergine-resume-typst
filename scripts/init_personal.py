"""仅创建缺失的个人内容文件，重复运行不会覆盖已有简历。"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    private = ROOT / "resume/private"
    try:
        private.mkdir(parents=True, exist_ok=True)
        for name in ("content.toml", "content.en.toml"):
            source = ROOT / "resume" / name
            destination = private / name
            # 先完整读取样例，避免源文件读取失败时留下空的个人文件。
            content = source.read_bytes()
            try:
                # 排他创建：即使另一进程刚创建了文件，也绝不截断或覆盖。
                output = destination.open("xb")
            except FileExistsError:
                if destination.is_dir():
                    raise IsADirectoryError("个人文件路径已被目录占用：" + str(destination))
                print("跳过已有文件：resume/private/" + name)
                continue
            with output:
                output.write(content)
            print("已创建：resume/private/" + name)
    except OSError as error:
        print("初始化失败：" + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
