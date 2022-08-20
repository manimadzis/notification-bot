from collections import defaultdict
from typing import Dict, List
import uuid
from schedule import Notifier


notifications: Dict[int, Dict[uuid.UUID, Notifier]] = defaultdict(lambda: {})

