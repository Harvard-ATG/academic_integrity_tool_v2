"""Replace TinyMCE HTMLField with plain TextField on both models.

Part of the TinyMCE → Quill editor migration. At the database level,
both tinymce.models.HTMLField and django.db.models.TextField map to
PostgreSQL TEXT — this migration changes only the Django field class,
not the column type. No data migration is needed.

The body field now stores either:
  - Quill Delta JSON (new submissions from the Quill editor)
  - Plain text or HTML (legacy data from TinyMCE)

Both formats are handled at display time by the |render_body template filter
(see policy_wizard/quill_utils.py).

This also adds the validate_no_script_tags validator to PolicyTemplates.body,
which previously had none (the TinyMCE HTMLField on line 10 of models.py was
silently overridden by a bare TextField on line 11 — a bug now fixed).
"""

from django.db import migrations, models
import policy_wizard.validators


class Migration(migrations.Migration):

    dependencies = [
        ('policy_wizard', '0002_auto_20210629_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policies',
            name='body',
            field=models.TextField(validators=[policy_wizard.validators.validate_no_script_tags]),
        ),
        migrations.AlterField(
            model_name='policytemplates',
            name='body',
            field=models.TextField(validators=[policy_wizard.validators.validate_no_script_tags]),
        ),
    ]
