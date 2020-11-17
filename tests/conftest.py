import pytest


tokens_in = {
    "aLINK": "0xA64BD6C70Cb9051F6A9ba1F163Fdc07E0DfB5F84",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "yDAI+yUSDC+yUSDT+yTUSD": "0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8",
    "TUSD": "0x0000000000085d4780B73119b644AE5ecd22b376",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "yDAI+yUSDC+yUSDT+yBUSD": "0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B",
    "crvRenWSBTC": "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "3Crv": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
    "GUSD": "0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd",
    "cDAI+cUSDC": "0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2",
}


tokens_out = {
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
}


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture
def whale(accounts):
    return accounts.at("0x93A62dA5a14C80f265DAbC077fCEE437B1a0Efde", force=True)


@pytest.fixture
def zap(TreasuryZap, whale):
    return TreasuryZap.deploy({"from": whale})


@pytest.fixture(params=tokens_in)
def token_in(interface, request, whale):
    return interface.ERC20(tokens_in[request.param], owner=whale)


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
