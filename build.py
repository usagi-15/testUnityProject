"""展示作品ホームページをビルドする。

使い方:
    python build.py            # dist/ にサイトを生成
    python build.py --serve    # 生成後、http://localhost:8000 で確認
"""

import argparse
import functools
import http.server
from pathlib import Path

from exhibition.builder import ROOT, build


def main() -> None:
    parser = argparse.ArgumentParser(description="展示作品ホームページを生成します。")
    parser.add_argument("--out", type=Path, default=ROOT / "dist", help="出力先（既定: dist）")
    parser.add_argument("--serve", action="store_true", help="生成後にローカルサーバーを起動する")
    parser.add_argument("--port", type=int, default=8000, help="サーバーのポート（既定: 8000）")
    args = parser.parse_args()

    written = build(args.out)
    print(f"{len(written)} ページを生成しました: {args.out}")

    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.out))
        with http.server.ThreadingHTTPServer(("", args.port), handler) as httpd:
            print(f"http://localhost:{args.port}/ で公開中（Ctrl+C で終了）")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
