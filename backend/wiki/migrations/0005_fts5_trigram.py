# Migration: Change FTS5 tokenizer from unicode61 to trigram
# trigram = 3-char sliding window, enables Japanese substring matching
# 「全文検索」→ trigrams: 全文検, 文検索 → search "検索" matches "文検索"

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0004_note_fts5'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- Drop old FTS5 table and triggers
                DROP TRIGGER IF EXISTS wiki_note_fts_ai;
                DROP TRIGGER IF EXISTS wiki_note_fts_ad;
                DROP TRIGGER IF EXISTS wiki_note_fts_au;
                DROP TABLE IF EXISTS wiki_note_fts;

                -- Recreate with trigram tokenizer
                CREATE VIRTUAL TABLE wiki_note_fts USING fts5(
                    title,
                    content,
                    content='wiki_note',
                    content_rowid='id',
                    tokenize='trigram'
                );

                -- Trigger: INSERT → index new row
                CREATE TRIGGER wiki_note_fts_ai AFTER INSERT ON wiki_note BEGIN
                    INSERT INTO wiki_note_fts(rowid, title, content)
                    VALUES (new.id, new.title, new.content);
                END;

                -- Trigger: DELETE → remove from index
                CREATE TRIGGER wiki_note_fts_ad AFTER DELETE ON wiki_note BEGIN
                    INSERT INTO wiki_note_fts(wiki_note_fts, rowid, title, content)
                    VALUES ('delete', old.id, old.title, old.content);
                END;

                -- Trigger: UPDATE → replace old with new
                CREATE TRIGGER wiki_note_fts_au AFTER UPDATE ON wiki_note BEGIN
                    INSERT INTO wiki_note_fts(wiki_note_fts, rowid, title, content)
                    VALUES ('delete', old.id, old.title, old.content);
                    INSERT INTO wiki_note_fts(rowid, title, content)
                    VALUES (new.id, new.title, new.content);
                END;

                -- Rebuild index with existing data
                INSERT INTO wiki_note_fts(wiki_note_fts) VALUES ('rebuild');
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS wiki_note_fts_ai;
                DROP TRIGGER IF EXISTS wiki_note_fts_ad;
                DROP TRIGGER IF EXISTS wiki_note_fts_au;
                DROP TABLE IF EXISTS wiki_note_fts;

                CREATE VIRTUAL TABLE wiki_note_fts USING fts5(
                    title,
                    content,
                    content='wiki_note',
                    content_rowid='id',
                    tokenize='unicode61 remove_diacritics 2'
                );

                CREATE TRIGGER wiki_note_fts_ai AFTER INSERT ON wiki_note BEGIN
                    INSERT INTO wiki_note_fts(rowid, title, content)
                    VALUES (new.id, new.title, new.content);
                END;
                CREATE TRIGGER wiki_note_fts_ad AFTER DELETE ON wiki_note BEGIN
                    INSERT INTO wiki_note_fts(wiki_note_fts, rowid, title, content)
                    VALUES ('delete', old.id, old.title, old.content);
                END;
                CREATE TRIGGER wiki_note_fts_au AFTER UPDATE ON wiki_note BEGIN
                    INSERT INTO wiki_note_fts(wiki_note_fts, rowid, title, content)
                    VALUES ('delete', old.id, old.title, old.content);
                    INSERT INTO wiki_note_fts(rowid, title, content)
                    VALUES (new.id, new.title, new.content);
                END;
                INSERT INTO wiki_note_fts(wiki_note_fts) VALUES ('rebuild');
            """,
        ),
    ]
