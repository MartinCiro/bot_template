from controller.GeckoDriverInstaller import GeckoDriverInstaller
from controller.utils.Helpers import Helpers
helper = Helpers()
driver_installer = GeckoDriverInstaller(helper.get_routes("SELENIUM", "pb_path"))
driver_installer.install()

driver_path = driver_installer.get_driver_path()
print("Path del driver:", driver_path)