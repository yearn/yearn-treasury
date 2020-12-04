// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.6.8;

import "@openzeppelinV3/contracts/math/SafeMath.sol";
import "@openzeppelinV3/contracts/token/ERC20/IERC20.sol";
import '@openzeppelinV3/contracts/token/ERC20/SafeERC20.sol';

import "../../interfaces/dex-handlers/IDexHandler.sol";
import "../../interfaces/swap/IGovernanceSwap.sol";
import "../utils/TransferHelper.sol";

/*
 * SafeSmartSwapAbstract
 */
abstract
contract SafeSmartSwap {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    IGovernanceSwap public governanceSwap;

    constructor(address _governanceSwap) public {
        _setGovernanceSwap(_governanceSwap);
    }

    // Setter
    function _setGovernanceSwap(address _governanceSwap) internal {
        governanceSwap = IGovernanceSwap(_governanceSwap);
        require(governanceSwap.isGovernanceSwap(), 'safe-smart-swap::set-governance-swap:is-not-governance-swap');
    }

    // Governance swap
    function _swap(uint256 _amount, address _in, address _out) internal returns (uint _amountOut) {
        address _handler = governanceSwap.getPairDefaultDexHandler(_in, _out);
        require(_handler != address(0), 'no-default-handler');
        bytes memory _data = governanceSwap.getPairDefaultData(_in, _out);

        _approve(_in, _handler, _amount);
        return IDexHandler(_handler).swap(_data, _amount);

    }

    // Custom swap
    function _swap(uint256 _amount, address _in, address _out, address _dex, bytes memory _data) internal returns (uint _amountOut) {
        // Use default swap if no custom dex and data was used
        if (_dex == address(0) && _data.length == 0) {
            return _swap(_amount, _in, _out);
        }

        uint256 inBalancePreSwap = IERC20(_in).balanceOf(address(this));
        uint256 outBalancePreSwap = IERC20(_out).balanceOf(address(this));

        // Get governanceSwap amount for token pair
        address _defaultHandler = governanceSwap.getPairDefaultDexHandler(_in, _out);
        bytes memory _defaultData = governanceSwap.getPairDefaultData(_in, _out);
        uint256 _governanceAmountOut = IDexHandler(_defaultHandler).getAmountOut(_defaultData, _amount);

        address _handler = governanceSwap.getDexHandler(_dex);
        require(_handler != address(0), 'no-handler-for-dex');
        
        _approve(_in, _handler, _amount);

        _amountOut = IDexHandler(_handler).swap(_data, _amount);

        require(_amountOut >= _governanceAmountOut, 'custom-swap-is-suboptimal');
        // TODO Check gas spendage if _amountOut == _governanceAmountOut to avoid gas mining? (overkill) [need this check for keep3r ]

        uint256 inBalancePostSwap = IERC20(_in).balanceOf(address(this));
        uint256 outBalancePostSwap = IERC20(_out).balanceOf(address(this));

        // Extra checks to avoid custom dex+data exploits
        require(inBalancePostSwap >= inBalancePreSwap.sub(_amount), 'in-balance-mismatch');
        require(outBalancePostSwap >= outBalancePreSwap.add(_governanceAmountOut), 'out-balance-mismatch');
    }

    function _approve(address _in, address _handler, uint256 _amount) internal {
        TransferHelper.safeApprove(_in, _handler, 0);
        TransferHelper.safeApprove(_in, _handler, _amount);
    }

}
