from abc import ABC, abstractmethod


class BashLinuxBackendCorrector(ABC):
    @abstractmethod
    def correct_cron_file(self, cron_file):
        pass

    @abstractmethod
    def correct_script_file(self, script_file):
        pass

    @abstractmethod
    def correct_sales_file(self, __correct_sales_file):
        pass
