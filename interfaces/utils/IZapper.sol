pragma solidity=0.6.12;

interface Zapper {
    function ZapOut(
        address payable toWhomToIssue,
        address swapAddress,
        uint256 incomingCrv,
        address toToken,
        uint256 minToTokens
    ) external returns (uint256 ToTokensBought);
}
