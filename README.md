## 🧠 Wallet Risk Scoring Logic

This script scores Ethereum wallets based on their **liquidity** and **shortfall** using data from the Compound V2 protocol via the `getAccountLiquidity()` function.

### 🔍 How It Works

The scoring logic relies on the Compound Comptroller contract:

```solidity
function getAccountLiquidity(address account) view returns (
    uint error,
    uint liquidity,
    uint shortfall
)
```

- `liquidity`: USD value (scaled by 1e18) the user can safely borrow.
- `shortfall`: USD value (scaled by 1e18) the user is under-collateralized by.
- `error`: 0 on success, non-zero on failure.

---

### ⚙️ Scoring Rules

| Condition                          | Score  | Explanation                                             |
|-----------------------------------|--------|---------------------------------------------------------|
| shortfall > 0                     | 1000   | 🔴 Max risk: wallet is underwater                       |
| liquidity > 0                     | 1000 - (liquidity * 100) | 🟡 Less risk with more liquidity            |
| liquidity == 0 and shortfall == 0 | 300    | ⚪ Neutral: likely inactive                              |
| error during call                 | 1000   | ❌ Failed to fetch data, treated as max risk            |

> 💡 Liquidity/Shortfall values are converted from 1e18 scale to ETH-equivalent USD.

---

### 📈 Example

- Wallet with liquidity = 3.0 ETH, shortfall = 0  
  → `score = 1000 - (3.0 * 100) = 700`

- Wallet with shortfall = 2.1 ETH  
  → `score = 1000`

- Wallet with no activity  
  → `score = 300`

