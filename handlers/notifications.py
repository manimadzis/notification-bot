from collections import defaultdict
from typing import Dict, List

from schedule import Notifier

notifications: Dict[int, List[Notifier]] = defaultdict(lambda: [])
