import os
import sys
import time
import json
import random
import asyncio
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv

load_dotenv()

class Colors:
    RESET = "\033[0m"
    BRIGHT = "\033[1m"
    GREEN = "\033[32m\033[1m"
    YELLOW = "\033[33m\033[1m"
    BLUE = "\033[34m\033[1m"
    MAGENTA = "\033[35m\033[1m"
    CYAN = "\033[36m\033[1m"
    WHITE = "\033[37m\033[1m"
    RED = "\033[31m\033[1m"
    GRAY = "\033[90m"

class SecurityConfig:
    """Security configuration to prevent wallet drain"""
    MAX_TRANSACTION_AMOUNT = 0.01
    MIN_BALANCE_THRESHOLD = 0.001
    MAX_TRANSACTIONS_PER_HOUR = 100
    REQUIRE_CONFIRMATION = False

class Logger:
    """Enhanced logger with custom formatting"""
    
    @staticmethod
    def clear_terminal():
        os.system('clear' if os.name != 'nt' else 'cls')
    
    @staticmethod
    def _get_timestamp():
        wib_timezone = timezone(timedelta(hours=7))
        return datetime.now(wib_timezone).strftime("%H:%M:%S")
    
    @staticmethod
    def info(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.BLUE}[{wallet_display}]{Colors.RESET} {msg}")
    
    @staticmethod
    def success(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.GREEN}[{wallet_display}]{Colors.RESET} ✅ {msg}")
    
    @staticmethod
    def error(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.RED}[{wallet_display}]{Colors.RESET} ❌ {msg}")
    
    @staticmethod
    def warning(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.YELLOW}[{wallet_display}]{Colors.RESET} ⚡ {msg}")
    
    @staticmethod
    def process(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.MAGENTA}[{wallet_display}]{Colors.RESET} 🔄 {msg}")
    
    @staticmethod
    def security(msg: str):
        timestamp = Logger._get_timestamp()
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.RED}[SECURITY]{Colors.RESET} 🔐 {msg}")

def display_banner():
    """Display application banner"""
    banner = f"""{Colors.CYAN}
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║                 BlockStreet Auto Bot                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)

def display_menu():
    """Display main menu"""
    print(f"\n{Colors.CYAN}╔════════════════════ MAIN MENU ════════════════════╗{Colors.RESET}")
    print(f"{Colors.GREEN}  [1]{Colors.RESET} Auto Swap          {Colors.GREEN}[6]{Colors.RESET} Repay Loan")
    print(f"{Colors.GREEN}  [2]{Colors.RESET} Manual Swap        {Colors.GREEN}[7]{Colors.RESET} Auto All Operations")
    print(f"{Colors.GREEN}  [3]{Colors.RESET} Supply Assets      {Colors.GREEN}[8]{Colors.RESET} Set TX Count")
    print(f"{Colors.GREEN}  [4]{Colors.RESET} Withdraw Assets    {Colors.GREEN}[9]{Colors.RESET} Security Settings")
    print(f"{Colors.GREEN}  [5]{Colors.RESET} Borrow Assets")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"{Colors.RED}  [0]{Colors.RESET} Exit Bot\n")

class WalletManager:
    """Secure wallet management"""
    
    @staticmethod
    def load_wallets_from_file(filename: str = 'private_keys.txt') -> List[Dict]:
        """Load wallets from file with validation"""
        wallets = []
        
        if not Path(filename).exists():
            Logger.error(None, f'Configuration file {filename} not found')
            Logger.info(None, f'Create {filename} with format: privatekey:wallet_name')
            return wallets
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            for idx, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split(':')
                    private_key = parts[0].strip()
                    name = parts[1].strip() if len(parts) > 1 else f'W{idx}'
                    
                    if not private_key.startswith('0x'):
                        private_key = '0x' + private_key
                    
                    account = Account.from_key(private_key)
                    
                    wallets.append({
                        'account': account,
                        'name': name,
                        'address': account.address
                    })
                    
                except Exception as e:
                    Logger.warning(None, f'Invalid wallet config at line {idx}')
            
            if wallets:
                Logger.success(None, f'Successfully loaded {len(wallets)} wallet(s)')
        
        except Exception as e:
            Logger.error(None, f'Failed to read configuration: {str(e)}')
        
        return wallets
    
    @staticmethod
    def validate_transaction_amount(amount: float) -> bool:
        """Validate transaction amount against security limits"""
        if amount > SecurityConfig.MAX_TRANSACTION_AMOUNT:
            Logger.security(f'Amount {amount} exceeds limit {SecurityConfig.MAX_TRANSACTION_AMOUNT}')
            return False
        return True

class ProxyManager:
    """Proxy management"""
    
    @staticmethod
    def parse_proxy(proxy_line: str) -> Optional[str]:
        """Parse proxy string into proper format"""
        proxy = proxy_line.strip()
        if not proxy or proxy.startswith('#'):
            return None
        
        proxy = proxy.replace('http://', '').replace('https://', '')
        
        if '@' in proxy:
            parts = proxy.split('@')
            if len(parts) == 2:
                host_port = parts[0]
                user_pass = parts[1]
                return f'http://{user_pass}@{host_port}'
        
        parts = proxy.split(':')
        if len(parts) == 4:
            host, port, user, password = parts
            return f'http://{user}:{password}@{host}:{port}'
        
        return f'http://{proxy}'
    
    @staticmethod
    def load_proxies(filename: str = 'proxies.txt') -> List[str]:
        """Load proxies from file"""
        proxies = []
        
        if not Path(filename).exists():
            return proxies
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                proxy = ProxyManager.parse_proxy(line)
                if proxy:
                    proxies.append(proxy)
        
        except Exception as e:
            Logger.error(None, f'Proxy loading error: {str(e)}')
        
        return proxies

class CaptchaSolver:
    """2Captcha solver with security checks"""
    
    @staticmethod
    def get_api_key(filename: str = '2captcha.txt') -> Optional[str]:
        """Get 2captcha API key from file"""
        try:
            if not Path(filename).exists():
                Logger.error(None, f'2Captcha key file {filename} not found')
                Logger.info(None, 'Create 2captcha.txt and add your API key')
                return None
            
            with open(filename, 'r') as f:
                key = f.read().strip()
            
            if not key:
                Logger.error(None, f'2Captcha key file is empty')
                return None
            
            Logger.success(None, '2Captcha API key loaded successfully')
            return key
        
        except Exception as e:
            Logger.error(None, f'Key file read error: {str(e)}')
            return None
    
    @staticmethod
    async def solve_turnstile(api_key: str, sitekey: str, pageurl: str) -> Optional[str]:
        """Solve Cloudflare Turnstile captcha using 2Captcha"""
        Logger.process(None, 'Initializing 2Captcha solver...')
        
        if not api_key:
            raise Exception('2Captcha API key is required')
        
        submit_url = 'http://2captcha.com/in.php'
        result_url = 'http://2captcha.com/res.php'
        
        submit_data = {
            'key': api_key,
            'method': 'turnstile',
            'sitekey': sitekey,
            'pageurl': pageurl,
            'json': 1
        }
        
        try:
            Logger.process(None, 'Submitting captcha to 2Captcha...')
            response = requests.post(submit_url, data=submit_data, timeout=30)
            result = response.json()
            
            if result.get('status') != 1:
                error_msg = result.get('request', 'Unknown error')
                raise Exception(f"2Captcha submit failed: {error_msg}")
            
            captcha_id = result['request']
            Logger.process(None, f'Captcha ID: {captcha_id}')
            Logger.process(None, 'Waiting for 2Captcha solution...')
            
            max_attempts = 40
            for attempt in range(max_attempts):
                await asyncio.sleep(5)
                
                res_params = {
                    'key': api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
                
                res_response = requests.get(result_url, params=res_params, timeout=30)
                res_result = res_response.json()
                
                if res_result.get('status') == 1:
                    Logger.success(None, '2Captcha solved successfully ✓')
                    return res_result['request']
                
                if res_result.get('request') == 'CAPCHA_NOT_READY':
                    if (attempt + 1) % 6 == 0:
                        Logger.process(None, f'Still solving... ({attempt + 1}/{max_attempts})')
                    continue
                
                error_code = res_result.get('request', 'UNKNOWN_ERROR')
                if error_code != 'CAPCHA_NOT_READY':
                    raise Exception(f"2Captcha error: {error_code}")
            
            raise Exception('2Captcha timeout - took too long to solve')
        
        except requests.exceptions.RequestException as e:
            raise Exception(f'2Captcha network error: {str(e)}')
        except Exception as e:
            raise Exception(f'2Captcha error: {str(e)}')

class BlockStreetAPI:
    """BlockStreet API client with security features"""
    
    CUSTOM_SIGN_TEXT = """blockstreet.money wants you to sign in with your Ethereum account:
