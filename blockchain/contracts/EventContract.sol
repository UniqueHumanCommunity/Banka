// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract EventContract is ReentrancyGuard, Ownable {
    string public eventName;
    uint256 public eventDate;
    bool public isActive;
    
    struct EventToken {
        string name;
        uint256 priceInCents; // Price in cents (USD cents)
        address tokenAddress;
        uint256 totalSupply;
        uint256 totalSold;
    }
    
    mapping(address => EventToken) public eventTokens;
    mapping(address => mapping(address => uint256)) public userTokenBalances; // user => token => balance
    mapping(address => bool) public authorizedVendors;
    
    address[] public tokenAddresses;
    
    event TokenCreated(address indexed tokenAddress, string name, uint256 priceInCents);
    event TokensPurchased(address indexed buyer, address indexed tokenAddress, uint256 amount, uint256 totalCost);
    event TokensTransferred(address indexed from, address indexed to, address indexed tokenAddress, uint256 amount);
    event TokensRedeemed(address indexed user, address indexed tokenAddress, uint256 amount, uint256 refundAmount);
    event VendorAuthorized(address indexed vendor);
    
    constructor(
        string memory _eventName,
        uint256 _eventDate,
        address _owner
    ) {
        eventName = _eventName;
        eventDate = _eventDate;
        isActive = true;
        _transferOwnership(_owner);
    }
    
    // Create a new token type for this event
    function createToken(
        string memory _name,
        uint256 _priceInCents,
        uint256 _initialSupply
    ) external onlyOwner {
        // Create new ERC20 token for this event
        EventTokenERC20 newToken = new EventTokenERC20(_name, _name, _initialSupply, address(this));
        address tokenAddress = address(newToken);
        
        eventTokens[tokenAddress] = EventToken({
            name: _name,
            priceInCents: _priceInCents,
            tokenAddress: tokenAddress,
            totalSupply: _initialSupply,
            totalSold: 0
        });
        
        tokenAddresses.push(tokenAddress);
        
        emit TokenCreated(tokenAddress, _name, _priceInCents);
    }
    
    // Users purchase tokens with BNB (simulating stablecoin for MVP)
    function purchaseTokens(address _tokenAddress, uint256 _amount) external payable nonReentrant {
        require(isActive, "Event is not active");
        require(eventTokens[_tokenAddress].tokenAddress != address(0), "Token does not exist");
        require(_amount > 0, "Amount must be greater than 0");
        
        EventToken storage token = eventTokens[_tokenAddress];
        require(token.totalSold + _amount <= token.totalSupply, "Not enough tokens available");
        
        // Calculate cost in wei (for MVP, we'll use a simple conversion)
        uint256 costInWei = (token.priceInCents * _amount * 1e18) / 100; // Simple conversion for testing
        require(msg.value >= costInWei, "Insufficient payment");
        
        // Update balances
        userTokenBalances[msg.sender][_tokenAddress] += _amount;
        token.totalSold += _amount;
        
        // Refund excess payment
        if (msg.value > costInWei) {
            payable(msg.sender).transfer(msg.value - costInWei);
        }
        
        emit TokensPurchased(msg.sender, _tokenAddress, _amount, costInWei);
    }
    
    // Transfer tokens to vendor (payment)
    function transferTokens(
        address _to,
        address _tokenAddress,
        uint256 _amount
    ) external nonReentrant {
        require(isActive, "Event is not active");
        require(userTokenBalances[msg.sender][_tokenAddress] >= _amount, "Insufficient token balance");
        require(_amount > 0, "Amount must be greater than 0");
        
        userTokenBalances[msg.sender][_tokenAddress] -= _amount;
        userTokenBalances[_to][_tokenAddress] += _amount;
        
        emit TokensTransferred(msg.sender, _to, _tokenAddress, _amount);
    }
    
    // Redeem tokens for refund
    function redeemTokens(address _tokenAddress, uint256 _amount) external nonReentrant {
        require(userTokenBalances[msg.sender][_tokenAddress] >= _amount, "Insufficient token balance");
        require(_amount > 0, "Amount must be greater than 0");
        
        EventToken storage token = eventTokens[_tokenAddress];
        uint256 refundAmount = (token.priceInCents * _amount * 1e18) / 100;
        
        require(address(this).balance >= refundAmount, "Insufficient contract balance for refund");
        
        userTokenBalances[msg.sender][_tokenAddress] -= _amount;
        token.totalSold -= _amount;
        
        payable(msg.sender).transfer(refundAmount);
        
        emit TokensRedeemed(msg.sender, _tokenAddress, _amount, refundAmount);
    }
    
    // Authorize vendor
    function authorizeVendor(address _vendor) external onlyOwner {
        authorizedVendors[_vendor] = true;
        emit VendorAuthorized(_vendor);
    }
    
    // Get user token balance
    function getUserTokenBalance(address _user, address _tokenAddress) external view returns (uint256) {
        return userTokenBalances[_user][_tokenAddress];
    }
    
    // Get all token addresses
    function getTokenAddresses() external view returns (address[] memory) {
        return tokenAddresses;
    }
    
    // Get token info
    function getTokenInfo(address _tokenAddress) external view returns (EventToken memory) {
        return eventTokens[_tokenAddress];
    }
    
    // Owner can withdraw funds
    function withdrawFunds() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    // Emergency stop
    function emergencyStop() external onlyOwner {
        isActive = false;
    }
    
    // Restart event
    function restartEvent() external onlyOwner {
        isActive = true;
    }
}

// Simple ERC20 token for events
contract EventTokenERC20 is ERC20 {
    address public eventContract;
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        address _eventContract
    ) ERC20(name, symbol) {
        eventContract = _eventContract;
        _mint(_eventContract, initialSupply);
    }
}