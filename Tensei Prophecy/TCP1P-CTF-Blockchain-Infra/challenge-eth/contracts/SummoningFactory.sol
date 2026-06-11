// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./StandardAdventurer.sol";

contract SummoningFactory {
    event Summoned(address indexed soul, bytes32 indexed salt);

    function summon(bytes32 salt) external returns (address soul) {
        soul = address(new StandardAdventurer{salt: salt}());
        emit Summoned(soul, salt);
    }

    function compute(bytes32 salt) external view returns (address) {
        bytes32 digest = keccak256(
            abi.encodePacked(
                bytes1(0xff),
                address(this),
                salt,
                keccak256(type(StandardAdventurer).creationCode)
            )
        );
        return address(uint160(uint256(digest)));
    }
}
