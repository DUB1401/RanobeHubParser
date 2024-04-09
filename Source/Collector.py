from dublib.WebRequestor import WebRequestor
from dublib.Methods import Cls
from time import sleep

import logging
import json

class Collector:

	def __ReadCollection(self) -> list[str]:
		# Коллекция.
		Collection = list()

		# Если файл коллекции существует.
		if os.path.exists("Collection.txt"):

			# Чтение содржимого файла.
			with open("Collection.txt", "r") as FileReader:
				# Буфер чтения.
				Bufer = FileReader.read().split("\n")
				
				# Для каждой строки.
				for String in Bufer:
					# Если строка не пуста, поместить её в список алиасов.
					if String.strip() != "": Collection.append(String.strip())

		return Collection

	def __SaveCollection(self, Collection: list[str]):

		# Открытие потока записи.
		with open("Collection.txt", "w") as FileWriter:
			# Запись каждого алиаса в файл.
			for Slug in Collection: FileWriter.write(Slug + "\n")
    
	def __init__(self,  Settings: dict, Requestor: WebRequestor):

		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Глобальные настройки.
		self.__Settings = Settings.copy()
		# Обработчик навигации.
		self.__Requestor = Requestor
		
	def collect(self, filters: str | None = None, force_mode: bool = False) -> list:
		# Формирование фильтров.
		if filters: filters = "&" + filters
		# Номер текущей страницы.
		CurrentPage = 1
		# Номер последней страницы.
		LastPage = None
		# Список алиасов.
		Collection = self.__ReadCollection() if force_mode else list()
		# Режим коллекционирования.
		ForceMode = "Force mode: " + ("ON" if force_mode else "OFF")

		# Пока не достигнута последняя страница.
		while LastPage == None or CurrentPage < LastPage:
			# Очистка консоли.
			Cls()
			# Вывод в консоль: прогресс.
			print(f"{ForceMode}\nCollecting: {CurrentPage} / {LastPage}" if LastPage else f"{ForceMode}\nCollecting: {CurrentPage}")
			# Запись в лог сообщения: страница просканирована.
			logging.info(f"Page {CurrentPage} collected.")
			# Выполнение запроса.
			Response = self.__Requestor.get(f"https://ranobehub.org/api/search?page={CurrentPage}&take=40{filters}")

			# Если запрос успешен.
			if Response.status_code == 200:
				# Преобразование в JSON.
				Data = json.loads(Response.text)
				# Обновление записи о последней странице.
				LastPage = Data["pagination"]["lastPage"]

				# Для каждой новеллы.
				for Item in Data["resource"]:
					# Получение алиаса.
					Slug = Item["url"].split("/")[-1]
					# Запись алиаса.
					Collection.append(Slug)

			else:
				# Запись в лог ошибки: не удалось получить страницу каталога.
				logging.error("Unable to load catalog page.")

			# Инкремент текущей страницы.
			CurrentPage += 1
			# Если не достигнута последняя страница, выждать интервал.
			if CurrentPage < LastPage: sleep(self.__Settings["delay"])

		# Запись в лог сообщения: количество элементов в коллекции.
		logging.info("Total slugs count in collection: " + str(len(Collection)) + ".")
		# Сохранение коллекции.
		self.__SaveCollection(Collection)