0x4CBB1421DF1CF362DC618d887056802d8adB7BC0

Welcome to Block Street

URI: https://blockstreet.money
Version: 1
Chain ID: 1
Nonce: Z9YFj5VY80yTwN3n
Issued At: 2025-10-27T09:49:38.537Z
Expiration Time: 2025-10-27T09:51:38.537Z"""
    
    def __init__(self, wallet_data: Dict, proxy: Optional[str] = None):
        self.wallet_data = wallet_data
        self.account = wallet_data['account']
        self.name = wallet_data['name']
        self.address = wallet_data['address']
        self.session_cookie = None
        self.transaction_count = 0
        self.last_transaction_time = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://blockstreet.money',
            'referer': 'https://blockstreet.money/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
        })
        
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        current_time = time.time()
        if current_time - self.last_transaction_time < 3600:
            if self.transaction_count >= SecurityConfig.MAX_TRANSACTIONS_PER_HOUR:
                Logger.security(f'Rate limit reached for {self.name}')
                return False
        else:
            self.transaction_count = 0
            self.last_transaction_time = current_time
        
        self.transaction_count += 1
        return True
    
    def _send_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Send HTTP request with security checks"""
        url = f'https://api.blockstreet.money/api{endpoint}'
        
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        if self.session_cookie:
            headers['Cookie'] = self.session_cookie
        
        try:
            response = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
            
            if 'set-cookie' in response.headers:
                cookie = response.headers['set-cookie']
                if 'gfsessionid=' in cookie:
                    self.session_cookie = cookie.split(';')[0]
            
            if response.status_code >= 200 and response.status_code < 300:
                data = response.json()
                if data.get('code') in [0, '0']:
                    return data.get('data', data)
                return data
            
            raise Exception(f'HTTP {response.status_code}: {response.text}')
        
        except Exception as e:
            raise Exception(f'Request failed: {str(e)}')
    
    async def login(self, captcha_token: str) -> Dict:
        """Login to BlockStreet"""
        try:
            Logger.process(self.name, 'Generating signature...')
            
            message = encode_defunct(text=self.CUSTOM_SIGN_TEXT)
            signed_message = self.account.sign_message(message)
            signature = signed_message.signature.hex()
            
            import re
            nonce_match = re.search(r'Nonce:\s*([^\n\r]+)', self.CUSTOM_SIGN_TEXT)
            nonce = nonce_match.group(1).strip() if nonce_match else 'Z9YFj5VY80yTwN3n'
            
            issued_match = re.search(r'Issued At:\s*([^\n\r]+)', self.CUSTOM_SIGN_TEXT)
            issued_at = issued_match.group(1).strip() if issued_match else datetime.now().isoformat()
            
            expiration_match = re.search(r'Expiration Time:\s*([^\n\r]+)', self.CUSTOM_SIGN_TEXT)
            expiration_time = expiration_match.group(1).strip() if expiration_match else datetime.now().isoformat()
            
            data = {
                'address': self.address,
                'nonce': nonce,
                'signature': signature,
                'chainId': '1',
                'issuedAt': issued_at,
                'expirationTime': expiration_time,
                'invite_code': os.getenv('INVITE_CODE', '')
            }
            
            Logger.process(self.name, 'Authenticating with server...')
            result = self._send_request('POST', '/account/signverify', data=data)
            
            Logger.success(self.name, 'Authentication successful ✓')
            return result
        
        except Exception as e:
            raise Exception(f'Authentication failed: {str(e)}')
    
    def get_token_list(self) -> List[Dict]:
        """Get available tokens"""
        return self._send_request('GET', '/swap/token_list')
    
    def get_earn_info(self) -> Dict:
        """Get earning information"""
        return self._send_request('GET', '/earn/info')
    
    def get_supplies(self) -> List[Dict]:
        """Get supplied assets"""
        return self._send_request('GET', '/my/supply')
    
    def share(self) -> Dict:
        """Daily check-in"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        return self._send_request('POST', '/share')
    
    def swap(self, from_symbol: str, to_symbol: str, from_amount: float, to_amount: float) -> Dict:
        """Swap tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(from_amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'from_symbol': from_symbol,
            'to_symbol': to_symbol,
            'from_amount': str(from_amount),
            'to_amount': str(to_amount)
        }
        
        return self._send_request('POST', '/swap', json=data)
    
    def supply(self, symbol: str, amount: float) -> Dict:
        """Supply tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/supply', json=data)
    
    def withdraw(self, symbol: str, amount: float) -> Dict:
        """Withdraw tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/withdraw', json=data)
    
    def borrow(self, symbol: str, amount: float) -> Dict:
        """Borrow tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/borrow', json=data)
    
    def repay(self, symbol: str, amount: float) -> Dict:
        """Repay borrowed tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/repay', json=data)

