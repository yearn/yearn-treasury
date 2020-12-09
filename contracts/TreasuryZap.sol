// SPDX-License-Identifier: AGPL
pragma solidity=0.6.12;

import "@openzeppelinV3/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV3/contracts/math/SafeMath.sol";
import "@openzeppelinV3/contracts/utils/Address.sol";
import "@openzeppelinV3/contracts/token/ERC20/SafeERC20.sol";
import '@openzeppelinV3/contracts/utils/EnumerableSet.sol';

import "../interfaces/utils/IZapper.sol";
import "../interfaces/curve/ICurveRegistry.sol";

import "./utils/UtilsReady.sol";
import "./swap/SafeSmartSwapAbstract.sol";

contract TreasuryZap is UtilsReady, SafeSmartSwap {
    using Address for address;
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // strategy constants
    address constant want = 0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e; // YFI

    // curve utils
    address constant curve_registry = 0x7D86446dDb609eD0F5f8684AcF30380a356b2B4c;
    address constant curve_zap_out = 0xA3061Cf6aC1423c6F40917AD49602cBA187181Dc;
    mapping(address => address) curve_deposit;

    // keeper utils
    EnumerableSet.AddressSet internal enabledKeepers;

    // swap variables
    uint256 public period = 6500 * 7; // 1 week
    mapping(address => uint256) public lastSwapAt;


    constructor(address _governanceSwap) public UtilsReady() SafeSmartSwap(_governanceSwap) {
        addKeeper(msg.sender);
    }

    // Curve Tokens
    function addCurveToken(address _token, address _curveContract) public onlyGovernor {
        require(_token != address(0));
        require(_curveContract != address(0));
        require(curve_deposit[_token] == address(0), 'TreasuryZap::addCurveToken:token-already-added');
        curve_deposit[_token] = _curveContract;
        _addProtocolToken(_token);
    }
    function editCurveToken(address _token, address _curveContract) external onlyGovernor {
        require(_token != address(0));
        require(_curveContract != address(0));
        require(curve_deposit[_token] != address(0), 'TreasuryZap::editCurveToken:token-not-added');
        curve_deposit[_token] = _curveContract;
    }

    // Non-Curve Tokens
    function addToken(address _token) external onlyGovernor {
        require(_token != address(0), 'token-not-0');
        address _curvePool = ICurveRegistry(curve_registry).get_pool_from_lp_token(_token);
        if (_curvePool != address(0)) {
            return addCurveToken(_token, _curvePool);
        }
        _addProtocolToken(_token);
    }

    function changePeriod(uint256 _period) external onlyGovernor {
        require(_period > 0, 'period-not-0');
        period = _period;
    }


    // keeper helpers
    function addKeeper(address _keeper) public onlyGovernor {
        require(!enabledKeepers.contains(_keeper), 'TreasuryZap::addKeeper:keeper-already-added');
        enabledKeepers.add(_keeper);
    }
    function removeKeeper(address _keeper) external onlyGovernor {
        require(enabledKeepers.contains(_keeper), 'TreasuryZap::removeKeeper:keeper-not-added');
        enabledKeepers.remove(_keeper);
    }
    modifier onlyKeeper {
        require(enabledKeepers.contains(msg.sender), 'TreasuryZap::onlyKeeper:sender-not-enabled-keeper');
        _;
    }

    // view functions
    function getSpendage(address _token) public view returns (uint256 _amount) {
        require(protocolTokens.contains(_token), 'TreasuryZap::getSpendage:token-not-in-protocol');
        uint256 balance = IERC20(_token).balanceOf(address(this));
        uint256 blocks = block.number.sub(lastSwapAt[_token]);
        require(blocks > 0, 'TreasuryZap::getSpendage:already-swapped-this-block');
        if (blocks >= period) {
            blocks = 1;
        }
        return balance.mul(blocks).div(period);
    }


    // Swaps
    function swap(address _token) external notPaused onlyKeeper returns (uint256 _amountOut) {
        uint256 _amount = getSpendage(_token);
        if (curve_deposit[_token] != address(0)) {
            _amountOut = _curveSwap(_amount, _token, want);
        } else {
            _amountOut = _swap(_amount, _token, want);
        }
        _reportSwap(_token, _amount, _amountOut);
    }

    function customSwap(address _token, address _dex, bytes calldata _data) external notPaused onlyKeeper returns (uint256 _amountOut) {
        uint256 _amount = getSpendage(_token);
        _amountOut = _swap(_amount, _token, want, _dex, _data);
        _reportSwap(_token, _amount, _amountOut);
    }


    function _curveSwap(uint256 _amount, address _token, address want) internal returns (uint256 _amountOut) {
        // IERC20(_token).safeApprove(curve_zap_out, 0);
        IERC20(_token).safeApprove(curve_zap_out, _amount);
        // Why is this required? (we sould add any extra curve token to avoid having it treated as dust)
        // pool = CurveRegistry(curve_registry).get_pool_from_lp_token(_token);
        address _curvePool = curve_deposit[_token];
        _amountOut = Zapper(curve_zap_out).ZapOut(
            payable(address(this)),
            _curvePool,
            _amount,
            want,
            0
        );
    }

    function _reportSwap(address _token, uint256 _amount, uint256 _amountOut) internal {
        lastSwapAt[_token] = block.number;
        // TODO Report swap with event
    }

}
