# Архитектура и источники

## Основа

OBS Studio 32.2.2, commit `fc546137470c0f4a5f1493b6e7815545ee1b170b`:
https://github.com/obsproject/obs-studio/tree/fc546137470c0f4a5f1493b6e7815545ee1b170b/plugins/decklink
и каталог `plugins/decklink-output-ui` того же commit.
Сохранены source ID, output ID и имена DLL для совместимости со штатным UI.
Поэтому проект собирает замену штатных модулей, а не дополнительный модуль рядом с ними.

## Передача видео

Program/Preview → render callback OBS → GPU staging → очередь raw video →
`decklink_output` → кадры DeckLink → preroll → Scheduled Playback → SDI OUT.
Аудио OBS конвертируется в interleaved signed 16-bit stereo 48 kHz и направляется
в тот же аппаратный выход. Запуск выхода независим от записи и интернет-трансляции.
Унаследованная очередь повторяет последний кадр при недостатке новых кадров.

Разрешение выхода масштабируется средствами существующего frontend-модуля;
частота кадров должна точно совпасть. 30000/1001 отличается от 30/1.
Перед EnableVideoOutput дополнительно проверяются SDI, pixel format и режим без
неявного преобразования режима через DoesSupportVideoMode.
Для устройства с несколькими типами выхода выбирается SDI через Configuration;
профиль платы автоматически не меняется.

## Обнаружение и сигналы

Discovery из исходного OBS отслеживает появление/исчезновение устройств.
ProfileAttributes предоставляет идентификаторы, subdevice и маски подключений;
QueryInterface определяет доступность capture/playback.
Автоопределение входного формата сохраняет исходный обработчик VideoInputFormatChanged.
Дополнительно отслеживается bmdFrameHasNoInputSource: переходы записываются в журнал.
Окно диагностики читает IDeckLinkStatus по запросу, без захвата устройства.
Значение «unknown» означает неподдерживаемый/неудачный запрос, а не состояние кабеля.
На машине без Desktop Video модуль может не загрузиться: это штатная зависимость от драйвера.

## Официальная документация

- Спецификация модели: https://www.blackmagicdesign.com/products/decklink/techspecs/W-DLK-11
  Раздел DeckLink SDI 4K: выделенные SDI IN/OUT и reference, поддерживаемые стандарты.
- SDK overview: https://sdk-doc.blackmagicdesign.com/decklink-sdk/section2.html
- Вывод, проверка режима и scheduled playback:
  https://sdk-doc.blackmagicdesign.com/decklink-sdk/DeckLinkAPI/interfaces/idecklinkoutput.html
- Вход и автоопределение:
  https://sdk-doc.blackmagicdesign.com/decklink-sdk/DeckLinkAPI/interfaces/idecklinkinput.html
- Состояние:
  https://sdk-doc.blackmagicdesign.com/decklink-sdk/DeckLinkAPI/interfaces/idecklinkstatus.html
- OBS raw output API: https://docs.obsproject.com/reference-outputs

Заголовки DeckLink взяты из закреплённой версии OBS. Современная онлайн-документация
может описывать более новый SDK; исходники используют только доступные в этих заголовках API.
Присутствие интерфейса не гарантирует, что устройство свободно или поддерживает режим:
окончательные проверки выполняются на старте и требуют реального драйвера.
