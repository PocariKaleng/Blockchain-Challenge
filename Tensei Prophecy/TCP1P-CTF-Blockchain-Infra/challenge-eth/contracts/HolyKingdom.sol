// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "./GoddessProphecy.sol";

contract HolyKingdom {
    address public trueHero;

    struct Relic {
        uint256 powerLevel;
        uint256 usesLeft;
    }

    mapping(address => mapping(uint256 => Relic)) public labyrinth;
    mapping(address => address) public guildRegistry;
    mapping(address => uint256) public guildBlock;

    event HolyLight(bytes32 purificationHash);

    constructor() {
        trueHero = msg.sender;
    }

    function registerAtGuild(address soul) external {
        require(GoddessProphecy.isPure(soul), "Impure soul or weak aura!");
        guildRegistry[msg.sender] = soul;
        guildBlock[msg.sender] = block.number;
    }

    function castGrandMagic() external {
        address soul = guildRegistry[msg.sender];
        require(soul != address(0), "Not registered");
        require(guildBlock[msg.sender] < block.number, "Let the prophecy settle");

        (bool success, bytes memory spell) = soul.delegatecall(
            abi.encodeWithSignature("chantSpell()")
        );
        require(success, "Magic failed!");
        require(spell.length == 64, "Weak chant!");

        (uint256 relicId, uint256 powerLevel) = abi.decode(
            spell,
            (uint256, uint256)
        );

        emit HolyLight(
            keccak256(abi.encodePacked(msg.sender, block.timestamp))
        );

        assembly {
            mstore(0x00, caller())
            mstore(0x20, 1)
            let baseSlot := keccak256(0x00, 0x40)

            sstore(add(baseSlot, relicId), powerLevel)
        }
    }
}
