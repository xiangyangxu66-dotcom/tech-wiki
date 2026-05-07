from django.db import migrations, models


def backfill_has_mermaid(apps, schema_editor):
    Note = apps.get_model('wiki', 'Note')
    for note in Note.objects.all().only('id', 'content'):
        has_mermaid = '```mermaid' in (note.content or '').lower()
        Note.objects.filter(id=note.id).update(has_mermaid=has_mermaid)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0002_note_content_hash_note_wiki_note_content_b17a2a_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='has_mermaid',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.RunPython(backfill_has_mermaid, noop_reverse),
    ]
