import argparse

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse


def get_index(string: str, target: str):
    """
    EN: Gets index of target in string.
        In case target not in string
        returns -1
    RU:
        Возвращает индекс элемента в строке.
        Если элемента нет,
        возвращает -1
    
    Arguments:
        string:
            EN: the string to look in
            RU: строка, в которой надо найти элемент
        target:
            EN: element to look for
            RU: элемент, который надо найти
    """
    if target in string:
        return string.index(target)
    else:
        return -1


"""
EN: List of possible characters
that split the package line into package name
and package version.
e.g. 
    requests==2.25.1
    requests >= 2.25.1
    etc
RU: Список возможных символов,
отделяющих имя пакета от его версии.
Например:
    requests==2.25.1
    requests >= 2.25.1
    и т.д.
"""
PACKAGE_NAME_DELIMITERS = [
    ">=",
    "==",
    ">=",
    "<=",
    "!=",
    " "
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # path to raw requirements
    parser.add_argument(
        "--requirements",
        "-r",
        help="Path to requirements.txt",
        type=str
    )
    # max day
    parser.add_argument(
        "--day",
        "-d",
        help="Max package day",
        type=int
    )
    # max month
    parser.add_argument(
        "--month",
        "-m",
        help="Max package month",
        type=int
    )
    # max year
    parser.add_argument(
        "--year",
        "-y",
        help="Max package year",
        type=int
    )
    # output path
    parser.add_argument(
        "--output",
        "-o",
        help="Path to output requirements.txt",
        type=str,
        default="requirements_to_date.txt"
    )

    args = parser.parse_args()

    # EN: Define the threshold date
    # RU: Определить пороговую дату
    max_dt = parse(f"{args.year}-{args.month}-{args.day}T00:00:00Z")

    # EN: Read the original requirements
    # RU: Считать исходный requirements
    with open(args.requirements, "r") as f:
        lines = f.readlines()
    
    # EN: Latest release before the threshold date
    #   will be found with pypi version history
    # RU: Последняя версия пакета до пороговой даты
    #   будет найдена с помощью истории версий pypi
    URL_BASE = "https://pypi.org/project/"

    # EN: list for output requirement strings
    # RU: список выходных строк с пакетами
    output_lines = []

    for line in lines:
        # EN: Find all possible package-version delimiter
        # RU: Найти все возможные разделители имени и версии пакета
        delims = {
            delimiter: get_index(line, delimiter)
            for delimiter in PACKAGE_NAME_DELIMITERS
            if get_index(line, delimiter) != -1
        }
        # EN: If no delimiters are found,
        #   the package name is the whole line, stripped.
        # RU: Если разделителей нет вообще,
        #   то имя пакета - это вся строка без пробелов по краям
        if len(list(delims.keys())):
            delim = min(list(delims.keys()), key=lambda x: delims[x])
            package_name = line.strip().split(delim)[0]
        else:
            package_name = line.strip()
        
        # EN: Define the url for request
        # RU: Определить url для запроса
        url = URL_BASE + package_name + "/#history"
        print(f"Package {package_name}, search url: {url}")

        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        
        # EN: Pypi release history is a list of a.release__card blocks
        #   under which there is a p.release__version containing the release version
        #   and p.release__version-date containing the release date in ISO-format
        # RU: История версии pypi - это список блоков a.release__card
        #   в которых есть p.release__version содержащий версию
        #   и p.release__version-date содержащий дату релиза в ISO-формате
        elems = soup.find_all("a", {"class": "release__card"})
        for elem in elems:
            release_version = (
                elem
                .find("p", {"class": "release__version"})
                .text.
                strip()
            )

            # EN: Sometimes, "YANKED" or "PRE_RELEASE" tags
            #   are added to the version. These are preceeded with a bunch
            #   of \n symbols and should be discarded
            # RU: Иногда после версии идут теги "YANKED" или "PRE_RELEASE"
            #   перед которым идет несколько символов новой строки.
            #   От этих тегов надо избавиться
            if "\n" in release_version:
                release_version = release_version.split("\n")[0]
            
            # EN: Parsing the date
            # RU: Парсим дату
            release_date = (
                elem
                .find("p", {"class": "release__version-date"})
                .find("time")['datetime']
            )
            release_date = parse(release_date)
            print(f"\tVersion {release_version}, released: {release_date},", end=" ")
            
            # EN: Since packages go top-to-bottom
            #   newest-to-oldest, the first
            #   package to be older than the threshold date
            #   is our target
            # RU: Т.к. пакеты идут сверху в низ
            #   от самого нового к самому старому
            #   самый первый пакет, старее пороговой даты 
            #   - то, что нам надо.
            if release_date < max_dt:
                print("success!")
                print(
                    f"\t{package_name} version {release_version} "
                    f"released on {release_date} is older than the "
                    f"threshold date ({max_dt})"
                )
                print("="*30)
                output_lines.append(
                    f"{package_name} == {release_version}"
                )
                break
            print(f"too new...")
    
    # EN: Finally, save the file
    # RU: В конце сохранить файл
    with open(args.output, "w") as f:
        f.write("\n".join(output_lines))
    