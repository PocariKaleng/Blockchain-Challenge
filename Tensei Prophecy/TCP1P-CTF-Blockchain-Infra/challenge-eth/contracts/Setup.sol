// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./HolyKingdom.sol";

contract Setup {
    address public immutable PLAYER;
    HolyKingdom public immutable TARGET;

    constructor(address player) {
        PLAYER = player;
        TARGET = new HolyKingdom();
    }

    function isSolved() external view returns (bool) {
        return TARGET.trueHero() == PLAYER;
    }
}
