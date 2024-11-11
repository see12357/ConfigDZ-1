import unittest
import os
import shutil
from shell1 import ShellEmulator, generate_files  # Импорт вашего эмулятора и функции генерации файлов

class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Генерация виртуальной файловой системы и стартового скрипта
        generate_files()
        cls.hostname = "test_host"
        cls.filesystem = "virtual_fs.tar"
        cls.startup_script = "startup_script.sh"

    def setUp(self):
        # Создаём новый экземпляр ShellEmulator для каждого теста
        self.shell = ShellEmulator(self.hostname, self.filesystem, None)

    @classmethod
    def tearDownClass(cls):
        # Удаление временной файловой системы после всех тестов
        shutil.rmtree('/tmp/shell_emulator_fs', ignore_errors=True)
        os.remove(cls.filesystem)
        os.remove(cls.startup_script)
        shutil.rmtree("virtual_fs", ignore_errors=True)

    # Тесты для команды ls
    def test_ls_root_directory(self):
        self.shell.current_directory = 'virtual_fs'
        result = self.shell.ls()
        self.assertIn("file1.txt", result)
        self.assertIn("file2.txt", result)
        self.assertIn("subdir", result)

    def test_ls_subdirectory(self):
        self.shell.current_directory = '/virtual_fs/subdir'
        result = self.shell.ls()
        self.assertIn("file3.txt", result)

    def test_ls_nonexistent_directory(self):
        self.shell.current_directory = '/nonexistent'
        result = self.shell.ls()
        self.assertEqual(result, "Путь '/nonexistent' не существует.")

    # Тесты для команды cd
    def test_cd_to_root(self):
        self.shell.cd('virtual_fs')
        self.assertEqual(self.shell.current_directory, '/virtual_fs')

    def test_cd_to_subdirectory(self):
        self.shell.current_directory = '/subdir'
        self.assertEqual(self.shell.current_directory, '/subdir')

    def test_cd_to_nonexistent_directory(self):
        result = self.shell.cd('nonexistent')
        self.assertEqual(self.shell.current_directory, '/')
        self.assertEqual(result, None)

    # Тесты для команды rev
    def test_rev_existing_file(self):
        self.shell.cd('virtual_fs')
        result = self.shell.rev('file1.txt')
        self.assertEqual(result, ".1 алйаф еомижредос отЭ")

    def test_rev_in_subdirectory(self):
        self.shell.current_directory = '/virtual_fs/subdir'
        result = self.shell.rev('file3.txt')
        self.assertEqual(result, ".иироткериддоп в алйаф еомижредос отЭ")

    def test_rev_nonexistent_file(self):
        result = self.shell.rev('nonexistent.txt')
        self.assertEqual(result, "Файл 'nonexistent.txt' не существует.")

    # Тесты для команды whoami
    def test_whoami(self):
        result = self.shell.whoami()
        self.assertEqual(result, os.getlogin())

    def test_whoami_not_empty(self):
        result = self.shell.whoami()
        self.assertTrue(result)

    def test_whoami_is_string(self):
        result = self.shell.whoami()
        self.assertIsInstance(result, str)

    # Тесты для команды exit
    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.shell.exit()

if __name__ == "__main__":
    unittest.main()
