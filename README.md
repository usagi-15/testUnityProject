# 展示作品ホームページ

Python（標準ライブラリのみ）で展覧会の作品紹介サイトを生成します。

```bash
python build.py            # dist/ にサイトを生成
python build.py --serve    # 生成して http://localhost:8000 で確認
python -m unittest -v      # テスト
```

- 展覧会情報: `content/site.json`
- 作品データ: `content/works.json`（画像は `content/images/` に置き、`image` にファイル名を指定）

詳細は `notes/仕様.md` を参照してください。
