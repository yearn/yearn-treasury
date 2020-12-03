pragma solidity=0.6.12;

interface CurveRegistry {
    function get_pool_from_lp_token(address) external view returns (address);
}
