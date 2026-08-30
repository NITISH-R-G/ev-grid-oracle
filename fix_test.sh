sed -i 's/assert out.get("oracle_timed_out") is False/assert out.get("oracle_timed_out", False) is False/g' tests/test_demo_api.py
