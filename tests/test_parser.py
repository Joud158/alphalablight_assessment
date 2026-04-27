from alphalablite.parser import parse_script

def test_parser_accepts_single_line_assignments():
    assignments = parse_script("price = Fetch{OneMinuteGoldPrices}{}\n")
    assert len(assignments) == 1
    assert assignments[0].target == "price"
    assert assignments[0].transformation == "Fetch"
    assert assignments[0].config_args == ("OneMinuteGoldPrices",)
    assert assignments[0].series_args == ()

def test_parser_accepts_split_assignment_lines():
    assignments = parse_script(
        """
        price
        = Fetch{OneMinuteGoldPrices}{}
        fast
        = ExponentialMovingAverage{0.3}{price}
        """
    )
    assert [item.target for item in assignments] == ["price", "fast"]