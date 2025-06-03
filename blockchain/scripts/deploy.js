const hre = require("hardhat");

async function main() {
  console.log("Deploying BanKa contracts to BNB Chain Testnet...");

  // Get the ContractFactory and Signers here.
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  // Deploy EventFactory
  const EventFactory = await hre.ethers.getContractFactory("EventFactory");
  const eventFactory = await EventFactory.deploy();

  await eventFactory.waitForDeployment();

  console.log("EventFactory deployed to:", await eventFactory.getAddress());

  // Verify the contract (optional, for testnet)
  if (hre.network.name !== "hardhat") {
    console.log("Waiting for block confirmations...");
    // Wait for a few blocks
    const receipt = await eventFactory.deploymentTransaction().wait(3);
    console.log("Contract deployed in block:", receipt.blockNumber);
  }

  return {
    eventFactory: await eventFactory.getAddress()
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