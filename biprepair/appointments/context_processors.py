from __future__ import annotations

from .constants import SESSION_CLIENT_KEY
from .models import ClientAccount


def client_user(request):
    client = None
    client_id = request.session.get(SESSION_CLIENT_KEY)
    if client_id:
        client = ClientAccount.objects.filter(id=client_id).first()
    return {
        'client_user': client,
        'is_client_authenticated': bool(client),
    }
