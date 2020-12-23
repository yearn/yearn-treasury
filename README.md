# Treasury Zap

As the rewards address of v1 strategies, `TreasuryZap` receives a bunch of different tokens and it swaps them to YFI, trying to avoid slippage as much as possible by partially swappping the rewards and allowing the keepers to set custom routes via governance-swaps.


- [governance-swaps](https://github.com/lbertenasco/safe-smart-swap): [`0xCe65aab4CE2ec7C13c82437Bd57baFEB0a0791d4`](https://etherscan.io/address/0xCe65aab4CE2ec7C13c82437Bd57baFEB0a0791d4#code)

## run tests:

```sh
export WEB3_INFURA_PROJECT_ID=YourInfuraID
brownie test -v -s
```


## How it works:

- Rewards are transfered to `TreasuryZap` (can be modified to an `approve -> transferFrom` logic if needed)
- Keeper calls `TreasuryZap.swap(address _token)` or `TreasuryZap.customSwap(address _token, address _dex, bytes calldata _data)`
- `TreasuryZap` uses `getSpendage` to get the `_amount` of `_token` available to be swapped, depending on the current `block.number`, `lastSwapAt[_token]` and `period`
- `TreasuryZap` `swaps` the `_amount` of `_token` for `want` via `SafeSmartSwapAbstract` which uses `governance-swaps`
- `SafeSmartSwapAbstract` calls `governance-swaps` to get the default `dexHandler` and `data` for the `_token -> want` pair
- `SafeSmartSwapAbstract` approves `dexHandler` to spend `_amount` of  `_token`
- `SafeSmartSwapAbstract` executes `dexHandler.swap(_data, _amount)`
- `TreasuryZap` receives the `amountOut` of `want`
- `TreasuryZap` updates the `lastSwapAt[_token]` and reports the swap


## Improvements:

- fix tests (not resetting the fork)


## Contracts:

### [`TreasuryZap.sol`](./contracts/TreasuryZap.sol)

- todo:
    - add curve zap to governance-swaps
    - add tokens_in -> yfi(want) default paths to governance-swaps

Curve Tokens and Pools: (not sure why we are not using `CurveRegistry.get_pool_from_lp_token(_token)` here, are those better default pools?)
```js
curve_deposit[0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2] = 0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06; // compound
curve_deposit[0x9fC689CCaDa600B6DF723D9E47D84d76664a1F23] = 0xac795D2c97e60DF6a99ff1c814727302fD747a80; // usdt
curve_deposit[0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8] = 0xbBC81d23Ea2c3ec7e56D39296F0cbB648873a5d3; // y
curve_deposit[0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B] = 0xb6c057591E073249F2D9D88Ba59a46CFC9B59EdB; // busd
curve_deposit[0xC25a3A3b969415c80451098fa907EC722572917F] = 0xFCBa3E75865d2d561BE8D220616520c171F12851; // susdv2
curve_deposit[0xD905e2eaeBe188fc92179b6350807D8bd91Db0D8] = 0xA50cCc70b6a011CffDdf45057E39679379187287; // pax
```

Tokens in:
```js
aLINK: 0xA64BD6C70Cb9051F6A9ba1F163Fdc07E0DfB5F84
LINK: 0x514910771AF9Ca656af840dff83E8264EcF986CA
USDC: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
TUSD: 0x0000000000085d4780B73119b644AE5ecd22b376
DAI: 0x6B175474E89094C44Da98b954EedeAC495271d0F
USDT: 0xdAC17F958D2ee523a2206206994597C13D831ec7
YFI: 0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e
crvRenWSBTC: 0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3
WETH: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
3Crv: 0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490
GUSD: 0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd
``` 
