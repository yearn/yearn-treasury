def test_liquidate(adapter, yfi, accounts, tokens):
    treasury = accounts.at("0x93A62dA5a14C80f265DAbC077fCEE437B1a0Efde", force=True)

    for token in tokens:
        if token.balanceOf(treasury) == 0:
            continue
        token.transfer(adapter, token.balanceOf(treasury), {"from": treasury})

    before = yfi.balanceOf(adapter)
    for token in tokens:
        if token.balanceOf(adapter) == 0:
            continue
        print(
            "swap", token.balanceOf(adapter) / 10 ** token.decimals(), token.symbol()
        )
        tx = adapter.swap(token, yfi, token.balanceOf(adapter))
        print("recv", tx.return_value / 10 ** yfi.decimals(), yfi.symbol())

    after = yfi.balanceOf(adapter)
    print("total", (after - before) / 10 ** yfi.decimals(), yfi.symbol())
