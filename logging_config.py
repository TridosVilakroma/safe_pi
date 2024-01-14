import logging,json,os
from logging.handlers import RotatingFileHandler

#build log dir-tree if necessary
os.makedirs("logs/log_files/debug", exist_ok=True)
os.makedirs("logs/log_files/info", exist_ok=True)
os.makedirs("logs/log_files/errors", exist_ok=True)

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
    """
    def __init__(self, fmt_dict: dict = None, time_format: str = "%Y-%m-%dT%H:%M:%S", msec_format: str = "%s.%03dZ"):
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Overwritten to look for the attribute in the format dict values instead of the fmt string.
        """
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string.
        KeyError is raised if an unknown attribute is provided in the fmt_dict. 
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is manipulated and dumped as JSON
        instead of a string.
        """
        record.message = record.getMessage()
        
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)

class LevelFilter(logging.Filter):
    '''Custom filter to isolate and allow through only the given level'''
    def __init__(self,filter_level, name: str = "") -> None:
        super().__init__(name)
        self.filter_level=filter_level
    def filter(self, record):
        return record.levelno == self.filter_level

debug_handler=RotatingFileHandler('logs/log_files/debug/debug.log', maxBytes=2*1024*1024, backupCount=3)
debug_handler.setLevel(logging.DEBUG)
debug_formatter=JsonFormatter(
    {"text": "message",
    "file": "filename",
    "line": "lineno",
    "function": "funcName",
    "time": "asctime",
    "path": "pathname",
    "thread": "threadName",
    "threadID": "thread"})
debug_handler.setFormatter(debug_formatter)
debug_filter=LevelFilter(logging.DEBUG)
debug_handler.addFilter(debug_filter)

info_handler=RotatingFileHandler('logs/log_files/info/info.log', maxBytes=2*1024*1024, backupCount=3)
info_handler.setLevel(logging.INFO)
info_formatter=JsonFormatter(
    {"text": "message",
    "file": "filename",
    "function": "funcName",
    "time": "asctime"})
info_handler.setFormatter(info_formatter)
info_filter=LevelFilter(logging.INFO)
info_handler.addFilter(info_filter)

error_handler=RotatingFileHandler('logs/log_files/errors/error.log', maxBytes=2*1024*1024, backupCount=3)
error_handler.setLevel(logging.WARNING)#get all levels >= warning
error_formatter=JsonFormatter(
    {"level": "levelname",
     "text": "message",
    "file": "filename",
    "line": "lineno",
    "function": "funcName",
    "time": "asctime",
    "path": "pathname",
    "thread": "threadName",
    "threadID": "thread"})
error_handler.setFormatter(error_formatter)

logger=logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
logger.propagate = False
logger.addHandler(debug_handler)
logger.addHandler(info_handler)
logger.addHandler(error_handler)
