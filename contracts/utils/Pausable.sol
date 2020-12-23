
// SPDX-License-Identifier: MIT

pragma solidity >=0.6.8;

import '@openzeppelinV3/contracts/utils/Address.sol';
import '@openzeppelinV3/contracts/utils/EnumerableSet.sol';
import '@openzeppelinV3/contracts/token/ERC20/IERC20.sol';

import '../../interfaces/utils/IPausable.sol';

abstract
contract Pausable is IPausable {
  bool public paused;

  constructor() public {}
  
  modifier notPaused() {
    require(!paused, 'paused');
    _;
  }

  function _pause(bool _paused) internal {
    require(paused != _paused, 'no-change');
    paused = _paused;
  }

}
