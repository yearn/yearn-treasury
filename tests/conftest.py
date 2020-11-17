import pytest


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture
def adapter(TreasuryAdapter, accounts):
    return TreasuryAdapter.deploy({"from": accounts[0]})


@pytest.fixture
def yfi(interface):
    return interface.ERC20("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")


@pytest.fixture
def tokens(web3, interface):
    yregistry = interface.YearnRegistry(web3.ens.resolve("registry.ychad.eth"))
    return [
        interface.ERC20(token)
        for token in yregistry.getVaultsInfo().dict()["tokenArray"]
    ]
