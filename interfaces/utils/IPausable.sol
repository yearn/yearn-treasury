// SPDX-License-Identifier: MIT
pragma solidity >=0.6.8;

interface IPausable {
  event Pause(bool _paused);

  function pause(bool _paused) external;
}
