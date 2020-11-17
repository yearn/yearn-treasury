import pytest


def test_swap(whale, zap, token_out, token_in):
    if token_in == token_out:
        pytest.skip("same token")

    if token_in.balanceOf(whale) == 0:
        pytest.skip("no token_in balance")

    before = token_out.balanceOf(whale)
    token_in.approve(zap, token_in.balanceOf(whale))
    amount_in = token_in.balanceOf(whale)
    zap.swap(token_in, token_out, amount_in)
    amount_out = token_out.balanceOf(whale) - before
    print(
        f"swap {amount_in / 10 ** token_in.decimals()} {token_in.symbol()} "
        f"for {amount_out / 10 ** token_out.decimals()} {token_out.symbol()}"
    )
    assert amount_out > 0
