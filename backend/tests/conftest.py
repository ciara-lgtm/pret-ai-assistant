import os
import sys
from pathlib import Path

# Ensure tests use FakeAIService, not real Azure (set before app import)
os.environ["USE_FAKE_AI"] = "true"

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
