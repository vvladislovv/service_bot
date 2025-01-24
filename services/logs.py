from loguru import logger
import sys, os
from services.database import insert_user, Logs_history

def format_record(record):
    frame = sys._getframe(6)
    return "{time:YYYY-MM-DD HH:mm:ss} | {name}:{function}:{line} | {level} | {message}\n"

def file_create(TypeLog: str, Text: str) -> None:
    logger.remove()  

    logger.add(sys.stdout, format=format_record)

async def setup_logging():
    file_create()
    
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    for level in log_levels:
        logger.add(
            f"./logs/Loggure_file/{level.lower()}_file.log",
            level=level,
            format=format_record,
            rotation="1 MB",
            enqueue=True,
            filter=lambda record, level=level: record["level"].name == level
        )

#setup_logging()

async def logs_bot(TypeLog: str, Text: str) -> None:
    await setup_logging()

    valid_log_types = ["error", "warning", "info", "debug"]
    if TypeLog.lower() not in valid_log_types:
        logger.warning(f"Unknown log type: {TypeLog}")
        TypeLog = "warning"  
    

    log_method = getattr(logger, TypeLog.lower())
    log_method(Text)
    

    #await insert_user(Logs_history, ["type_log", "message"], [TypeLog, Text])
    
    
    




