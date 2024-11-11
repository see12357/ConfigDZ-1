import os
import tarfile
import argparse
import time
from datetime import datetime
import shutil
import sys
import getpass  # For whoami command
class ShellEmulator:
    def __init__(self, hostname, fs_archive, startup_script):
        self.hostname = hostname
        self.current_directory = '/'
        self.fs_root = '/tmp/shell_emulator_fs'  # Виртуальная файловая система во временной папке

        # Распаковка виртуальной файловой системы
        self.extract_fs(fs_archive)

        # Запуск стартового скрипта, если он задан
        if startup_script:
            self.execute_startup_script(startup_script)

    def extract_fs(self, fs_archive):
        """Распаковывает виртуальную файловую систему в заданную папку."""
        if os.path.exists(self.fs_root):
            shutil.rmtree(self.fs_root)
        os.makedirs(self.fs_root)

        with tarfile.open(fs_archive, 'r') as tar:
            tar.extractall(path=self.fs_root)

    def execute_startup_script(self, script_path):
        """Выполняет команды из стартового скрипта."""
        with open(script_path, 'r') as script:
            for line in script:
                self.run_command(line.strip())

    def prompt(self):
        """Показывает приглашение к вводу."""
        return f"{self.hostname}:{self.current_directory}$ "

    def run(self):
        """Основной цикл эмулятора."""
        try:
            while True:
                command = input(self.prompt())
                result = self.run_command(command)
                if result:
                    print(result)
        except KeyboardInterrupt:
            self.exit()

    def run_command(self, command):
        """Обрабатывает ввод пользователя и возвращает результат команды."""
        if command.startswith('ls'):
            return self.ls()
        elif command.startswith('cd'):
            self.cd(command.split(' ')[1] if len(command.split()) > 1 else '/')
            return None
        elif command == 'exit':
            self.exit()
        elif command.startswith('rev'):
            _, file = command.split(' ')
            return self.rev(file)
        elif command == 'whoami':
            return self.whoami()
        else:
            return f"Команда '{command}' не поддерживается."

    def cd(self, path):
        """Команда cd."""
        new_dir = os.path.join(self.current_directory, path) if not path.startswith('/') else path
        abs_path = os.path.join(self.fs_root, new_dir.strip('/'))
        
        if os.path.isdir(abs_path):
            self.current_directory = new_dir if new_dir.startswith('/') else '/' + new_dir.strip('/')
        else:
            print(f"Путь '{path}' не существует.")
        
    def ls(self):
        """Команда ls."""
        path = os.path.join(self.fs_root, self.current_directory.strip('/'))
        if os.path.exists(path):
            files = os.listdir(path)
            return '  '.join(files)  # Возвращаем список файлов
        else:
            return f"Путь '{self.current_directory}' не существует."

    def rev(self, file):
        """Команда rev - выводит содержимое файла в обратном порядке."""
        file_path = os.path.join(self.fs_root, self.current_directory.strip('/'), file.strip('/'))
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                return content[::-1]  # Возвращаем перевернутое содержимое
        else:
            return f"Файл '{file}' не существует."

    def whoami(self):
        """Команда whoami - выводит имя текущего пользователя."""
        return getpass.getuser()

    def exit(self):
        """Команда exit."""
        print("Выход из эмулятора.")
        sys.exit(0)


def generate_files():
    """Функция для генерации всех нужных файлов в директории."""
    
    # Creating virtual filesystem
    virtual_fs_dir = 'virtual_fs'
    if not os.path.exists(virtual_fs_dir):
        os.makedirs(virtual_fs_dir)
        with open(os.path.join(virtual_fs_dir, 'file1.txt'), 'w') as f:
            f.write("Это содержимое файла 1.")
        with open(os.path.join(virtual_fs_dir, 'file2.txt'), 'w') as f:
            f.write("Это содержимое файла 2.")
        os.makedirs(os.path.join(virtual_fs_dir, 'subdir'))
        with open(os.path.join(virtual_fs_dir, 'subdir', 'file3.txt'), 'w') as f:
            f.write("Это содержимое файла в поддиректории.")
        
    # Tar archive generation
    fs_tar = 'virtual_fs.tar'
    with tarfile.open(fs_tar, 'w') as tar:
        tar.add(virtual_fs_dir, arcname=os.path.basename(virtual_fs_dir))

    print(f"Создан архив виртуальной файловой системы: {fs_tar}")

    # Startup script generation
    startup_script = 'startup_script.sh'
    with open(startup_script, 'w') as f:
        f.write('ls\n')
        f.write('cd subdir\n')
        f.write('ls\n')
    
    print(f"Создан стартовый скрипт: {startup_script}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор shell для UNIX-подобных систем.")
    parser.add_argument("--hostname", required=True, help="Имя компьютера для показа в приглашении к вводу.")
    parser.add_argument("--filesystem", required=True, help="Путь к архиву виртуальной файловой системы.")
    parser.add_argument("--startup_script", help="Путь к стартовому скрипту для выполнения команд.")
    parser.add_argument("--generate_files", action="store_true", help="Сгенерировать все необходимые файлы в текущей директории.")

    args = parser.parse_args()

    if args.generate_files:
        generate_files()
    else:
        shell = ShellEmulator(args.hostname, args.filesystem, args.startup_script)
        shell.run()
