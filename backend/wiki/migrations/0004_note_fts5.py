# Generated migration: FTS5 full-text search for Note

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_note_has_mermaid'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- FTS5 virtual table with external content (always in sync via triggers)
                CREATE VIRTUAL TABLE wiki_note_fts USING fts5(
                    title,
                    content,
                    content='wiki_note',
                    content_rowid='id',
                    tokenize='unicode61 remove_diacritics 2'
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

                -- Populate with existing data
                INSERT INTO wiki_note_fts(wiki_note_fts) VALUES ('rebuild');
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS wiki_note_fts_ai;
                DROP TRIGGER IF EXISTS wiki_note_fts_ad;
                DROP TRIGGER IF EXISTS wiki_note_fts_au;
                DROP TABLE IF EXISTS wiki_note_fts;
            """,
        ),
    ]
