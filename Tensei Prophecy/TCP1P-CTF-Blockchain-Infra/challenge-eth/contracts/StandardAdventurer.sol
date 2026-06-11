// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract StandardAdventurer {
    function chantSpell() external view returns (uint256 relicId, uint256 powerLevel) {
        assembly {
            mstore(0x00, caller())
            mstore(0x20, 1)
            let baseSlot := keccak256(0x00, 0x40)

            relicId := sub(0, baseSlot)
            powerLevel := caller()
        }
    }

    function meetTruckKun() external {
        selfdestruct(payable(msg.sender));
    }
}
