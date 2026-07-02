#!/bin/bash
set -e
python -m pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 &
streamlit run frontend.py --server.address 0.0.0.0 --server.port 8501
