#!/usr/bin/env python3
"""Decode and inspect the Centris q= parameter."""
import base64
import gzip
import json

# The q= parameter from the Sherbrooke search URL
q_param = "H4sIAAAAAAAACl2MQQuCQBCF_8uePVTHbmEQEURkeBEPmz51aGpldq0W8b-3YgfxNt9735tePdmqrVqpSN3FPCCxKRGCwKaqqMAJfsLO4gBTi24bnzS6RditImXHMyV8AmZ5YGgpmrN-_r9UxA7yLysClzbV3I3rrJ-CYxnUWDvURnyYvMc-RFdYKvFypFkN0VxOwEyv-uZbzPxEMxbiRUwLcX5hXhjfhRmT83uyTqhwO-aZvN6oIR9-ZJ3voSoBAAA"

# Fix base64url padding
padded = q_param.replace('-', '+').replace('_', '/')
padded += '=' * (4 - len(padded) % 4)

try:
    decoded_bytes = base64.b64decode(padded)
    decompressed = gzip.decompress(decoded_bytes)
    data = json.loads(decompressed.decode('utf-8'))
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
