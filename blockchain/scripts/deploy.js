const hre = require("hardhat");

async function main() {
  console.log("Deploying BanKa contracts to BNB Chain Testnet...");

  // Get the ContractFactory and Signers here.
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy EventFactory
  const EventFactory = await hre.ethers.getContractFactory("EventFactory");
  const eventFactory = await EventFactory.deploy();

  await eventFactory.deployed();

  console.log("EventFactory deployed to:", eventFactory.address);

  // Verify the contract (optional, for testnet)
  if (hre.network.name !== "hardhat") {
    console.log("Waiting for block confirmations...");
    await eventFactory.deployTransaction.wait(6);
    
    try {
      await hre.run("verify:verify", {
        address: eventFactory.address,
        constructorArguments: [],
      });
    } catch (error) {
      console.log("Verification failed:", error.message);
    }
  }

  return {
    eventFactory: eventFactory.address
  };
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then((addresses) => {
    console.log("Deployment successful!");
    console.log("Contract addresses:", addresses);
    process.exit(0);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });