import pyautogui
import os
import datetime
import subprocess

DEVICE_DIRS = os.listdir(r'c:\ingi\cache\static\devices')  # Каталог с папками устройств
SCREEN_DIR = r'c:\ingi\screen'  # Каталог для сохранения скринов
STATUS_LOG = r'c:\ingi\cache\logs\screen.log'  # Файл в который пишутся статусы
FIX_LOG = r'c:\ingi\cache\logs\fix.log'  # Лог выполнения фикса воспроизведения

# Получаем время срабатывания скрипта, формируем имя для файла скриншота и сохраняем его
screen_time = datetime.datetime.now()
screen_name = 'scr_' + screen_time.strftime('%Y-%m-%d_%H-%M-%S') + '.png'
screenshot = pyautogui.screenshot()
screenshot.save(SCREEN_DIR + '\\' + screen_name)


# Функция побайтового сравнения двух файлов. Возвращает Истина/Ложь
def validate_file_content(file1, file2):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        content1 = f1.read()
        content2 = f2.read()
    return content1 == content2


# Получаем список с именами файлов скриншотов в папке
screen_files = os.listdir(SCREEN_DIR)

# Проверяем количество файлов, если их больше 2х, то вызываем функцию сравнения беря 2 последних имени из массива
# Результат пишем в файл статуса
if len(screen_files) > 2:
    result = validate_file_content(SCREEN_DIR + '\\' + screen_files[-2], SCREEN_DIR + '\\' + screen_files[-1])
    with open(STATUS_LOG, 'a') as lf:
        if result:
            lf.write('SAME\n')
            lf.close()
        else:
            lf.write('DIFFERENT\n')
            lf.close()

# Читаем файл статусов построчно, берем последние 3 строки и считаем сколько раз в них встречается значение одинаковых скриншотов
# Если больше или равно 3м - чистим кэш и запускаем батник синхронизации
# Записываем событие починки в лог
with open(STATUS_LOG, 'r') as lfr:
    result_list = lfr.readlines()
    if len(result_list) > 3:
        s = result_list[-3:].count('SAME\n')
        if s >= 3:
            for directory in DEVICE_DIRS:
                devices = os.listdir('c:\\ingi\\cache\\static\\devices\\' + directory)
                print(devices)
                for files in devices:
                    os.remove('c:\\ingi\\cache\\static\\devices\\' + directory + '\\' + files)
            subprocess.call('c:\\ingi\\cmd\\run_cron.bat')
            with open(FIX_LOG, 'a') as fl:
                fl.write(screen_time.strftime('%Y-%m-%d %H:%M:%S') + ' FIXED\n')
                fl.close()

# Чистим файлы скриншотов если их больше 5
if len(screen_files) > 5:
    for x in range(0, len(screen_files) - 5):
        os.remove(SCREEN_DIR + '\\' + screen_files[x])

# Чистим файл статусов, чтобы не разрастался
with open(STATUS_LOG, 'r') as fs:
    lines = fs.readlines()
    fs.close()
    if len(lines) > 20:
        with open(STATUS_LOG, 'w') as fs2:
            fs2.writelines(lines[-10:])
            fs2.close()
