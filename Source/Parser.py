from dublib.Methods import CheckForCyrillicPresence, Cls, ReadJSON, RemoveRecurringSubstrings, WriteJSON
from dublib.Methods import IsNotAlpha, Zerotify
from dublib.WebRequestor import WebRequestor
from dublib.Polyglot import HTML
from bs4 import BeautifulSoup
from time import sleep

import requests
import logging
import os
import re

class Parser:
	
	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __DownloadImage(self, Link: str, ChapterID: int | str, ImageID: str):
		# Директория загрузки.
		Directory = self.__Settings["images-directory"] + f"/{self.__ID}/{ChapterID}"
		# Если директория не существует, создать.
		if not os.path.exists(Directory): os.makedirs(Directory)
		# Список файлов в папке.
		Files = os.listdir(self.__Settings["images-directory"] + f"/{self.__ID}/{ChapterID}")
		# Для каждого названия файла удалить расширение.
		for Index in range(len(Files)): Files[Index] = "".join(Files[Index].split(".")[:-1])
		
		# Если файл ещё не загружен.
		if ImageID not in Files:

			try:
				# Выполнение запроса.
				Response = requests.get(Link)
		
				# Если запрос успешен.
				if Response.status_code == 200:

					# Открытие потока записи.
					with open(f"{Directory}/{ImageID}.webp", "wb") as FileWriter:
						# Запись файла изображения.
						FileWriter.write(Response.content)

					# Запись в лог сообщения: иллюстрация загружена.
					logging.info(f"Novel: \"{self.__Slug}\". Chapter: {ChapterID}. Image downloaded: {ImageID}.")
		
				else:
					# Запись в лог ошибки: не удалось скачать иллюстрацию.
					logging.error(f"Novel: \"{self.__Slug}\". Chapter: {ChapterID}. Unable to download image: \"{Link}\". Response code: {Response.status_code}.")
				
			except:
				# Запись в лог ошибки: не удалось скачать иллюстрацию из-за некорректной ссылки.
				logging.error(f"Novel: \"{self.__Slug}\". Chapter: {ChapterID}. Incorrect link to image.")
				
		else:
			# Запись в лог сообщения: иллюстрация уже загружена.
			logging.info(f"Novel: \"{self.__Slug}\". Chapter: {ChapterID}. Image already exists: {ImageID}.")
	
	def __FilterStringData(self, Data: str):
		# Для каждого регулярного выражения удалить все вхождения.
		for Regex in self.__Filters: Data = re.sub(Regex, "", Data)

		return Data
	
	def __GetNumberFromString(self, String: str) -> int | float | None:
		# Поиск первого числа.
		Result = re.search("\d+(\.\d+)?", String)
		# Число.
		Number = None
		
		# Если удалось найти число.
		if Result:
			# Получение строки.
			Result = Result[0]
			
			# Если число содержит точку.
			if "." in Result:
				# Преобразовать в число с плавающей запятой.
				Number = float(Result)
				
			else:
				# Преобразовать в число.
				Number = int(Result)

		return Number
	
	def __Merge(self):
		# Чтение локального файла.
		Local = ReadJSON(self.__Settings["novels-directory"] + f"/{self.__UsedName}.json")
		# Локальные определения глав.
		LocalChapters = dict()
		# Количество дополненных глав.
		MergedChaptersCount = 0
		
		# Для каждой главы.
		for Chapter in Local["chapters"][str(self.__ID)]:
			# Запись информации об абзацах.
			LocalChapters[Chapter["id"]] = Chapter["paragraphs"]
			
		# Для каждой главы.
		for ChapterIndex in range(0, len(self.__Novel["chapters"][str(self.__ID)])):
					
			# Если для главы с таким ID найдены абзацы.
			if self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["id"] in LocalChapters.keys():
				# Запись информации об абзацах.
				self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["paragraphs"] = LocalChapters[self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["id"]]
				# Инкремент количества дополненных глав.
				MergedChaptersCount += 1
						
		# Запись в лог сообщения: количество дополненных глав.
		logging.info(f"Novel: \"{self.__Slug}\". Merged chapters: {MergedChaptersCount}.")

	def __ReadFilters(self) -> list[str]:
		# Список регулярных выражений.
		RegexList = list()

		# Если файл фильтров существует.
		if os.path.exists("Filters.txt"):

			# Чтение содржимого файла.
			with open("Filters.txt", "r") as FileReader:
				# Буфер чтения.
				Bufer = FileReader.read().split("\n")
				
				# Для каждой строки.
				for String in Bufer:
					# Если строка не пуста и не комментарий, поместить её в список регулярных выражений.
					if String.strip() != "" and not String.startswith("#"): RegexList.append(String.strip())

		return RegexList

	def __RemoveBaseNumbers(self):
		# Для каждой главы удалить порядковый номер.
		for ChapterIndex in range(len(self.__Novel["chapters"][str(self.__ID)])): del self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["BASE_NUMBER"]

	#==========================================================================================#
	# >>>>> МЕТОДЫ ПАРСИНГА <<<<< #
	#==========================================================================================#
	
	def __Amend(self):
		# Количество дополненных глав.
		AmendedChaptersCount = 0 
				
		# Для каждой главы.
		for ChapterIndex in range(len(self.__Novel["chapters"][str(self.__ID)])):
			# Очистка консоли.
			Cls()
			# Вывод в консоль: сообщение из внешнего обработчика и прогресс.
			print(self.__Message + "\n" + f"Amending: " + str(ChapterIndex + 1) + " / " + str(len(self.__Novel["chapters"][str(self.__ID)])))
			
			# Если глава не имеет абзацев и не является платной.
			if self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["paragraphs"] == [] and not self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["is-paid"]:
				# ID главы.
				ChapterID = self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["id"]
				# Номер тома.
				Volume = self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["volume"]
				# Номер главы.
				BaseNumber = self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["BASE_NUMBER"]
				# Инкремент количества дополненных глав.
				AmendedChaptersCount += 1
				# Список абзацев.
				ParagraphsList = self.__GetChapterParagraphs(ChapterID, Volume, BaseNumber)
				# Сохранение контента.
				self.__Novel["chapters"][str(self.__ID)][ChapterIndex]["paragraphs"] = ParagraphsList
				# Запись в лог сообщения: глава дополнена контентом.
				if len(ParagraphsList) > 0: logging.info(f"Novel: \"{self.__Slug}\". Chapter: {ChapterID}. Amended.")
				# Выжидание интервала.
				sleep(self.__Settings["delay"])

		# Удаление порядкового номера глав.
		self.__RemoveBaseNumbers()

		# Запись в лог сообщения: количество дополненных глав.
		logging.info(f"Novel: \"{self.__Slug}\". Chapters amended: {AmendedChaptersCount}.")
	
	def __DetermineChapterType(self, ChapterName: str) -> str:
		# Тип главы.
		Type = "chapter"
		# Приведение главы к нижнему регистру.
		ChapterName = ChapterName.lower()

		# Определение типа главы.
		if ChapterName.startswith("пролог"): Type = "prologue"
		if ChapterName.startswith("эпилог"): Type = "epilogue"
		if ChapterName.startswith("начальные иллюстрации") or ChapterName.startswith("иллюстрации"): Type = "illustrations"
		if ChapterName.startswith("экстра") or ChapterName.startswith("побочная история"): Type = "extra"
		if ChapterName.startswith("послесловие"): Type = "afterword"

		return Type

	def __GetAuthor(self, Soup: BeautifulSoup) -> str | None:
		# Поиск первого контейнера с автором.
		AuthorContainer = Soup.find("div", {"class": "book-author"})
		# Автор.
		Author = None
		# Если удалось найти контейнер автора, получить ник.
		if AuthorContainer: Author = AuthorContainer.get_text().replace("(Автор)", "").strip().split("\n")[0]
		
		return Author	
	
	def __GetCovers(self, Soup: BeautifulSoup) -> list:
		# Поиск контейнера обложек.
		CoversContainer = Soup.find("div", {"class": "sticky"}).find("div", {"class": "poster-slider"})
		# Поиск всех изображений.
		CoversBlocks = CoversContainer.find_all("img")
		# Список обложек.
		Covers = list()
		
		# Для каждого изображения.
		for Block in CoversBlocks:
			# Буфер изображения.
			Buffer = {
				"link": Block["data-src"],
				"filename": Block["data-src"].split("/")[-1] + ".webp",
				"width": None,
				"height": None
			}
			# Добавление обложки в список.
			Covers.append(Buffer)
			
		return Covers
	
	def __GetChapterParagraphs(self, ChapterID: int | str, Volume: int, BaseNumber: int):
		# Запрос главы.
		Response = self.__Requestor.get(f"https://ranobehub.org/ranobe/{self.__ID}/{Volume}/{BaseNumber}")
		# Буфер абзацев.
		Buffer = list()

		# Если запрос успешен.
		if Response.status_code == 200 and "Слишком много запросов" not in str(Response.text):
			# Парсинг страницы главы.
			Soup = BeautifulSoup(Response.text, "html.parser")
			# Поиск контейнера главы.
			Container = Soup.find("div", {"data-container": str(ChapterID)})
			
			# Если есть перевод.
			if Container != None:
				# Поиск всех вложенных тегов.
				Paragraphs = Container.find_all(["p", "blockquote"], recursive = False)
				# Поиск контейнера сносок.
				Notes = Container.find_all("li")
				# Индекс сноски внизу главы.
				NoteIndex = 1
				# Индекс сноски в тексте главы.
				MarkIndex = 1

				# Для каждого параграфа.
				for Paragraph in Paragraphs:
					# Если абзац имеет выравнивание по ширине строки, удалить стиль.
					if Paragraph.has_attr("style") and Paragraph["style"] == "text-align:justify;": del Paragraph["style"]
					# Поиск ссылок в абзаце.
					Links = Paragraph.find_all("a")
					
					# Если ссылки найдены.
					if Links: 

						# Для каждой ссылки.
						for Link in Links:

							# Если ссылка является сноской.
							if Link.get_text().strip() == "*":
								# Удаление сноски.
								Link.replace_with(f" [{MarkIndex}]")
								# Инкремент индекса сноски.
								MarkIndex += 1

					# Если в абзаце есть изображение.
					if Paragraph.find("img"):
						# Поиск всех изображений в абзаце.
						Images = Paragraph.find_all("img")

						# Для каждого изображения.
						for Image in Images:

							# Если иллюстрация имеет ID.
							if Image.has_attr("data-media-id"):
								# ID иллюстрации.
								ImageID = Image["data-media-id"]
								# Удаление идентифицирующего атрибута.
								del Image["data-media-id"]
								# Перезапись URI иллюстрации.
								Image["src"] = self.__Settings["mount-images"].rstrip("/\\") + f"/{self.__ID}/{ChapterID}/{ImageID}.webp"
								# Скачивание иллюстрации.
								self.__DownloadImage(f"https://ranobehub.org/api/media/{ImageID}", ChapterID, ImageID)

						# Запись абзаца.
						Buffer.append(str(Paragraph))

					# Если в абзаце есть окно.
					elif "<blockquote" in str(Paragraph):
						# Запись абзаца.
						Buffer.append("<p>" + str(Paragraph) + "</p>")
					
					# Если абзац содержит текст.
					elif Paragraph.get_text().strip() != "":
						# Текст абзаца.
						Line = self.__FilterStringData(str(Paragraph))
						# Парсинг тегов.
						Line = HTML(Line)
						Line.replace_tag("em", "i")
						Line.replace_tag("strong", "b")
						Line.remove_tags(["br"])
						# Сохранение текста.
						Buffer.append(Line.text)
						
				# Если вклюбчен режим улучшения и есть сноски, добавить разделитель.
				if self.__Settings["prettifier"] and Notes: Buffer.append("<p>____________</p>")

				# Для каждой сноски.
				for Note in Notes:
					# Текст заметки.
					NoteText = self.__FilterStringData(Note.get_text().strip(" ↑\t\n").capitalize())
					# Дополнение текста главы сноской.
					Buffer.append(f"<p>{NoteIndex}. {NoteText}</p>")
					# Инкремент индекса сноски.
					NoteIndex += 1

				# Если включен форматировщик.
				if self.__Settings["prettifier"]:
					# Пока в последнем абзаце отсутсвуют буквенные символы, удалять последний абзац.
					while len(Buffer) > 0 and not re.search("[a-zA-ZА-я_]{3,}", Buffer[-1]): Buffer.pop()
					# Если в первом абзаце присутствует номер главы, удалить его.
					if len(Buffer) > 0 and re.search("глава \d+", Buffer[0], re.IGNORECASE) or len(Buffer) > 0 and re.search("^эпилог|пролог|экстра|начальные иллюстрации", Buffer[0], re.IGNORECASE): Buffer.pop(0)

			else:
				# Запись в лог предупреждения: глава не содержит перевод.
				logging.warning(f"Novel: \"{self.__Slug}\". Chapter: {ChapterID}. No translation.")

		else:
			# Запись в лог ошибки: не удалось получить содержимое главы.
			logging.error(f"Novel: \"{self.__Slug}\". Chapter: {ChapterID}. Unable to load content.")

		return Buffer

	def __GetChapters(self) -> list[dict]:
		# Запрос контента.
		Response = self.__Requestor.get(f"https://ranobehub.org/api/ranobe/{self.__ID}/contents")
		# Список глав.
		Chapters = list()

		# Если запрос успешен.
		if Response.status_code == 200:
			# Получение томов.
			Volumes = Response.json["volumes"]

			# Для каждого тома.
			for Volume in Volumes:
				# Номер тома.
				VolumeNumber = Volume["num"]

				# Для каждой главы в томе.
				for Chapter in Volume["chapters"]:
					# Часть с номером главы.
					ChapterNameNumberPart = re.search("( )?\d+(\.\d+)?( )?(. )?", Chapter["name"], re.IGNORECASE)
					# Номер главы.
					ChapterNumber = None
					# Тип главы.
					Type = self.__DetermineChapterType(Chapter["name"])
					
					# Если найден номер главы.
					if ChapterNameNumberPart:
						# Удаление номера из названия.
						Chapter["name"] = Chapter["name"].split(ChapterNameNumberPart[0])[-1]
						# Если тип – глава, получить номер.
						if Type == "chapter": ChapterNumber = self.__GetNumberFromString(ChapterNameNumberPart[0])

					else:
						# Если тип – глава, получить номер.
						if Type == "chapter": ChapterNumber = self.__GetNumberFromString(Chapter["name"])

					# Обнуление названия главы.
					Chapter["name"] = Zerotify(Chapter["name"])

					# Если включено улучшение названия и оное определено.
					if self.__Settings["prettifier"] and Chapter["name"]:
						# Замена трёх точек символом многоточия.
						Chapter["name"].replace("...", "…")
						# Удаление повторяющихся символов многоточия.
						Chapter["name"] = RemoveRecurringSubstrings(Chapter["name"], "…")
						# Удаление краевых символов.
						Chapter["name"] = Chapter["name"].strip(".")

					# Буфер главы.
					Buffer = {
						"id": Chapter["id"],
						"volume": VolumeNumber,
						"number": ChapterNumber,
						"BASE_NUMBER": Chapter["num"],
						"name": Chapter["name"],
						"type": Type,
						"is-paid": False,
						"translator": None,
						"paragraphs": []
					}
					# Запись буфера.
					Chapters.append(Buffer)
			
			# Запись количества глав.
			self.__Novel["branches"][0]["chapters-count"] = len(Chapters)

		else:
			# Запись в лог критической ошибки: не удалось получить информацию о главах.
			logging.critical(f"Novel: \"{self.__Slug}\". Unable to request content.")
		
		return Chapters
	
	def __GetDescription(self, Soup: BeautifulSoup) -> str | None:
		# Поиск блока описания.
		DescriptionBlock = Soup.find("div", {"class": "book-description"})
		# Описание.
		Description = None
		
		# Если блок описания найден.
		if DescriptionBlock:
			# Поиск всех абзацев.
			Paragraphs = DescriptionBlock.find_all("p")
			# Приведение описания к строковому типу.
			Description = ""
			
			# Для каждого абзаца добавить строку описания.
			for p in Paragraphs: Description += HTML(p.get_text()).plain_text.strip() + "\n"
				
		# Удаление повторяющихся и концевых символов новой строки.
		Description = RemoveRecurringSubstrings(Description, "\n")
		Description = Description.strip("\n")
		
		return Description

	def __GetGenres(self, Soup: BeautifulSoup) -> list[str]:
		# Список жанров.
		Genres = list()
		# Поиск контейнера с данными.
		DataContainer = Soup.find("div", {"id": "section-common"})
		# Поиск всех блоков данных.
		DataBlocks = DataContainer.find_all("div", {"class": "book-meta-row"})
		# Строка жанров.
		GenresLinks = None

		# Для каждого блока.
		for Block in DataBlocks: 
			
			# Если блок содержит нужные данные.
			if "Жанр" in str(Block):
				# Поиск ссылок на жанры.
				GenresLinks = Block.find_all("a")
				# Для каждой ссылки записать название жанра.
				for Link in GenresLinks: Genres.append(Link.get_text().strip().lower())
			
		return Genres

	def __GetOriginalLanguage(self, Soup: BeautifulSoup) -> str | None:
		# Определения кодов языков по стандарту ISO 639-1.
		LanguagesDeterminations = {
			"Китай": "ZH",
			"Корея": "KO",
			"Япония": "JA",
			"США": "EN"
		}
		# Поиск контейнера с данными.
		DataContainer = Soup.find("div", {"id": "section-common"})
		# Поиск всех блоков данных.
		DataBlocks = DataContainer.find_all("div", {"class": "book-meta-row"})
		# Оригинальный язык.
		Language = None
		# Страна.
		Country = None

		# Для каждого блока.
		for Block in DataBlocks: 
			
			# Если блок содержит нужные данные.
			if "Страна" in str(Block):
				# Получение названия страны.
				Country = Block.get_text().replace("Страна", "").strip()
		
		# Если для страны определён язык.
		if Country in LanguagesDeterminations.keys(): Language = LanguagesDeterminations[Country]

		return Language

	def __GetNovel(self) -> bool:
		# Состояние: успешен ли запрос.
		IsSuccess = False
		# Выполнение запроса.
		Response = self.__Requestor.get(f"https://ranobehub.org/ranobe/{self.__Slug}")
		# Если запрос успешен.
		if Response.status_code == 200:
			# Парсинг кода страницы.
			Soup = BeautifulSoup(Response.text, "html.parser")
			# Парсинг названий.
			Names = self.__GetNames(Soup)
			# Заполнение данных новеллы.
			self.__Novel["covers"] = self.__GetCovers(Soup)
			self.__Novel["ru-name"] = Names["ru"]
			self.__Novel["en-name"] = Names["en"]
			self.__Novel["another-names"] = Names["another"]
			self.__Novel["author"] = self.__GetAuthor(Soup)
			self.__Novel["publication-year"] = self.__GetPublicationYear(Soup)
			self.__Novel["description"] = self.__GetDescription(Soup)
			self.__Novel["original-language"] = self.__GetOriginalLanguage(Soup)
			self.__Novel["status"] = self.__GetStatus(Soup)
			self.__Novel["genres"] = self.__GetGenres(Soup)
			self.__Novel["tags"] = self.__GetTags(Soup)
			self.__Novel["chapters"][str(self.__ID)] = self.__GetChapters()
			# Переключение состояния.
			IsSuccess = True
			
		return IsSuccess
	
	def __GetNames(self, Soup: BeautifulSoup) -> dict:
		# Поиск заголовка альтернативного названия.
		AlternativeName = Soup.find("h3")
		# Словарь названий.
		Names = {
			"ru": Soup.find("h1").get_text().strip(),
			"en": Soup.find("h2").get_text().strip(),
			"another": AlternativeName.get_text().strip() if AlternativeName else []
		}

		return Names
	
	def __GetPublicationYear(self, Soup: BeautifulSoup) -> int | None:
		# Поиск контейнера с данными.
		DataContainer = Soup.find("div", {"id": "section-common"})
		# Поиск всех блоков данных.
		DataBlocks = DataContainer.find_all("div", {"class": "book-meta-row"})
		# Год публикации.
		Year = None
		
		# Для каждого блока.
		for Block in DataBlocks: 
			
			# Если блок содержит нужные данные.
			if "Год выпуска" in str(Block):
				
				try:
					# Получение данных.
					Year = int(Block.get_text().replace("Год выпуска", "").strip())
				
				except ValueError: pass
			
		return Year
	
	def __GetStatus(self, Soup: BeautifulSoup) -> str:
		# Определения статусов.
		Statuses = {
			"В процессе": "ONGOING",
			"Неизвестно": "UNKNOWN",
			"Заморожено": "ABANDONED",
			"Завершено": "COMPLETED"
		}
		# Статус.
		Status = "UNKNOWN"
		# Поиск контейнера с данными.
		DataContainer = Soup.find("div", {"id": "section-common"})
		# Поиск всех блоков данных.
		DataBlocks = DataContainer.find_all("div", {"class": "book-meta-row"})
		# Описание статуса.
		StatusLine = None

		# Для каждого блока.
		for Block in DataBlocks: 
			
			# Если блок содержит нужные данные.
			if "Статус перевода" in str(Block):
				# Получение данных.
				StatusLine = Block.get_text().replace("Статус перевода", "").strip()

		# Если строка статуса определена, установить статус.
		if StatusLine in Statuses.keys(): Status = Statuses[StatusLine]
			
		return Status
	
	def __GetTags(self, Soup: BeautifulSoup) -> list:
		# Список тегов.
		Tags = list()
		# Поиск контейнера с данными.
		DataContainer = Soup.find_all("div", {"class": "book-tags"})[-1]
		# Поиск спойлера.
		DataSpoiler = DataContainer.find("div", {"class": "__spoiler_new display-none"})
		# Поиск всех ссылок на теги в контейнере или спойлере.
		DataBlocks = DataSpoiler.find_all("a") if DataSpoiler else DataContainer.find_all("a")

		# Для каждой ссылки..
		for Block in DataBlocks: 
			# Запись названия тега.
			Tags.append(Block.get_text().strip().lower())
			
		return Tags

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, settings: dict, requestor: WebRequestor, slug: int | str, force_mode: bool = True, amend: bool = True, message: str = ""):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Список фильтров на основе регулярных выражений.
		self.__Filters = self.__ReadFilters()
		# Глоабльные настройки.
		self.__Settings = settings
		# Менеджер запросов.
		self.__Requestor = requestor
		# Алиас новеллы.
		self.__Slug = slug
		# ID новеллы.
		self.__ID = int(self.__Slug.split("-")[0])
		# Используемое имя тайтла.
		self.__UsedName = str(self.__ID) if settings["use-id-instead-slug"] else slug
		# Состояние: включён ли режим перезаписи.
		self.__ForceMode = force_mode
		# Сообщение из внешних обработчиков.
		self.__Message = message + "Current novel: " + str(self.__Slug) + "\n"
		# Структура новеллы.
		self.__Novel = {
			"format": "dnp-v1",
			"site": "ranobehub.org",
			"id": int(self.__Slug.split("-")[0]),
			"slug": self.__Slug,
			"covers": [],
			"ru-name": None,
			"en-name": None,
			"another-names": [],
			"author": None,
			"publication-year": None,
			"age-rating": None,
			"description": None,
			"original-language": None,
			"status": None,
			"is-licensed": False,
			"series": [],
			"genres": [],
			"tags": [],
			"branches": [
				{
					"id": self.__ID,
					"chapters-count": 0
				}
			],
			"chapters": {
				str(self.__ID): []
			}
		}
		# Состояние: доступна ли новелла для парсинга.
		self.__IsAccesed = None
		
		#---> Подготовка к парсингу.
		#==========================================================================================#
		# Очистка консоли.
		Cls()
		# Вывод в консоль: базовое сообщение.
		print(self.__Message)
		# Запись в лог сообщения: старт парсинга.
		logging.info(f"Novel: \"{self.__Slug}\". Parsing...")
		
		#---> Получение данных о новелле.
		#==========================================================================================#
		# Парсинг страницы новеллы.
		self.__IsAccesed = self.__GetNovel()
		
		# Если удалось спарсить страницу новеллы и указано дополнить главы.
		if self.__IsAccesed:
			
			# Если уже существует описательный файл и режим перезаписи отключен.
			if os.path.exists(self.__Settings["novels-directory"] + f"/{self.__UsedName}.json") and not force_mode:
				# Запись в лог сообщения: информация будет перезаписана.
				logging.info(f"Novel: \"{self.__Slug}\". Local JSON already exists. Merging...")
				# Слияние источников.
				self.__Merge()
				
			# Если уже существует описательный файл и режим перезаписи включен.
			elif os.path.exists(self.__Settings["novels-directory"] + f"/{self.__UsedName}.json") and force_mode:
				# Запись в лог сообщения: информация будет перезаписана.
				logging.info(f"Novel: \"{self.__Slug}\". Local JSON already exists. Will be overwritten...")

			# Дополнение глав.
			if amend: self.__Amend()
		
		else:
			# Запись в лог предупреждения: новелла недоступна.
			logging.warning(f"Novel: \"{self.__Slug}\". Not accesed. Skipped.")

	def download_covers(self):
		# Количество загруженных обложек.
		DownloadedCoversCount = 0
		# Очистка консоли.
		Cls()
		# Вывод в консоль: заголовок парсинга.
		print(self.__Message)
		
		# Для каждой обложки.
		for Cover in self.__Novel["covers"]:
			# Вывод в консоль: загрузка обложки.
			print("Downloading cover: \"" + Cover["link"] + "\"... ", end = "")
			# Директория загрузки.
			Directory = self.__Settings["covers-directory"] + f"/{self.__UsedName}"
			# Если директория не существует, создать.
			if not os.path.exists(Directory): os.makedirs(Directory)
			# Имя файла.
			Filename = Cover["filename"]
			# Состояние: существует ли уже обложка.
			IsAlreadyExists = os.path.exists(f"{Directory}/{Filename}")
			
			# Если обложка не загружена или загружена, но включен режим перезаписи.
			if not IsAlreadyExists or IsAlreadyExists and self.__ForceMode:
				# Выполнение запроса.
				Response = requests.get(Cover["link"])
		
				# Если запрос успешен.
				if Response.status_code == 200:

					# Открытие потока записи.
					with open(f"{Directory}/{Filename}", "wb") as FileWriter:
						# Запись файла изображения.
						FileWriter.write(Response.content)
					
					# Инкремент количества загруженных обложек.
					DownloadedCoversCount += 1
					# Вывод в консоль: загрузка завершена.
					print("Done.")
				
				else:
					# Вывод в консоль: ошибка загрузки.
					print("Failure!")
				
				# Выжидание интервала.
				sleep(self.__Settings["delay"])
				
			else:
				# Вывод в консоль: обложка уже существует.
				print("Already exists.")
					
		# Запись в лог сообщения: старт парсинга.
		logging.info(f"Novel: \"{self.__Slug}\". Covers downloaded: {DownloadedCoversCount}.")

	def repair_chapter(self, chapter_id: int | str):

		# Если новелла доступна.
		if self.__IsAccesed:
			# Приведение ID главы к целочисленному.
			chapter_id = int(chapter_id)
			# Состояние: восстановлена ли глава.
			IsRepaired = False		

			# Для каждой ветви.
			for BranchID in self.__Novel["chapters"].keys():
				
				# Для каждый главы.
				for ChapterIndex in range(0, len(self.__Novel["chapters"][BranchID])):
					
					# Если ID совпадает с искомым.
					if self.__Novel["chapters"][BranchID][ChapterIndex]["id"] == chapter_id:
						# Переключение состояния.
						IsRepaired = True
						# Получение списка абзацев главы.
						Paragraphs = self.__GetChapterParagraphs(
							self.__Novel["chapters"][BranchID][ChapterIndex]["id"],
							self.__Novel["chapters"][BranchID][ChapterIndex]["volume"],
							self.__Novel["chapters"][BranchID][ChapterIndex]["BASE_NUMBER"],
						)
						# Удаление порядкового номера глав.
						self.__RemoveBaseNumbers()
						# Запись в лог сообщения: глава дополнена.
						logging.info(f"Novel: \"{self.__Slug}\". Chapter {chapter_id} repaired.")
						# Запись информации о параграфах.
						self.__Novel["chapters"][BranchID][ChapterIndex]["paragraphs"] = Paragraphs
						
			# Если глава восстановлена.
			if IsRepaired == False:
				# Запись в лог критической ошибки: глава не найдена.
				logging.critical("Title: \"" + self.__Slug + f"\". Chapter {chapter_id} not found.")
				# Выброс исключения.
				raise Exception(f"Chapter with ID {chapter_id} not found.")

	def save(self, filename: str | None = None):
		# Если не указано имя файла, использовать стандартное.
		if not filename: filename = self.__UsedName
		# Если каталог для новелл не существует, создать.
		if os.path.exists(self.__Settings["novels-directory"]) == False: os.makedirs(self.__Settings["novels-directory"])
		# Запись файла.
		WriteJSON(self.__Settings["novels-directory"] + f"/{filename}.json", self.__Novel)