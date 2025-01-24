#from .chat import router as chat_router
from .common import router as common_router
from .Nerulas import *

__all__ = [
    #"chat_router",
    "common_router"
]

routers = [
   # chat_router,
    common_router
]