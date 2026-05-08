# テストデータ管理規約

## テスト用タグ

テスト目的で作成されたノートには、Frontmatter に以下のタグを付与する：

```yaml
tags: _test_
```

### 命名規則

| 用途 | タグ | 意味 |
|------|------|------|
| 汎用テスト | `_test_` | 全テストデータ共通。DBクリーンアップ時の識別用 |
| パフォーマンステスト | `_test_`, `_perf_` | パフォーマンス計測用ダミーデータ |
| 特定機能テスト | `_test_`, `_test_fts_` 等 | 機能別テストデータ |

### 運用ルール

1. **テストファイルは `dropzone/duplicates/` に配置** — 本番 `processed/` を汚染しない
2. **テスト後は物理削除** — `dropzone/duplicates/test-*.md` は使い捨て
3. **DBクリーンアップ** — テスト完了後、`Note.objects.filter(tags__slug='_test_').delete()` で全テストノートを一括削除可能
4. **`_test_` タグは検索対象外** — 将来、検索APIで `_test_` タグをデフォルト除外にする拡張余地あり

### テストファイル命名

```
dropzone/duplicates/test-{連番}.md       # 汎用テスト
dropzone/duplicates/test-perf-{連番}.md  # パフォーマンステスト
dropzone/duplicates/test-fts-{連番}.md   # FTS5検索テスト
```

---

## 開発ログ

`logs/` ディレクトリおよび `*.log` ファイルは `.gitignore` 対象。
システム開発完了後、`logs/` ディレクトリごと削除すること。
