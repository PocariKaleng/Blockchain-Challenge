// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract EchoVault {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public echoes;
    mapping(address => bool) public joined;

    uint256 public constant JOIN_FEE = 1 ether;
    uint256 public constant MAX_ECHO = 0.5 ether;

    constructor() payable {}

    function join() external payable {
        require(msg.value == JOIN_FEE, "Need exactly 1 ETH");
        require(!joined[msg.sender], "Already joined");

        joined[msg.sender] = true;
        balances[msg.sender] = msg.value;
        echoes[msg.sender] = 3;
    }

    function echo() external {
        require(joined[msg.sender], "Not joined");
        require(echoes[msg.sender] > 0, "No echo left");
        require(balances[msg.sender] >= MAX_ECHO, "Balance too low");

        (bool success, ) = msg.sender.call{value: MAX_ECHO}("");
        require(success, "Echo failed");

        unchecked {
            echoes[msg.sender] -= 1;
            balances[msg.sender] -= MAX_ECHO;
        }
    }

    function deposit() external payable {
        require(joined[msg.sender], "Join first");
        require(msg.value > 0, "No ETH sent");

        balances[msg.sender] += msg.value;
    }

    function getVaultBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
