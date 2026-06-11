// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

library GoddessProphecy {
    uint256 internal constant PREFIX_BITS = 20;
    uint160 internal constant PURE_SOUL_PREFIX = 0x77777;
    bytes32 public constant APPROVED_SOUL_HASH =
        0xaadc8b147468a2b680618de57f5be4f110b99f32908ecebdbfb69e26a4dc25d9;

    function isPure(address soul) internal view returns (bool) {
        bytes32 soulHash;
        assembly {
            soulHash := extcodehash(soul)
        }
        return
            soulHash == APPROVED_SOUL_HASH &&
            uint160(soul) >> (160 - PREFIX_BITS) == PURE_SOUL_PREFIX;
    }
}