async def process_auto_swap(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process auto swap for all wallets"""
    Logger.info(None, f'Starting Auto Swap for {len(wallets)} wallet(s)')
    Logger.info(None, f'Transactions per wallet: {tx_count}')
    
    proxy_index = 0
    for idx, wallet_data in enumerate(wallets, 1):
        proxy = proxies[proxy_index % len(proxies)] if proxies else None
        proxy_index += 1
        
        print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.YELLOW}Processing Wallet {idx}/{len(wallets)}: {wallet_data['name']}{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        
        api = BlockStreetAPI(wallet_data, proxy)
        
        try:
            await api.login(captcha_token)
            
            supplies = api.get_supplies()
            owned_tokens = [s for s in supplies if s and float(s.get('amount', 0)) > 0]
            
            if not owned_tokens:
                Logger.warning(wallet_data['name'], 'No supplied assets found to swap')
                continue
            
            for i in range(tx_count):
                Logger.process(wallet_data['name'], f'Executing swap {i + 1}/{tx_count}')
                
                try:
                    from_asset = random.choice(owned_tokens)
                    from_token = next((t for t in token_list if t['symbol'] == from_asset['symbol']), None)
                    
                    if not from_token:
                        continue
                    
                    to_token = random.choice([t for t in token_list if t['symbol'] != from_token['symbol']])
                    
                    from_amount = get_random_amount(0.001, 0.0015)
                    to_amount = (from_amount * float(from_token.get('price', 1))) / float(to_token.get('price', 1))
                    
                    api.swap(from_token['symbol'], to_token['symbol'], from_amount, to_amount)
                    Logger.success(wallet_data['name'], f'Swapped {from_amount:.6f} {from_token["symbol"]} → {to_amount:.6f} {to_token["symbol"]}')
                    
                except Exception as e:
                    Logger.error(wallet_data['name'], f'Swap failed: {str(e)}')
                
                if i < tx_count - 1:
                    await random_delay()
        
        except Exception as e:
            Logger.error(wallet_data['name'], f'Error: {str(e)}')
        
        await asyncio.sleep(3)

async def process_manual_swap(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process manual swap for all wallets"""
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}SELECT TOKEN TO SWAP FROM:{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    for idx, token in enumerate(token_list[:20], 1):
        print(f"{Colors.GREEN}[{idx}]{Colors.RESET} {token['symbol']}")
    
    try:
        from_idx = int(input(f"\n{Colors.CYAN}>{Colors.RESET} Select FROM token (1-20): ")) - 1
        from_token = token_list[from_idx]
    except:
        Logger.error(None, 'Invalid selection')
        return
    
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}SELECT TOKEN TO SWAP TO:{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    for idx, token in enumerate(token_list[:20], 1):
        if token['symbol'] != from_token['symbol']:
            print(f"{Colors.GREEN}[{idx}]{Colors.RESET} {token['symbol']}")
    
    try:
        to_idx = int(input(f"\n{Colors.CYAN}>{Colors.RESET} Select TO token (1-20): ")) - 1
        to_token = token_list[to_idx]
    except:
        Logger.error(None, 'Invalid selection')
        return
    
    try:
        from_amount = float(input(f"\n{Colors.CYAN}>{Colors.RESET} Amount of {from_token['symbol']} to swap: "))
    except:
        Logger.error(None, 'Invalid amount')
        return
    
    Logger.info(None, f'Starting Manual Swap: {from_amount} {from_token["symbol"]} → {to_token["symbol"]}')
    
    proxy_index = 0
    for idx, wallet_data in enumerate(wallets, 1):
        proxy = proxies[proxy_index % len(proxies)] if proxies else None
        proxy_index += 1
        
        api = BlockStreetAPI(wallet_data, proxy)
        
        try:
            await api.login(captcha_token)
            
            for i in range(tx_count):
                Logger.process(wallet_data['name'], f'Executing swap {i + 1}/{tx_count}')
                
                try:
                    to_amount = (from_amount * float(from_token.get('price', 1))) / float(to_token.get('price', 1))
                    api.swap(from_token['symbol'], to_token['symbol'], from_amount, to_amount)
                    Logger.success(wallet_data['name'], f'Swapped {from_amount:.6f} {from_token["symbol"]} → {to_amount:.6f} {to_token["symbol"]}')
                except Exception as e:
                    Logger.error(wallet_data['name'], f'Swap failed: {str(e)}')
                
                if i < tx_count - 1:
                    await random_delay()
        
        except Exception as e:
            Logger.error(wallet_data['name'], f'Error: {str(e)}')
        
        await asyncio.sleep(3)

async def process_supply(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process supply for all wallets"""
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}SELECT TOKEN TO SUPPLY:{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    for idx, token in enumerate(token_list[:20], 1):
        print(f"{Colors.GREEN}[{idx}]{Colors.RESET} {token['symbol']}")
    
    try:
        token_idx = int(input(f"\n{Colors.CYAN}>{Colors.RESET} Select token (1-20): ")) - 1
        selected_token = token_list[token_idx]
        amount = float(input(f"{Colors.CYAN}>{Colors.RESET} Amount to supply: "))
    except:
        Logger.error(None, 'Invalid input')
        return
    
    Logger.info(None, f'Starting Supply: {amount} {selected_token["symbol"]}')
    
    proxy_index = 0
    for idx, wallet_data in enumerate(wallets, 1):
        proxy = proxies[proxy_index % len(proxies)] if proxies else None
        proxy_index += 1
        
        api = BlockStreetAPI(wallet_data, proxy)
        
        try:
            await api.login(captcha_token)
            
            for i in range(tx_count):
                Logger.process(wallet_data['name'], f'Executing supply {i + 1}/{tx_count}')
                
                try:
                    api.supply(selected_token['symbol'], amount)
                    Logger.success(wallet_data['name'], f'Supplied {amount:.6f} {selected_token["symbol"]}')
                except Exception as e:
                    Logger.error(wallet_data['name'], f'Supply failed: {str(e)}')
                
                if i < tx_count - 1:
                    await random_delay()
        
        except Exception as e:
            Logger.error(wallet_data['name'], f'Error: {str(e)}')
        
        await asyncio.sleep(3)

async def process_withdraw(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process withdraw for all wallets"""
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}SELECT TOKEN TO WITHDRAW:{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    for idx, token in enumerate(token_list[:20], 1):
        print(f"{Colors.GREEN}[{idx}]{Colors.RESET} {token['symbol']}")
    
    try:
        token_idx = int(input(f"\n{Colors.CYAN}>{Colors.RESET} Select token (1-20): ")) - 1
        selected_token = token_list[token_idx]
        amount = float(input(f"{Colors.CYAN}>{Colors.RESET} Amount to withdraw: "))
    except:
        Logger.error(None, 'Invalid input')
        return
    
    Logger.info(None, f'Starting Withdrawal: {amount} {selected_token["symbol"]}')
    
    proxy_index = 0
    for idx, wallet_data in enumerate(wallets, 1):
        proxy = proxies[proxy_index % len(proxies)] if proxies else None
        proxy_index += 1
        
        api = BlockStreetAPI(wallet_data, proxy)
        
        try:
            await api.login(captcha_token)
            
            for i in range(tx_count):
                Logger.process(wallet_data['name'], f'Executing withdrawal {i + 1}/{tx_count}')
                
                try:
                    api.withdraw(selected_token['symbol'], amount)
                    Logger.success(wallet_data['name'], f'Withdrew {amount:.6f} {selected_token["symbol"]}')
                except Exception as e:
                    Logger.error(wallet_data['name'], f'Withdrawal failed: {str(e)}')
                
                if i < tx_count - 1:
                    await random_delay()
        
        except Exception as e:
            Logger.error(wallet_data['name'], f'Error: {str(e)}')
        
        await asyncio.sleep(3)

async def process_borrow(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process borrow for all wallets"""
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}SELECT TOKEN TO BORROW:{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    for idx, token in enumerate(token_list[:20], 1):
        print(f"{Colors.GREEN}[{idx}]{Colors.RESET} {token['symbol']}")
    
    try:
        token_idx = int(input(f"\n{Colors.CYAN}>{Colors.RESET} Select token (1-20): ")) - 1
        selected_token = token_list[token_idx]
        amount = float(input(f"{Colors.CYAN}>{Colors.RESET} Amount to borrow: "))
    except:
        Logger.error(None, 'Invalid input')
        return
    
    Logger.info(None, f'Starting Borrow: {amount} {selected_token["symbol"]}')
    
    proxy_index = 0
    for idx, wallet_data in enumerate(wallets, 1):
        proxy = proxies[proxy_index % len(proxies)] if proxies else None
        proxy_index += 1
        
        api = BlockStreetAPI(wallet_data, proxy)
        
        try:
            await api.login(captcha_token)
            
            for i in range(tx_count):
                Logger.process(wallet_data['name'], f'Executing borrow {i + 1}/{tx_count}')
                
                try:
                    api.borrow(selected_token['symbol'], amount)
                    Logger.success(wallet_data['name'], f'Borrowed {amount:.6f} {selected_token["symbol"]}')
                except Exception as e:
                    Logger.error(wallet_data['name'], f'Borrow failed: {str(e)}')
                
                if i < tx_count - 1:
                    await random_delay()
        
        except Exception as e:
            Logger.error(wallet_data['name'], f'Error: {str(e)}')
        
        await asyncio.sleep(3)

async def process_repay(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process repay for all wallets"""
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}SELECT TOKEN TO REPAY:{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    for idx, token in enumerate(token_list[:20], 1):
        print(f"{Colors.GREEN}[{idx}]{Colors.RESET} {token['symbol']}")
    
    try:
        token_idx = int(input(f"\n{Colors.CYAN}>{Colors.RESET} Select token (1-20): ")) - 1
        selected_token = token_list[token_idx]
        amount = float(input(f"{Colors.CYAN}>{Colors.RESET} Amount to repay: "))
    except:
        Logger.error(None, 'Invalid input')
        return
    
    Logger.info(None, f'Starting Repay: {amount} {selected_token["symbol"]}')
    
    proxy_index = 0
    for idx, wallet_data in enumerate(wallets, 1):
        proxy = proxies[proxy_index % len(proxies)] if proxies else None
        proxy_index += 1
        
        api = BlockStreetAPI(wallet_data, proxy)
        
        try:
            await api.login(captcha_token)
            
            for i in range(tx_count):
                Logger.process(wallet_data['name'], f'Executing repay {i + 1}/{tx_count}')
                
                try:
                    api.repay(selected_token['symbol'], amount)
                    Logger.success(wallet_data['name'], f'Repaid {amount:.6f} {selected_token["symbol"]}')
                except Exception as e:
                    Logger.error(wallet_data['name'], f'Repay failed: {str(e)}')
                
                if i < tx_count - 1:
                    await random_delay()
        
        except Exception as e:
            Logger.error(wallet_data['name'], f'Error: {str(e)}')
        
        await asyncio.sleep(3)

async def process_auto_all(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process auto all operations"""
    Logger.info(None, f'Starting Auto All for {len(wallets)} wallet(s)')
    Logger.info(None, 'Running daily check-in and all operations automatically')
    
    while True:
        proxy_index = 0
        for idx, wallet_data in enumerate(wallets, 1):
            proxy = proxies[proxy_index % len(proxies)] if proxies else None
            proxy_index += 1
            
            print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
            print(f"{Colors.YELLOW}Processing Wallet {idx}/{len(wallets)}: {wallet_data['name']}{Colors.RESET}")
            print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
            
            api = BlockStreetAPI(wallet_data, proxy)
            
            try:
                await api.login(captcha_token)
                
                Logger.process(wallet_data['name'], 'Daily check-in...')
                try:
                    api.share()
                    Logger.success(wallet_data['name'], 'Daily check-in complete')
                except Exception as e:
                    Logger.warning(wallet_data['name'], f'Check-in: {str(e)}')
                
                supplies = api.get_supplies()
                owned_tokens = [s for s in supplies if s and float(s.get('amount', 0)) > 0]
                
                if owned_tokens:
                    Logger.process(wallet_data['name'], 'Executing 5 swaps...')
                    for j in range(5):
                        try:
                            from_asset = random.choice(owned_tokens)
                            from_token = next((t for t in token_list if t['symbol'] == from_asset['symbol']), None)
                            
                            if from_token:
                                to_token = random.choice([t for t in token_list if t['symbol'] != from_token['symbol']])
                                from_amount = get_random_amount(0.001, 0.0015)
                                to_amount = (from_amount * float(from_token.get('price', 1))) / float(to_token.get('price', 1))
                                
                                api.swap(from_token['symbol'], to_token['symbol'], from_amount, to_amount)
                                Logger.success(wallet_data['name'], f'Swap {j+1}/5: {from_amount:.6f} {from_token["symbol"]} → {to_amount:.6f} {to_token["symbol"]}')
                        except Exception as e:
                            Logger.error(wallet_data['name'], f'Swap {j+1}/5: {str(e)}')
                        
                        await random_delay()
                
                operations = [
                    ('Supply', api.supply),
                    ('Withdraw', api.withdraw),
                    ('Borrow', api.borrow),
                    ('Repay', api.repay)
                ]
                
                for op_name, op_func in operations:
                    Logger.process(wallet_data['name'], f'Executing {tx_count} {op_name}(s)...')
                    for j in range(tx_count):
                        try:
                            random_token = random.choice(token_list)
                            amount = get_random_amount(0.001, 0.0015)
                            op_func(random_token['symbol'], amount)
                            Logger.success(wallet_data['name'], f'{op_name} {j+1}/{tx_count}: {amount:.6f} {random_token["symbol"]}')
                        except Exception as e:
                            Logger.error(wallet_data['name'], f'{op_name} {j+1}/{tx_count}: {str(e)}')
                        
                        await random_delay()
                
                Logger.success(wallet_data['name'], 'All operations completed')
            
            except Exception as e:
                Logger.error(wallet_data['name'], f'Error: {str(e)}')
            
            await asyncio.sleep(5)
        
        Logger.success(None, 'Daily run completed for all wallets')
        Logger.info(None, 'Waiting 24 hours for next run...')
        
        for remaining in range(24 * 60 * 60, 0, -1):
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60
            print(f"\r{Colors.CYAN}⏳ Next run in: {hours:02d}:{minutes:02d}:{seconds:02d}{Colors.RESET}", end='')
            await asyncio.sleep(1)
        
        print()

def get_random_amount(min_val: float, max_val: float) -> float:
    """Get random amount within range"""
    amount = random.uniform(min_val, max_val)
    return min(amount, SecurityConfig.MAX_TRANSACTION_AMOUNT)

async def random_delay(min_sec: int = 5, max_sec: int = 10):
    """Random delay between operations"""
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

def display_security_settings():
    """Display current security settings"""
    print(f"\n{Colors.CYAN}╔═══════════════ SECURITY CONFIGURATION ════════════════╗{Colors.RESET}")
    print(f"  Max TX Amount:              {Colors.GREEN}{SecurityConfig.MAX_TRANSACTION_AMOUNT}{Colors.RESET}")
    print(f"  Min Balance Threshold:      {Colors.GREEN}{SecurityConfig.MIN_BALANCE_THRESHOLD}{Colors.RESET}")
    print(f"  Max TX per Hour:            {Colors.GREEN}{SecurityConfig.MAX_TRANSACTIONS_PER_HOUR}{Colors.RESET}")
    confirm_status = f"{Colors.GREEN}YES{Colors.RESET}" if SecurityConfig.REQUIRE_CONFIRMATION else f"{Colors.RED}NO{Colors.RESET}"
    print(f"  Require Confirmation:       {confirm_status}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════╝{Colors.RESET}\n")

def display_wallet_info(wallets: List[Dict]):
    """Display loaded wallet information"""
    print(f"\n{Colors.CYAN}╔═══════════════ WALLET CONFIGURATION ══════════════════╗{Colors.RESET}")
    print(f"  Total Wallets Loaded: {Colors.GREEN}{len(wallets)}{Colors.RESET}\n")
    for idx, wallet in enumerate(wallets, 1):
        addr_short = f"{wallet['address'][:6]}...{wallet['address'][-4:]}"
        print(f"  {Colors.GREEN}#{idx}{Colors.RESET} {wallet['name']:<15} {Colors.GRAY}{addr_short}{Colors.RESET}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════╝{Colors.RESET}\n")

async def main():
    """Main application entry point"""
    Logger.clear_terminal()
    display_banner()
    
    Logger.process(None, 'Loading wallet configuration...')
    wallets = WalletManager.load_wallets_from_file()
    if not wallets:
        Logger.error(None, 'No wallets configured. Exiting.')
        return
    
    Logger.process(None, 'Loading proxy configuration...')
    proxies = ProxyManager.load_proxies()
    if proxies:
        Logger.success(None, f'{len(proxies)} proxy server(s) configured')
    else:
        Logger.warning(None, 'No proxies configured - using direct connection')
    
    display_wallet_info(wallets)
    
    Logger.process(None, 'Loading API credentials...')
    captcha_key = CaptchaSolver.get_api_key()
    if not captcha_key:
        Logger.error(None, 'API key required. Exiting.')
        return
    
    try:
        captcha_token = await CaptchaSolver.solve_turnstile(
            captcha_key,
            '0x4AAAAAABpfyUqunlqwRBYN',
            'https://blockstreet.money/dashboard'
        )
    except Exception as e:
        Logger.error(None, f'Captcha failed: {str(e)}')
        return
    
    Logger.process(None, 'Initializing connection...')
    proxy = proxies[0] if proxies else None
    api = BlockStreetAPI(wallets[0], proxy)
    
    try:
        await api.login(captcha_token)
        Logger.process(None, 'Fetching available tokens...')
        token_list = api.get_token_list()
        Logger.success(None, f'{len(token_list)} tokens available for trading')
        
        try:
            earn_info = api.get_earn_info()
            if earn_info and 'balance' in earn_info:
                balance = float(earn_info['balance'])
                Logger.info(wallets[0]['name'], f'Balance: {balance:.4f}')
        except:
            pass
            
    except Exception as e:
        Logger.error(None, f'Initialization failed: {str(e)}')
        return
    
    transaction_count = 1
    
    while True:
        display_menu()
        status_text = f"TX Count: {Colors.GREEN}{transaction_count}{Colors.RESET}"
        print(f"  {status_text}\n")
        
        choice = input(f"{Colors.CYAN}>{Colors.RESET} Select option: ").strip()
        
        if choice == '0':
            Logger.info(None, 'Shutting down bot...')
            Logger.success(None, 'Bot stopped successfully')
            break
        
        elif choice == '9':
            display_security_settings()
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == '8':
            try:
                new_count = int(input(f"{Colors.CYAN}>{Colors.RESET} Enter TX count (1-100): "))
                if 1 <= new_count <= 100:
                    transaction_count = new_count
                    Logger.success(None, f'TX count set to {transaction_count}')
                else:
                    Logger.error(None, 'Invalid range. Must be 1-100')
            except ValueError:
                Logger.error(None, 'Invalid input. Enter a number')
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == '1':
            await process_auto_swap(wallets, proxies, token_list, captcha_token, transaction_count)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

        elif choice == '2':
            await process_manual_swap(wallets, proxies, token_list, captcha_token, transaction_count)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

        elif choice == '3':
            await process_supply(wallets, proxies, token_list, captcha_token, transaction_count)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

        elif choice == '4':
            await process_withdraw(wallets, proxies, token_list, captcha_token, transaction_count)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

        elif choice == '5':
            await process_borrow(wallets, proxies, token_list, captcha_token, transaction_count)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

        elif choice == '6':
            await process_repay(wallets, proxies, token_list, captcha_token, transaction_count)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

        elif choice == '7':
            await process_auto_all(wallets, proxies, token_list, captcha_token, transaction_count)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        else:
            Logger.warning(None, 'Invalid option. Please try again.')
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        Logger.clear_terminal()
        display_banner()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Bot interrupted by user{Colors.RESET}")
    except Exception as e:
        Logger.error(None, f'Critical error: {str(e)}')
