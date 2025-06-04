const { Web3 } = require('web3');
const fs = require('fs');
const path = require('path');

// Configuration
const MNEMONIC = "flee cluster north scissors random attitude mutual strategy excuse debris consider uniform";
const BNB_TESTNET_URL = "https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5";

async function deployContracts() {
    console.log("🚀 Iniciando deploy dos contratos BanKa na BNB Chain Testnet...");
    
    // Initialize Web3
    const HDWalletProvider = require('@truffle/hdwallet-provider');
    const provider = new HDWalletProvider(MNEMONIC, BNB_TESTNET_URL);
    const web3 = new Web3(provider);
    
    const accounts = await web3.eth.getAccounts();
    const deployer = accounts[0];
    
    console.log("📋 Deployer account:", deployer);
    
    const balance = await web3.eth.getBalance(deployer);
    console.log("💰 Balance:", web3.utils.fromWei(balance, 'ether'), "BNB");
    
    // Load contract artifacts
    const eventFactoryArtifact = JSON.parse(fs.readFileSync(path.join(__dirname, '../artifacts/contracts/EventFactory.sol/EventFactory.json')));
    
    // Deploy EventFactory
    console.log("📄 Deploying EventFactory...");
    
    const EventFactory = new web3.eth.Contract(eventFactoryArtifact.abi);
    
    const eventFactoryDeploy = EventFactory.deploy({
        data: eventFactoryArtifact.bytecode
    });
    
    const gas = await eventFactoryDeploy.estimateGas({ from: deployer });
    console.log("⛽ Estimated gas:", gas);
    
    const eventFactory = await eventFactoryDeploy.send({
        from: deployer,
        gas: Math.round(gas * 1.2), // Add 20% buffer
        gasPrice: '20000000000' // 20 gwei
    });
    
    console.log("✅ EventFactory deployed at:", eventFactory.options.address);
    
    // Verify deployment
    const code = await web3.eth.getCode(eventFactory.options.address);
    if (code === '0x') {
        throw new Error("Contract deployment failed - no code at address");
    }
    
    console.log("🔗 BSCScan Testnet:", `https://testnet.bscscan.com/address/${eventFactory.options.address}`);
    
    // Save deployment info
    const deploymentInfo = {
        network: "BNB Chain Testnet",
        chainId: 97,
        deployer: deployer,
        contracts: {
            EventFactory: {
                address: eventFactory.options.address,
                abi: eventFactoryArtifact.abi
            }
        },
        deployedAt: new Date().toISOString(),
        bscscanUrl: `https://testnet.bscscan.com/address/${eventFactory.options.address}`
    };
    
    fs.writeFileSync(
        path.join(__dirname, '../deployment.json'), 
        JSON.stringify(deploymentInfo, null, 2)
    );
    
    console.log("💾 Deployment info saved to deployment.json");
    
    provider.engine.stop();
    
    return {
        eventFactory: eventFactory.options.address
    };
}

// Run deployment
deployContracts()
    .then((addresses) => {
        console.log("🎉 Deployment successful!");
        console.log("📋 Contract addresses:", addresses);
        process.exit(0);
    })
    .catch((error) => {
        console.error("❌ Deployment failed:", error);
        process.exit(1);
    });