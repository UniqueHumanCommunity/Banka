require("@nomicfoundation/hardhat-toolbox");

const PRIVATE_KEY = "flee cluster north scissors random attitude mutual strategy excuse debris consider uniform";
const BNB_TESTNET_URL = "https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.19",
  networks: {
    bnbTestnet: {
      url: BNB_TESTNET_URL,
      accounts: [PRIVATE_KEY]
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};