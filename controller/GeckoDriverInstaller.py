from os import chmod
from re import fullmatch, sub
from requests import get
from pathlib import Path
from zipfile import ZipFile
from tarfile import open as tar_open
from platform import system as system_p, machine as machine_p

class GeckoDriverInstaller:
    def __init__(self, download_path: Path = Path.cwd()):
        download_path = sub(r'geckodriver\.exe', '', str(download_path))
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.system_info = self._detect_system()
        self.executable_path = self._find_existing_driver()

    def _find_existing_driver(self):
        """Busca si el driver ya existe en la carpeta de descargas"""
        driver_name = 'geckodriver.exe' if self.system_info['is_windows'] else 'geckodriver'
        possible_path = self.download_path / driver_name
        
        if possible_path.exists():
            return possible_path
        return None

    def _detect_system(self):
        """Detecta el sistema operativo y arquitectura"""
        system = system_p().lower()
        machine = machine_p().lower()

        arch_map = {
            'x86_64': '64',
            'amd64': '64',
            'i386': '32',
            'i686': '32',
            'arm64': 'arm64',
            'aarch64': 'arm64'
        }

        arch = arch_map.get(machine, machine)

        return {
            'system': system,
            'arch': arch,
            'is_linux': system == 'linux',
            'is_windows': system == 'windows',
            'is_mac': system == 'darwin'
        }

    def _get_asset_pattern(self):
        """Genera el patrón regex para buscar el asset correcto"""
        if self.system_info['is_linux']:
            if self.system_info['arch'] == 'arm64':
                return r'geckodriver-v\d+\.\d+\.\d+-linux-aarch64\.tar\.gz'
            return r'geckodriver-v\d+\.\d+\.\d+-linux64\.tar\.gz'
        elif self.system_info['is_windows']:
            return r'geckodriver-v\d+\.\d+\.\d+-win64\.zip'
        elif self.system_info['is_mac']:
            if self.system_info['arch'] == 'arm64':
                return r'geckodriver-v\d+\.\d+\.\d+-macos-aarch64\.tar\.gz'
            return r'geckodriver-v\d+\.\d+\.\d+-macos\.tar\.gz'
        raise Exception("Sistema no soportado")

    def install(self):
        """Descarga y extrae el geckodriver adecuado para el sistema si no existe"""
        if self.executable_path is not None:
            return self.executable_path

        try:
            # Obtener última versión desde GitHub
            api_url = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
            response = get(api_url, timeout=10)
            response.raise_for_status()

            # Buscar asset con regex
            pattern = self._get_asset_pattern()
            assets = response.json()["assets"]
            download_url = None

            for asset in assets:
                if fullmatch(pattern, asset["name"]):
                    download_url = asset["browser_download_url"]
                    break

            if not download_url:
                raise Exception(f"No se encontró asset que coincida con {pattern}")
            
            file_ext = '.zip' if self.system_info['is_windows'] else '.tar.gz'
            temp_file = self.download_path / f"geckodriver-latest{file_ext}"

            with get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(temp_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            if self.system_info['is_windows']:
                with ZipFile(temp_file, 'r') as zip_ref:
                    zip_ref.extractall(self.download_path)
                self.executable_path = self.download_path / 'geckodriver.exe'
            else:
                with tar_open(temp_file) as tar:
                    tar.extractall(self.download_path)
                self.executable_path = self.download_path / 'geckodriver'
                chmod(self.executable_path, 0o755)

        except Exception as e:
            print(f"Error durante instalación: {e}")
            raise
        finally:
            if 'temp_file' in locals() and temp_file.exists():
                temp_file.unlink()

    def get_driver_path(self) -> Path:
        """Devuelve la ruta del driver, instalándolo si es necesario"""
        if self.executable_path is None:
            self.install()
        return self.executable_path