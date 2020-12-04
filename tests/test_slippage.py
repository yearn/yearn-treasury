import pytest
from conftest import tokens_in, curve_tokens_in, curve_pools_in

all_tokens_in = { **tokens_in, **curve_tokens_in } # merge both tokens

def test_slippage(whale, zap, sushiswap_handler, interface, governance_swaps):
    token_out = yfi = interface.ERC20("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")
    usdc = interface.ERC20("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    weth = interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    uniswap = interface.Uniswap("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
    price0 = uniswap.getAmountsOut("1 ether", [yfi, weth, usdc])[-1] / 1e6
    print(f"price {price0}")

    for name in curve_tokens_in:
        curve_token_in = interface.ERC20(curve_tokens_in[name], owner=whale)
        zap.addCurveToken(curve_token_in, curve_pools_in[name])
    for name in tokens_in:
        token_in = interface.ERC20(tokens_in[name], owner=whale)
        if token_in == token_out:
            continue
        zap.addToken(token_in)
        # setup governance swap default path
        path = [token_in, token_out] if token_in == weth else [token_in, weth, token_out]
        defaultSwapData = sushiswap_handler.customSwapData(0, 0, path, whale, 0)
        governance_swaps.setPairDefaults(token_in, token_out, sushiswap_handler.dex(), defaultSwapData)

    zap.changePeriod(10) # change period to 10 blocks (swaps only 10% of the rewards)

    for name in all_tokens_in:
        token_in = interface.ERC20(all_tokens_in[name], owner=whale)
        if token_in.balanceOf(whale) == 0:
            continue
        if token_in == token_out:
            continue
        token_in.transfer(zap, token_in.balanceOf(whale))
        zap.swap(token_in)

    price = uniswap.getAmountsOut("1 ether", [yfi, weth, usdc])[-1] / 1e6
    print(f"price {price}")
    print(f"obtained {yfi.balanceOf(zap) / 1e18} {yfi.symbol()}")
    print(f"slippage {price / price0 - 1:+.2%}")
    assert price / price0 - 1 <= 0.2, "max acceptable slippage is 20%"

