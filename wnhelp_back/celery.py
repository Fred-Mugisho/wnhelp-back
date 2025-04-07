import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wnhelp_back.settings')

app = Celery('wnhelp_back')

# Utilise le Redis du serveur
# app.conf.broker_url = 'redis://:TON_MOT_DE_PASSE@127.0.0.1:PORT/0'

# Charge les tâches depuis toutes les apps installées
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['utils.functions'])
