import pytest
from conftest import tokens_in, curve_tokens_in, curve_pools_in

def test_swap(whale, zap, interface, governance_swaps, token_in, token_out):
    if token_in == token_out:
        pytest.skip("same token")
    if token_in.balanceOf(whale) == 0:
        pytest.skip("no token_in balance")

    token_in.transfer(zap, token_in.balanceOf(whale))
    amount_in = token_in.balanceOf(zap)
    print(f"{token_in.symbol()} amount: {amount_in / 10 ** token_in.decimals()}")
    before = token_out.balanceOf(zap)
    zap.changePeriod(10) # change period to 10 blocks
    zap.swap(token_in)
    remaining_in = token_in.balanceOf(zap)
    amount_out = token_out.balanceOf(zap) - before
    print(
        f"swap {(amount_in-remaining_in) / 10 ** token_in.decimals()} {token_in.symbol()} "
        f"for {amount_out / 10 ** token_out.decimals()} {token_out.symbol()}"
    )
    assert amount_out > 0

def test_curve_swap(whale, zap, interface, curve_token_in, token_out):
    if curve_token_in == token_out:
        pytest.skip("same token")
    if curve_token_in.balanceOf(whale) == 0:
        pytest.skip("no curve_token_in balance")

    curve_token_in.transfer(zap, curve_token_in.balanceOf(whale))
    amount_in = curve_token_in.balanceOf(zap)
    before = token_out.balanceOf(zap)
    print(f"{curve_token_in.symbol()} amount: {amount_in / 10 ** curve_token_in.decimals()}")
    zap.changePeriod(10) # change period to 10 blocks
    zap.swap(curve_token_in)
    remaining_in = curve_token_in.balanceOf(zap)
    amount_out = token_out.balanceOf(zap) - before
    print(
        f"swap {(amount_in-remaining_in) / 10 ** curve_token_in.decimals()} {curve_token_in.symbol()} "
        f"for {amount_out / 10 ** token_out.decimals()} {token_out.symbol()}"
    )
    assert amount_out > 0

