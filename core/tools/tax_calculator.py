"""Tính các loại thuế VN: VAT, TNCN, TNDN, NTT, lệ phí môn bài."""
from __future__ import annotations
import re
from core.tools.base_tool import BaseTool, ToolResult


TNCN_BRACKETS = [
    (5_000_000, 0.05),
    (10_000_000, 0.10),
    (18_000_000, 0.15),
    (32_000_000, 0.20),
    (52_000_000, 0.25),
    (80_000_000, 0.30),
    (float("inf"), 0.35),
]


class TaxCalculator(BaseTool):
    name = "tax_calculator"
    description = "Tính VAT, TNCN, TNDN, Thuế nhà thầu, lệ phí môn bài VN."

    def run(self, query: str, **kwargs) -> ToolResult:
        parts = query.split()
        if len(parts) < 2:
            return ToolResult(data={}, notes="invalid format")

        tax_type = parts[0].lower()
        amount = self._parse_amount(parts[1])
        params = self._parse_kv(parts[2:])

        if tax_type == "vat":
            rate = float(params.get("rate", 10)) / 100
            vat = int(amount * rate)
            return ToolResult(
                data={"base_vnd": amount, "rate_pct": rate * 100,
                      "vat_amount_vnd": vat, "total_vnd": amount + vat},
                sources=["Luật Thuế GTGT 2008 + sửa đổi 2024"],
            )

        if tax_type == "tncn":
            deduction = self._parse_amount(params.get("deduction", "11000000"))
            taxable = max(0, amount - deduction)
            tax = self._tncn_progressive(taxable)
            return ToolResult(
                data={"income_vnd": amount, "deduction_vnd": deduction,
                      "taxable_vnd": taxable, "tax_vnd": tax,
                      "net_vnd": amount - tax},
                sources=["Luật Thuế TNCN 2007 + sửa đổi"],
            )

        if tax_type == "tndn":
            rate = float(params.get("rate", 20)) / 100
            tax = int(amount * rate)
            return ToolResult(
                data={"profit_vnd": amount, "rate_pct": rate * 100,
                      "tax_vnd": tax, "net_vnd": amount - tax},
                sources=["Luật Thuế TNDN 2008 + sửa đổi"],
            )

        if tax_type == "foreign_contractor":
            service = params.get("service", "general")
            ntt_rate, vat_rate = self._foreign_contractor_rates(service)
            ntt = int(amount * ntt_rate)
            vat = int(amount * vat_rate)
            return ToolResult(
                data={"base_vnd": amount, "service": service,
                      "ntt_rate_pct": ntt_rate * 100, "ntt_amount_vnd": ntt,
                      "vat_rate_pct": vat_rate * 100, "vat_amount_vnd": vat,
                      "total_tax_vnd": ntt + vat},
                sources=["TT 103/2014/TT-BTC", "TT 60/2012/TT-BTC"],
            )

        return ToolResult(data={}, notes=f"Unknown tax type: {tax_type}")

    @staticmethod
    def _parse_amount(s) -> int:
        s = str(s)
        return int(re.sub(r"[_,.]", "", s))

    @staticmethod
    def _parse_kv(parts: list[str]) -> dict:
        out = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                out[k] = v
        return out

    @staticmethod
    def _tncn_progressive(taxable: int) -> int:
        tax = 0
        prev = 0
        for ceil, rate in TNCN_BRACKETS:
            if taxable <= prev:
                break
            slice_amount = min(taxable, ceil) - prev
            tax += int(slice_amount * rate)
            prev = ceil
            if taxable <= ceil:
                break
        return tax

    @staticmethod
    def _foreign_contractor_rates(service: str) -> tuple[float, float]:
        rates = {
            "ads": (0.05, 0.05),
            "software": (0.05, 0.05),
            "consulting": (0.05, 0.05),
            "transport": (0.02, 0.03),
            "general": (0.05, 0.05),
        }
        return rates.get(service.lower(), rates["general"])
