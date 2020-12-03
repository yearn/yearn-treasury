// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.6.8;

import "./IDexHandler.sol";
interface IUniswapDexHandler is IDexHandler {
    function customSwapData(
        uint256 _amount,
        uint256 _min,
        address[] memory _path,
        address _to,
        uint256 _expire
    ) external pure returns (bytes memory);
}
