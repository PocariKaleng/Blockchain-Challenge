// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {EchoVault} from "./EchoVault.sol";

contract Setup {
    EchoVault public vault;

    constructor() payable {
        require(msg.value == 10 ether, "Setup needs 10 ETH");
        vault = new EchoVault{value: 10 ether}();
    }

    function isSolved() public view returns (bool) {
        return address(vault).balance < 0.1 ether;
    }
}
