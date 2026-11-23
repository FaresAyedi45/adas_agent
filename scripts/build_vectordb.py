# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_engine import build_vectordb

if __name__ == "__main__":
    print("Construction base vectorielle ADAS...")
    build_vectordb()
    print("Termine.")
