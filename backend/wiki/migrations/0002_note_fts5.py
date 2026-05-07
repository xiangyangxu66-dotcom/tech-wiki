# Generated migration — FTS5 full-text search virtual table
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('wiki', '0001_initial'),
    ]

    operations = [
        # FTS5 virtual table with content sync (external content)
        migrations.RunSQL(
            """CREATE VIRTUAL TABLE wiki_note_fts USING fts5(
                title,
                content,
                content=wiki_note,
                content_rowid=id
            )""",
            "DROP TABLE IF EXISTS wiki_note_fts",
        ),
        # INSERT trigger — keeps FTS5 index in sync
        migrations.RunSQL(
            """CREATE TRIGGER wiki_note_fts_insert AFTER INSERT ON wiki_note
            BEGIN
                INSERT INTO wiki_note_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END""",
            "DROP TRIGGER IF EXISTS wiki_note_fts_insert",
        ),
        # DELETE trigger
        migrations.RunSQL(
            """CREATE TRIGGER wiki_note_fts_delete AFTER DELETE ON wiki_note
            BEGIN
                INSERT INTO wiki_note_fts(wiki_note_fts, rowid, title, content)
                VALUES ('delete', old.id, old.title, old.content);
            END""",
            "DROP TRIGGER IF EXISTS wiki_note_fts_delete",
        ),
        # UPDATE trigger
        migrations.RunSQL(
            """CREATE TRIGGER wiki_note_fts_update AFTER UPDATE ON wiki_note
            BEGIN
                INSERT INTO wiki_note_fts(wiki_note_fts, rowid, title, content)
                VALUES ('delete', old.id, old.title, old.content);
                INSERT INTO wiki_note_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END""",
            "DROP TRIGGER IF EXISTS wiki_note_fts_update",
        ),
    ]
