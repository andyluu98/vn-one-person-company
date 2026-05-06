from core.tools.tax_calculator import TaxCalculator


def test_vat_10_percent():
    tc = TaxCalculator()
    r = tc.run("vat 100000000 rate=10")
    assert r.data["vat_amount_vnd"] == 10_000_000
    assert r.data["total_vnd"] == 110_000_000


def test_tncn_progressive_brackets():
    tc = TaxCalculator()
    r = tc.run("tncn 50000000 deduction=11000000")
    assert r.data["taxable_vnd"] == 39_000_000


def test_foreign_contractor_tax_on_ad_spend():
    tc = TaxCalculator()
    r = tc.run("foreign_contractor 200000000 service=ads provider=facebook")
    assert r.data["ntt_amount_vnd"] == 10_000_000
    assert r.data["vat_amount_vnd"] == 10_000_000
