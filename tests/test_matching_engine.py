from app.matching_engine import determine_order_status


def test_determine_order_status_buy_filled():
    # A buy price of 1000.0 is way above AAPL ask (~185.10), so it must fill
    status = determine_order_status("AAPL", "BUY", 1000.0)
    assert status == "FILLED"


def test_determine_order_status_buy_acked():
    # A buy price of 1.0 is way below AAPL ask (~185.10), so it must ack
    status = determine_order_status("AAPL", "BUY", 1.0)
    assert status == "ACKED"


def test_determine_order_status_sell_filled():
    # A sell price of 1.0 is way below AAPL bid (~184.90), so it must fill
    status = determine_order_status("AAPL", "SELL", 1.0)
    assert status == "FILLED"


def test_determine_order_status_sell_acked():
    # A sell price of 1000.0 is way above AAPL bid (~184.90), so it must ack
    status = determine_order_status("AAPL", "SELL", 1000.0)
    assert status == "ACKED"


def test_determine_order_status_rejected_symbol():
    status = determine_order_status("INVALID_SYM", "BUY", 100.0)
    assert status == "REJECTED"


def test_determine_order_status_case_insensitive():
    status = determine_order_status("aapl", "buy", 1000.0)
    assert status == "FILLED"
