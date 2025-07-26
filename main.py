import pandas as pd
from web3 import Web3

# === Web3 Connection using your Alchemy Mainnet URL ===
ALCHEMY_URL = "https://eth-mainnet.g.alchemy.com/v2/ZtIBFQgjXMg0JooaN4Yx6ABCjpaVyBsL"
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

# === Compound Comptroller Contract ===
COMPTROLLER_ADDRESS = "0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b"
COMPTROLLER_ABI = [
    {
        "name": "getAccountLiquidity",
        "type": "function",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [
            {"name": "error", "type": "uint"},
            {"name": "liquidity", "type": "uint"},
            {"name": "shortfall", "type": "uint"}
        ],
        "stateMutability": "view"
    }
]

# === Contract Instance ===
comptroller = w3.eth.contract(
    address=w3.to_checksum_address(COMPTROLLER_ADDRESS),
    abi=COMPTROLLER_ABI
)

# === Scoring Logic ===
def score_wallet(wallet_address):
    try:
        wallet = w3.to_checksum_address(wallet_address)
        error, liquidity, shortfall = comptroller.functions.getAccountLiquidity(wallet).call()

        if error != 0:
            print(f"[⚠️ Error] Could not fetch data for {wallet_address} (error code {error})")
            return 1000

        liquidity_eth = liquidity / 1e18
        shortfall_eth = shortfall / 1e18

        if shortfall_eth > 0:
            return 1000  # Max risk for being underwater
        elif liquidity_eth > 0:
            score = max(0, 1000 - int(liquidity_eth * 100))  # Inverse score
            return min(score, 1000)
        else:
            return 300  # Inactive or no current borrow

    except Exception as e:
        print(f"[❌ Failed] Wallet {wallet_address}: {e}")
        return 1000  # Default to max risk if call fails

# === Main Function ===
def main():
    input_file = "full_wallet_scores.csv"
    output_file = "wallet_scores_output.csv"

    try:
        df = pd.read_csv(input_file)
        if 'wallet_id' not in df.columns:
            raise ValueError("CSV must contain a 'wallet_id' column.")

        print(f"🔍 Scoring {len(df)} wallets...\n")
        df["score"] = df["wallet_id"].apply(score_wallet)

        df.to_csv(output_file, index=False)
        print(f"\n✅ Done! Scores saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
