from app.dao.base import BaseDAO
from app.chat.models import Messages


class MessagesDAO(BaseDAO[Messages]):
    model = Messages
    
