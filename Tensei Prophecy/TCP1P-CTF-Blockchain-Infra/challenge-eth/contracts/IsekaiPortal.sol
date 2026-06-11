// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./HolyKingdom.sol";

contract IsekaiPortal {
    HolyKingdom public immutable kingdom;

    constructor() {
        kingdom = new HolyKingdom();
    }

    function isConquered() external view returns (bool) {
        return kingdom.trueHero() == msg.sender;
    }
}
