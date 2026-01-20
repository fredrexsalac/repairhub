from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0007_appointment_proof_image_alter_appointment_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessageReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(choices=[('admin', 'Admin Crew')], default='admin', max_length=20)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'admin',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name='message_replies',
                        to='appointments.adminuser',
                    ),
                ),
                (
                    'message',
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name='replies',
                        to='appointments.contactmessage',
                    ),
                ),
            ],
            options={
                'db_table': 'contact_message_replies',
                'ordering': ['created_at'],
            },
        ),
    ]
