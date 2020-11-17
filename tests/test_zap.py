def test_swap(whale, zap, token_out, tokens):
    before = token_out.balanceOf(whale)
    for token_in in tokens:
        token_in.approve(zap, token_in.balanceOf(whale))
        amount_in = token_in.balanceOf(whale)
        tx = zap.swap(token_in, token_out, amount_in)
        print(
            f"swap {amount_in / 10 ** token_in.decimals()} {token_in.symbol()} "
            f"for {tx.return_value / 10 ** token_out.decimals()} {token_out.symbol()}"
        )

    after = token_out.balanceOf(whale)
    print(f"total {(after - before) / 10 ** token_out.decimals()} {token_out.symbol()}")
