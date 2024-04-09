# RanobeHubParser
**RanobeHubParser** – это кроссплатформенный скрипт для получения данных с сайта [RanobeHub](https://ranobehub.org/) в формате JSON. Он позволяет записать всю информацию о конкретной манге, а также её главах и содержании глав.

## Порядок установки и использования
1. Загрузить последний релиз. Распаковать.
2. Установить Python версии не старше 3.10. Рекомендуется добавить в PATH.
3. В среду исполнения установить следующие пакеты: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/), [dublib](https://github.com/DUB1401/dublib).
```
pip install BeautifulSoup4
pip install dublib
```
Либо установить сразу все пакеты при помощи следующей команды, выполненной из директории скрипта.
```
pip install -r requirements.txt
```
4. Настроить скрипт путём редактирования _Settings.json_.
5. Открыть директорию со скриптом в терминале. Можно использовать метод `cd` и прописать путь к папке, либо запустить терминал из проводника.
6. Указать для выполнения главный файл скрипта `main.py`, передать ему команду вместе с параметрами, нажать кнопку ввода и дождаться завершения работы.

# Консольные команды
```
collect [FLAGS] [KEYS]
```
Собирает коллекцию из алиасов новелл, соответствующих набору фильтров в каталоге [RanobeHub](https://ranobehub.org/). Собранные алиасы добавляются в файл _Collection.txt_ в порядке убывания даты обновления. По умолчанию собирает алиасы всех новелл на сайте.

> [!IMPORTANT]  
> Фильтр _**page**_ зарезервирован сборщиком и не может быть использован.

**Список специфических флагов:**
* _**-f**_ – удаляет содержимое файла коллекции перед записью.

**Список специфических ключей:**
* _**--filters**_ – задаёт набор фильтров из адресной строки, разделённых амперсантом `&` и заключённых в кавычки `"`.
___
```
getcov [NOVEL_SLUG*] [FLAGS]
```
Загружает обложки конкретной новеллы, алиас которой передан в качестве аргумента.

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек.
___
```
parse [TARGET*] [FLAGS] [KEYS]
```
Проводит парсинг новеллы с указанным алиасом в JSON формат и загружает её обложки. В случае, если файл новеллы уже существует, дополнит его новыми данными. 

**Описание позиций:**
* **TARGET** – задаёт цель для парсинга. Обязательная позиция.
	* Аргумент – алиас новеллы для парсинга.
	* Флаги:
		* _**-collection**_ – указывает, что список новелл для парсинга необходимо взять из файла _Collection.txt_;
		* _**-local**_ – указывает для парсинга все локальные файлы.
		
**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек и существующих JSON файлов.

**Список специфических ключей:**
* _**--from**_ – указывает алиас новеллы, с момента обнаружения которой в коллекции необходимо начать парсинг.
___
```
repair [FILENAME*] [CHAPTER_ID*]
```
Обновляет и перезаписывает сведения о контенте конкретной главы в локальном файле.

**Описание позиций:**
* **FILENAME** – название локального файла, в котором необходимо исправить контент. Обязательная позиция.
	* Аргумент – имя файла в директории тайтлов. Можно указывать как с расширением, так и без него.
* **CHAPTER_ID** – ID главы в локальном файле, контент которой необходимо заново получить с сервера. Обязательная позиция.
	* Ключи:
		* _**--chapter**_ – указывает ID главы.

# Settings.json
```JSON
"noveld-directory": ""
```
Указывает, куда сохранять JSON-файлы тайтлов. При пустом значении будет создана папка _Novels_ в исполняемой директории скрипта.
___
```JSON
"images-directory": ""
```
Указывает, куда сохранять иллюстрации новелл. При пустом значении будет создана папка _Images_ в исполняемой директории скрипта.
___
```JSON
"covers-directory": ""
```
Указывает, куда сохранять обложки тайтлов. При пустом значении будет создана папка _Covers_ в исполняемой директории скрипта.
___
```JSON
"mount-images": ""
```
Указывает путь, который будет добавлен к ссылкам на иллюстрации.
___
```JSON
"use-id-instead-slug": true
```
При включении данного параметра файлы JSON, директория обложек и каталог иллюстраций новеллы будут названы по ID произведения, а не по алиасу.
___
```JSON
"prettifier": true
```
Включает набор готовых решений для повышения качества получаемого контента:
* очистка небуквенных абзацев в конце глав;
* удаление дублирующихся названий из текста глав;
* замена трёх точек символом многоточия в названиях глав;
* удаление лишних точек из названий глав;
* добавление 12-ти символов `_` между текстом главы и сносками.
___
```JSON
"filters": false
```
Включает удаление подстрок из текста глав по регулярным выражениям из файла _Filters.txt_. В файле поддерживается комментирование при помощи спецсимвола `#`.
___
```JSON
"proxy": {
	"enable": false,
	"host": "",
	"port": "",
	"login": "",
	"password": ""
}
```
Указывает HTTP-прокси для выполнения запросов.
___
```JSON
"delay": 3
```
Устанавливает интервал в секундах между последовательными запросами к серверу.

_Copyright © DUB1401. 2024._
