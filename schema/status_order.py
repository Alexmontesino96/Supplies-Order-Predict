import os
import json
from enum import Enum
from dotenv import load_dotenv

load_dotenv()
STATUS = json.loads(os.getenv('STATUS'))


class Status_Order(Enum):
    PENDING = STATUS[0]
    IN_PROGRESS = STATUS[1]
    COMPLETED = STATUS[2]
