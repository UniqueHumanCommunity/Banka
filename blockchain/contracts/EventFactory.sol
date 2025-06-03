// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EventContract.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract EventFactory is Ownable {
    struct Event {
        address contractAddress;
        string eventName;
        uint256 eventDate;
        address organizer;
        bool isActive;
        uint256 createdAt;
    }
    
    mapping(address => Event[]) public organizerEvents;
    mapping(address => Event) public eventContracts;
    address[] public allEventContracts;
    
    event EventCreated(
        address indexed contractAddress,
        string eventName,
        address indexed organizer,
        uint256 eventDate
    );
    
    constructor() Ownable(msg.sender) {}
    
    // Create a new event contract
    function createEvent(
        string memory _eventName,
        uint256 _eventDate
    ) external returns (address) {
        require(bytes(_eventName).length > 0, "Event name cannot be empty");
        require(_eventDate > block.timestamp, "Event date must be in the future");
        
        // Deploy new EventContract
        EventContract newEventContract = new EventContract(
            _eventName,
            _eventDate,
            msg.sender
        );
        
        address contractAddress = address(newEventContract);
        
        // Store event information
        Event memory newEvent = Event({
            contractAddress: contractAddress,
            eventName: _eventName,
            eventDate: _eventDate,
            organizer: msg.sender,
            isActive: true,
            createdAt: block.timestamp
        });
        
        organizerEvents[msg.sender].push(newEvent);
        eventContracts[contractAddress] = newEvent;
        allEventContracts.push(contractAddress);
        
        emit EventCreated(contractAddress, _eventName, msg.sender, _eventDate);
        
        return contractAddress;
    }
    
    // Get events by organizer
    function getOrganizerEvents(address _organizer) external view returns (Event[] memory) {
        return organizerEvents[_organizer];
    }
    
    // Get event by contract address
    function getEvent(address _contractAddress) external view returns (Event memory) {
        return eventContracts[_contractAddress];
    }
    
    // Get all events
    function getAllEvents() external view returns (address[] memory) {
        return allEventContracts;
    }
    
    // Get total number of events
    function getTotalEvents() external view returns (uint256) {
        return allEventContracts.length;
    }
    
    // Check if contract is an event
    function isEventContract(address _contractAddress) external view returns (bool) {
        return eventContracts[_contractAddress].contractAddress != address(0);
    }
}