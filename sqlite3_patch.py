# sqlite3_patch.py
import pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3