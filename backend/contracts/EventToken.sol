// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract EventToken is IERC20 {
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    uint256 private _totalSupply;
    string public name;
    string public symbol;
    uint8 public decimals;
    
    address public owner;
    address public eventContract;
    string public eventName;
    uint256 public priceInCents;
    bool public isPaused;
    
    event Paused();
    event Unpaused();
    event TokenMetadataUpdated(string name, string symbol);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier whenNotPaused() {
        require(!isPaused, "Token transfers are paused");
        _;
    }
    
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _totalSupply,
        uint8 _decimals,
        address _owner,
        string memory _eventName,
        uint256 _priceInCents
    ) {
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        _totalSupply = _totalSupply * 10**_decimals;
        eventName = _eventName;
        priceInCents = _priceInCents;
        owner = _owner;
        isPaused = false;
        
        // Mint all tokens to the owner (event organizer)
        _balances[_owner] = _totalSupply;
        emit Transfer(address(0), _owner, _totalSupply);
    }
    
    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }
    
    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }
    
    function transfer(address recipient, uint256 amount) public override whenNotPaused returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }
    
    function allowance(address tokenOwner, address spender) public view override returns (uint256) {
        return _allowances[tokenOwner][spender];
    }
    
    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address sender, address recipient, uint256 amount) public override whenNotPaused returns (bool) {
        uint256 currentAllowance = _allowances[sender][msg.sender];
        require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
        
        _transfer(sender, recipient, amount);
        _approve(sender, msg.sender, currentAllowance - amount);
        
        return true;
    }
    
    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(sender != address(0), "ERC20: transfer from the zero address");
        require(recipient != address(0), "ERC20: transfer to the zero address");
        require(_balances[sender] >= amount, "ERC20: transfer amount exceeds balance");
        
        _balances[sender] -= amount;
        _balances[recipient] += amount;
        emit Transfer(sender, recipient, amount);
    }
    
    function _approve(address tokenOwner, address spender, uint256 amount) internal {
        require(tokenOwner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");
        
        _allowances[tokenOwner][spender] = amount;
        emit Approval(tokenOwner, spender, amount);
    }
    
    // Owner functions
    function pause() public onlyOwner {
        isPaused = true;
        emit Paused();
    }
    
    function unpause() public onlyOwner {
        isPaused = false;
        emit Unpaused();
    }
    
    function updateMetadata(string memory _name, string memory _symbol) public onlyOwner {
        name = _name;
        symbol = _symbol;
        emit TokenMetadataUpdated(_name, _symbol);
    }
    
    function mint(address to, uint256 amount) public onlyOwner {
        require(to != address(0), "ERC20: mint to the zero address");
        
        _totalSupply += amount;
        _balances[to] += amount;
        emit Transfer(address(0), to, amount);
    }
    
    function burn(uint256 amount) public {
        require(_balances[msg.sender] >= amount, "ERC20: burn amount exceeds balance");
        
        _balances[msg.sender] -= amount;
        _totalSupply -= amount;
        emit Transfer(msg.sender, address(0), amount);
    }
    
    // Utility functions for frontend integration
    function getTokenInfo() public view returns (
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _totalSupply,
        string memory _eventName,
        uint256 _priceInCents,
        address _owner,
        bool _isPaused
    ) {
        return (name, symbol, decimals, _totalSupply, eventName, priceInCents, owner, isPaused);
    }
}