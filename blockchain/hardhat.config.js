require("@nomicfoundation/hardhat-ethers");

const MNEMONIC = "flee cluster north scissors random attitude mutual strategy excuse debris consider uniform";
const BNB_TESTNET_URL = "https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    bnbTestnet: {
      url: BNB_TESTNET_URL,
      accounts: {
        mnemonic: MNEMONIC,
        path: "m/44'/60'/0'/0",
        initialIndex: 0,
        count: 10
      },
      chainId: 97,
      gasPrice: 20000000000,
      gas: 8000000
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};