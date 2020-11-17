import pytest

tokens_in = {
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
}


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture
def zap(TreasuryZap, whale):
    return TreasuryZap.deploy({"from": whale})


@pytest.fixture(
    scope="module",
    params=tokens_in,
)
def token_out(interface, request):
    return interface.ERC20(tokens_in[request.param])


@pytest.fixture
def whale(accounts):
    return accounts.at("0x93A62dA5a14C80f265DAbC077fCEE437B1a0Efde", force=True)


@pytest.fixture
def tokens(web3, interface, whale):
    yregistry = interface.YearnRegistry(web3.ens.resolve("registry.ychad.eth"))
    tokens = [
        interface.ERC20(token, owner=whale)
        for token in yregistry.getVaultsInfo().dict()["tokenArray"]
    ]
    return [token for token in tokens if token.balanceOf(whale)]
