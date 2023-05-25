# pip2date
## EN

Sometimes, it is necessary to filter pypi package versions by a date, e.g. when you want all your packages released before 2023-06-06.

pip2date does just that! Provided an existing requirements.txt file (or a list of package names) it will generate a new requirements.txt file where all packages will be of the latest version before the threshold date.

## RU: Установить версии пакетов в requirements.txt по дате

Иногда нужно отфильтровать версии pypi-пакетов по дате, например когда нужно, чтобы все версии были выпущены до 2023-06-06.

pip2date делает именно это! Подайте на вход существующий requirements.txt (или список имен пакетов) и на выходе получите новый requirements.txt, в котором все версии пакетов будут самыми актуальными до пороговой даты.

## Example
```
python pip2date.py -r example_requirements.txt -o requirements_to_date.txt -y 2022 -m 1 -d 1
```

will give a list of package versions all released before 2022-01-01.

## CLI parameters

--requirements / -r : path to input file (str, required)

--output / -o : path to output file (str, optional, default = "requirements_to_date.txt")

--year / -y : year of the threshold date (int, required)

--month / -m : month of the threshold date (int, required)

--day / -d : day of the threshold date (int, required)

## Side-note

EN: Sometimes, the raw release date can differ from the date you actually see on the pypi website.
  For example, see numpy 1.20.0. It was released December 31, 2021, but the actual date displayed is Jan 1, 2022.
  To counter this, I suggest simply lowering the threshold date. E.g. 2022-01-01 -> 2021-12-31
RU: Иногда сырая версия выгрузки версии отличается от того, что на самом деле показывает сайт pypi.
  Например, см. numpy 1.20.0. Он был выпущен 31 декабря 2021, но отображаемая дата - 1 января 2022.
  Чтобы исправить это, предлагаю просто понижать дату, т.е. 2022-01-01 -> 2021-12-31
