// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./TimeVariantCasino.sol";

contract Setup {
    TimeVariantCasino public casino;

    event TargetDeployed(address targetAddress);

    constructor() payable {
        uint256 initialSeed = uint256(
            keccak256(
                abi.encodePacked(
                    blockhash(block.number - 1),
                    block.coinbase,
                    msg.sender
                )
            )
        );

        casino = new TimeVariantCasino(initialSeed);

        emit TargetDeployed(address(casino));
    }

    function isSolved() external view returns (bool) {
        return casino.isSolved();
    }
}
