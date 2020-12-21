import pytest


tokens_in = {
    "aLINK": "0xA64BD6C70Cb9051F6A9ba1F163Fdc07E0DfB5F84",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "TUSD": "0x0000000000085d4780B73119b644AE5ecd22b376",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "crvRenWSBTC": "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "3Crv": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
    "GUSD": "0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd",
}

curve_tokens_in = {
    "curve_compound": "0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2", # cDAI+cUSDC
    "curve_usdt": "0x9fC689CCaDa600B6DF723D9E47D84d76664a1F23",
    "curve_y": "0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8", # yDAI+yUSDC+yUSDT+yTUSD
    "curve_busd": "0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B", # yDAI+yUSDC+yUSDT+yBUSD
    "curve_susdv2": "0xC25a3A3b969415c80451098fa907EC722572917F",
    "curve_pax": "0xD905e2eaeBe188fc92179b6350807D8bd91Db0D8",
}
curve_pools_in = {
    "curve_compound": "0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06", # cDAI+cUSDC
    "curve_usdt": "0xac795D2c97e60DF6a99ff1c814727302fD747a80",
    "curve_y": "0xbBC81d23Ea2c3ec7e56D39296F0cbB648873a5d3", # yDAI+yUSDC+yUSDT+yTUSD
    "curve_busd": "0xb6c057591E073249F2D9D88Ba59a46CFC9B59EdB", # yDAI+yUSDC+yUSDT+yBUSD
    "curve_susdv2": "0xFCBa3E75865d2d561BE8D220616520c171F12851",
    "curve_pax": "0xA50cCc70b6a011CffDdf45057E39679379187287",
}

tokens_out = {
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    # "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F", // only swap to YFI
}



@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

@pytest.fixture
def swap_owner(accounts, web3):
    return accounts.at(web3.ens.resolve("lucho.eth"), force=True)

@pytest.fixture
def governance_swaps(interface, swap_owner):
    return interface.IGovernanceSwap("0xCe65aab4CE2ec7C13c82437Bd57baFEB0a0791d4", owner=swap_owner)

@pytest.fixture
def uniswap_handler(UniswapV2DexHandler, interface, governance_swaps, swap_owner):
    uni_handler = interface.IUniswapDexHandler("0x293aC14CB38E2443d9c95C185A25b8EA6f2f18A2", owner=swap_owner)
    uni_handler_new = UniswapV2DexHandler.deploy(uni_handler.dex(), {"from": swap_owner})
    governance_swaps.removeDexHandler(uni_handler_new.dex())
    governance_swaps.addDexHandler(uni_handler_new.dex(), uni_handler_new)
    return uni_handler_new

@pytest.fixture
def sushiswap_handler(UniswapV2DexHandler, interface, governance_swaps, swap_owner):
    sushi_handler = interface.IUniswapDexHandler("0xfB5Ab2909A455934214A7b84C802fbFBcE7c4e9F", owner=swap_owner)
    sushi_handler_new = UniswapV2DexHandler.deploy(sushi_handler.dex(), {"from": swap_owner})
    governance_swaps.removeDexHandler(sushi_handler_new.dex())
    governance_swaps.addDexHandler(sushi_handler_new.dex(), sushi_handler_new)
    return sushi_handler_new

@pytest.fixture
def whale(accounts):
    return accounts.at("0x93A62dA5a14C80f265DAbC077fCEE437B1a0Efde", force=True)

@pytest.fixture()
def weth(interface):
    return interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

@pytest.fixture
def zap(TreasuryZap, whale, governance_swaps):
    return TreasuryZap.deploy(governance_swaps, {"from": whale})


@pytest.fixture(params=tokens_in)
def token_in(interface, zap, weth, token_out, governance_swaps, sushiswap_handler, request, whale):
    token_in = interface.ERC20(tokens_in[request.param], owner=whale)
    zap.addToken(token_in)
    if token_in == token_out:
        return token_in
    # setup governance swap default path
    path = [token_in, token_out] if token_in == weth else [token_in, weth, token_out]
    defaultSwapData = sushiswap_handler.customSwapData(0, 0, path, whale, 0)
    governance_swaps.setPairDefaults(token_in, token_out, sushiswap_handler.dex(), defaultSwapData)

    return token_in

@pytest.fixture(params=curve_tokens_in)
def curve_token_in(interface, zap, weth, token_out, governance_swaps, sushiswap_handler, request, whale):
    curve_token_in = interface.ERC20(curve_tokens_in[request.param], owner=whale)
    zap.addCurveToken(curve_token_in, curve_pools_in[request.param])
    if curve_token_in == token_out:
        return curve_token_in

    return curve_token_in

@pytest.fixture(params=tokens_out)
def token_out(interface, request):
    return interface.ERC20(tokens_out[request.param])


@pytest.fixture
def tokens(web3, interface, whale):
    yregistry = interface.YearnRegistry(web3.ens.resolve("registry.ychad.eth"))
    return [
        interface.ERC20(token, owner=whale)
        for token in yregistry.getVaultsInfo().dict()["tokenArray"]
    ]
