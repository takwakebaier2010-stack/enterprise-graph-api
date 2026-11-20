import os, sys
sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from strawberry.printer import print_schema
from core.schema_optimized import schema_optimized

print(print_schema(schema_optimized))
