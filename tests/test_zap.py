import pytest
from conftest import tokens_in, curve_tokens_in, curve_pools_in

all_tokens_in = { **tokens_in, **curve_tokens_in } # merge both tokens

def test_swap(whale, zap, interface, token_in, token_out):
    if token_in == token_out:
        pytest.skip("same token")
    if token_in.balanceOf(whale) == 0:
        pytest.skip("no token_in balance")

    token_in.transfer(zap, token_in.balanceOf(whale))
    amount_in = token_in.balanceOf(zap)
    print(f"{token_in.symbol()} amount: {amount_in / 10 ** token_in.decimals()}")
    before = token_out.balanceOf(zap)
    zap.changePeriod(10) # change period to 1 block
    zap.swap(token_in)
    remaining_in = token_in.balanceOf(zap)
    amount_out = token_out.balanceOf(zap) - before
    print(
        f"swap {(amount_in-remaining_in) / 10 ** token_in.decimals()} {token_in.symbol()} "
        f"for {amount_out / 10 ** token_out.decimals()} {token_out.symbol()}"
    )
    # assert amount_out > 0

def test_curve_swap(whale, zap, interface, curve_token_in, token_out):
    if curve_token_in == token_out:
        pytest.skip("same token")
    if curve_token_in.balanceOf(whale) == 0:
        pytest.skip("no curve_token_in balance")

    curve_token_in.transfer(zap, curve_token_in.balanceOf(whale))
    amount_in = curve_token_in.balanceOf(zap)
    before = token_out.balanceOf(zap)
    print(f"{curve_token_in.symbol()} amount: {amount_in / 10 ** curve_token_in.decimals()}")
    zap.changePeriod(10) # change period to 1 block
    zap.swap(curve_token_in)
    amount_out = token_out.balanceOf(zap) - before
    print(
        f"swap {amount_in / 10 ** curve_token_in.decimals()} {curve_token_in.symbol()} "
        f"for {amount_out / 10 ** token_out.decimals()} {token_out.symbol()}"
    )
    # assert amount_out > 0


def test_slippage(whale, zap, interface, governance_swaps):
    for name in curve_tokens_in:
        curve_token_in = interface.ERC20(curve_tokens_in[name], owner=whale)
        zap.addCurveToken(curve_token_in, curve_pools_in[name])
    for name in tokens_in:
        token_in = interface.ERC20(tokens_in[name], owner=whale)
        zap.addToken(token_in)

    yfi = interface.ERC20("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")
    usdc = interface.ERC20("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    weth = interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    uniswap = interface.Uniswap("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
    amount0 = yfi.balanceOf(whale)
    price0 = uniswap.getAmountsOut("1 ether", [yfi, weth, usdc])[-1] / 1e6
    print(f"price {price0}")
    for name in all_tokens_in:
        token_in = interface.ERC20(all_tokens_in[name], owner=whale)
        # governance_swaps.setPairDefaults()
        if token_in.balanceOf(whale) == 0:
            continue
        # amount_in = token_in.balanceOf(whale)
        # token_in.approve(zap, amount_in)
        zap.swap(token_in)

    price = uniswap.getAmountsOut("1 ether", [yfi, weth, usdc])[-1] / 1e6
    print(f"price {price}")
    print(f"obtained {(yfi.balanceOf(whale) - amount0) / 1e18} {yfi.symbol()}")
    print(f"slippage {price / price0 - 1:+.2%}")
    assert price / price0 - 1 <= 0.2, "max acceptable slippage is 20%"
