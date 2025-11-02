# BlockStreet Auto Bot 🤖

<div align="center">

![BlockStreet Bot Banner](./assets/bot-demo.png)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/febriyan9346/BlockStreet-Auto-Bot.svg)](https://github.com/febriyan9346/BlockStreet-Auto-Bot/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/febriyan9346/BlockStreet-Auto-Bot.svg)](https://github.com/febriyan9346/BlockStreet-Auto-Bot/network)

**An automated trading bot for BlockStreet platform with advanced security features and multi-wallet support.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Security](#-security-configuration)

</div>

---

## 📸 Bot in Action

![Bot in Action](./assets/IMG_4090.jpeg)

## ✨ Features

- 🔄 **Auto Swap** - Automated token swapping with randomized amounts
- 💰 **Manual Swap** - Controlled token swapping with custom parameters
- 📈 **Supply Assets** - Automated asset supply to earning pools
- 📉 **Withdraw Assets** - Smart withdrawal management
- 💳 **Borrow Assets** - Automated borrowing operations
- 🔁 **Repay Loans** - Loan repayment automation
- 🚀 **Auto All Operations** - Complete automation with daily check-ins
- 🔐 **Security Features** - Built-in transaction limits and rate limiting
- 🌐 **Proxy Support** - Rotate through multiple proxies
- 👛 **Multi-Wallet** - Manage multiple wallets simultaneously
- ⏰ **24-Hour Automation** - Runs continuously with countdown timer
- 📊 **Real-time Logging** - Color-coded status updates

## 🛡️ Security Configuration

The bot includes comprehensive security features to protect your assets:

| Feature | Value | Description |
|---------|-------|-------------|
| **Max Transaction Amount** | 0.01 | Maximum amount per transaction |
| **Min Balance Threshold** | 0.001 | Prevents wallet drain |
| **Rate Limiting** | 100/hour | Maximum transactions per wallet |
| **Transaction Validation** | ✅ Enabled | All operations validated |

## 📋 Prerequisites

- ✅ Python 3.8 or higher
- ✅ 2Captcha API key (for solving Cloudflare Turnstile)
- ✅ Ethereum wallet private keys
- ⚙️ (Optional) Proxy servers

## 🚀 Installation

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/febriyan9346/BlockStreet-Auto-Bot.git
cd BlockStreet-Auto-Bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your files
# Edit private_keys.txt - Add your wallet private keys
# Edit 2captcha.txt - Add your 2Captcha API key
# Edit proxies.txt (optional) - Add your proxies

# 4. Run the bot
python bot.py
```

### Detailed Setup

**1. Clone the repository**
```bash
git clone https://github.com/febriyan9346/BlockStreet-Auto-Bot.git
cd BlockStreet-Auto-Bot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure your wallets**

Edit `private_keys.txt`:
```
your_private_key_1:Wallet1
your_private_key_2:Wallet2
your_private_key_3:Wallet3
```

**4. Add 2Captcha API key**

Edit `2captcha.txt`:
```
your_2captcha_api_key
```
> Get your API key from [2captcha.com](https://2captcha.com)

**5. (Optional) Configure proxies**

Edit `proxies.txt`:
```
host:port:username:password
http://user:pass@host:port
```

**6. (Optional) Set invite code**

Create `.env` file:
```
INVITE_CODE=your_invite_code
```

## 💻 Usage

### Starting the Bot

```bash
python bot.py
```

### Main Menu Options

```
╔══════════════════════ MAIN MENU ══════════════════════╗
  [1] Auto Swap          [6] Repay Loan
  [2] Manual Swap        [7] Auto All Operations
  [3] Supply Assets      [8] Set TX Count
  [4] Withdraw Assets    [9] Security Settings
  [5] Borrow Assets
╚═══════════════════════════════════════════════════════╝
  [0] Exit Bot
```

### Option Details

#### [1] Auto Swap
Automatically swaps tokens from your supplied assets with randomized amounts (0.001-0.0015).

#### [2] Manual Swap
Choose specific tokens and amounts for swapping.

#### [3] Supply Assets
Supply tokens to earning pools.

#### [4] Withdraw Assets
Withdraw supplied assets.

#### [5] Borrow Assets
Borrow tokens against your supplied collateral.

#### [6] Repay Loan
Repay borrowed tokens.

#### [7] Auto All Operations ⭐ **Recommended**
Runs a complete automation cycle:
- ✅ Daily check-in
- ✅ 5 automated swaps
- ✅ Supply operations (configurable count)
- ✅ Withdraw operations (configurable count)
- ✅ Borrow operations (configurable count)
- ✅ Repay operations (configurable count)
- ⏰ Repeats every 24 hours

#### [8] Set TX Count
Configure how many transactions to execute per operation (1-100).

#### [9] Security Settings
View current security configuration.

## 📁 File Structure

```
BlockStreet-Auto-Bot/
├── bot.py                  # Main bot script
├── private_keys.txt        # Your wallet private keys
├── 2captcha.txt           # 2Captcha API key
├── proxies.txt            # (Optional) Proxy list
├── .env                   # (Optional) Environment variables
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── assets/
│   └── bot-demo.png      # Demo screenshot
└── README.md             # Documentation
```

## 🔧 Configuration Files

### private_keys.txt
```
# Format: privatekey:WalletName
1234567890abcdef...:MainWallet
abcdef1234567890...:SecondWallet
# Lines starting with # are ignored
```

### proxies.txt
```
# Format options:
host:port:username:password
http://user:pass@host:port
host:port
```

### 2captcha.txt
```
your_2captcha_api_key_here
```

### .env
```
INVITE_CODE=your_invite_code
```

## 🔐 Security Best Practices

| ⚠️ | Security Recommendation |
|----|------------------------|
| 🔑 | **Never share your private keys** - Keep `private_keys.txt` secure |
| 👛 | **Use dedicated wallets** - Don't use your main wallet |
| 👀 | **Monitor transactions** - Check bot operations regularly |
| ⚙️ | **Adjust limits** - Modify `SecurityConfig` class for your needs |
| 🧪 | **Test with small amounts** - Start with minimal funds |
| 🔒 | **Keep API keys safe** - Protect your 2Captcha credentials |
| 📝 | **Review code** - Understand what the bot does before running |
| 🚫 | **Never commit sensitive files** - Use .gitignore properly |

## ⚙️ Customizing Security Settings

Edit the `SecurityConfig` class in `bot.py`:

```python
class SecurityConfig:
    """Security configuration to prevent wallet drain"""
    MAX_TRANSACTION_AMOUNT = 0.01          # Maximum per transaction
    MIN_BALANCE_THRESHOLD = 0.001          # Minimum balance to maintain
    MAX_TRANSACTIONS_PER_HOUR = 100        # Rate limit per wallet
    REQUIRE_CONFIRMATION = False           # Manual confirmation for each TX
```

### Example: Increase Transaction Limit

```python
class SecurityConfig:
    MAX_TRANSACTION_AMOUNT = 0.05  # Increase to 0.05
    # ... other settings
```

## 📊 Transaction Logging

The bot provides detailed colored logging:

| Symbol | Type | Description |
|--------|------|-------------|
| 🔵 | **Info** | General information |
| ✅ | **Success** | Successful operations |
| ⚠️ | **Warning** | Non-critical issues |
| ❌ | **Error** | Failed operations |
| 🔄 | **Process** | Ongoing operations |
| 🔒 | **Security** | Security-related messages |

### Example Log Output
```
13:18:00 [W1] 🔄 Generating signature...
13:18:00 [W1] 🔄 Authenticating with server...
13:18:00 [W1] ✅ Authentication successful ✓
13:18:00 [W1] 🔄 Daily check-in...
13:18:00 [W1] ✅ Daily check-in complete
13:18:00 [W1] ✅ Swap 1/5: 0.001046 COIN → 0.000787 TSLA
```

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>"No wallets configured"</b></summary>

**Solution:**
- Check `private_keys.txt` exists in the same folder as `bot.py`
- Ensure format is: `privatekey:name` (one per line)
- Make sure private keys are valid Ethereum keys
- Remove any empty lines or invalid entries

</details>

<details>
<summary><b>"2Captcha key file not found"</b></summary>

**Solution:**
- Create `2captcha.txt` in the same folder as `bot.py`
- Add your API key from [2captcha.com](https://2captcha.com)
- Ensure file contains only the API key (no extra spaces)

</details>

<details>
<summary><b>"Captcha solving failed"</b></summary>

**Solution:**
- Check your 2Captcha balance at https://2captcha.com
- Verify API key is correct in `2captcha.txt`
- Check internet connection
- Wait a few minutes and try again

</details>

<details>
<summary><b>"Rate limit exceeded"</b></summary>

**Solution:**
- Wait before running more transactions
- Adjust `MAX_TRANSACTIONS_PER_HOUR` in `SecurityConfig`
- Spread operations across multiple wallets

</details>

<details>
<summary><b>"Amount exceeds security limit"</b></summary>

**Solution:**
- Reduce transaction amount
- Modify `MAX_TRANSACTION_AMOUNT` in `SecurityConfig` if needed
- Check that amounts are within reasonable ranges

</details>

## 📝 Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

Requirements:
- `web3>=6.0.0` - Ethereum library
- `eth-account>=0.9.0` - Account management
- `requests>=2.31.0` - HTTP requests
- `python-dotenv>=1.0.0` - Environment variables

## ⚠️ Disclaimer

**IMPORTANT: READ BEFORE USING**

- ⚠️ This bot is for **educational purposes only**
- 💰 Use at your **own risk** - developers are not responsible for financial losses
- 🧪 Always **test with small amounts** first
- 📚 **Understand the risks** involved in automated trading
- 🔒 Keep your **private keys secure** at all times
- 👀 **Monitor bot operations** regularly
- ⚖️ Ensure compliance with your **local regulations**
- 🚫 **Never invest** more than you can afford to lose

**By using this bot, you acknowledge that:**
- You understand the risks of automated cryptocurrency trading
- You are responsible for your own financial decisions
- The developers provide no warranties or guarantees
- You will keep your credentials and private keys secure

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🔧 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔍 Open a Pull Request

### Areas for Contribution
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🧪 Test coverage
- 🎨 UI/UX enhancements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

Need help? Here's how to get support:

- 🐛 **Bug Reports**: [Open an issue](https://github.com/febriyan9346/BlockStreet-Auto-Bot/issues)
- 💡 **Feature Requests**: [Open an issue](https://github.com/febriyan9346/BlockStreet-Auto-Bot/issues)
- 💬 **Questions**: Check [existing issues](https://github.com/febriyan9346/BlockStreet-Auto-Bot/issues) first
- 📧 **Discussions**: [Join discussion](https://github.com/febriyan9346/BlockStreet-Auto-Bot/discussions)

## 🌟 Star History

If you find this bot useful, please consider giving it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=febriyan9346/BlockStreet-Auto-Bot&type=Date)](https://star-history.com/#febriyan9346/BlockStreet-Auto-Bot&Date)

## 🙏 Acknowledgments

- [Web3.py](https://web3py.readthedocs.io/) - Ethereum Python library
- [2Captcha](https://2captcha.com) - Captcha solving service
- [BlockStreet](https://blockstreet.money) - Trading platform

---

<div align="center">

**⚠️ SECURITY WARNING**

This bot handles private keys and performs financial transactions.  
Always review the code before running and never share your private keys or configuration files.

**Made with ❤️ by the community**

[⬆ Back to Top](#blockstreet-auto-bot-)

</div>
