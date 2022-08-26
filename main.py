import vk_api
import requests
import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

config = configparser.ConfigParser()
config.read("Configuration.ini")
LOGIN = config.get("Configuration", "Login")
PASSWORD = config.get("Configuration", "Password")
GROUP_URL = config.get("Configuration", "Group_URL")
OFFSET = config.get("Configuration", "Offset")


def authorization():
    vk_session = vk_api.VkApi(LOGIN, PASSWORD)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    return vk_session.get_api()


def main():
    vk = authorization()
    group = vk.groups.getById(group_id=GROUP_URL)[0]['id']
    photoAlbums = vk.photos.getAlbums(owner_id="-" + str(group))['items']
    for album in photoAlbums:
        i = int(OFFSET)
        try:
            if not os.path.exists("parsed/" + album['title']):
                os.makedirs("parsed/" + album['title'])
        except (FileNotFoundError, NotADirectoryError, OSError):
            if not os.path.exists("parsed/" + str(album['id'])):
                os.makedirs("parsed/" + str(album['id']))
        getphotos = vk.photos.get(owner_id="-" + str(group), album_id=album['id'], photo_sizes=1, count=1000,
                                  offset=OFFSET)
        photos = getphotos['items']
        for photo in photos:
            try:
                if int(OFFSET) < int(getphotos['count']):
                    biggest = photo['sizes'][0]['width']
                    biggestSrc = photo['sizes'][0]['url']
                else:
                    continue
            except IndexError:
                continue
            for size in photo['sizes']:
                if size['width'] > biggest:
                    try:
                        if int(OFFSET) < int(getphotos['count']):
                            biggest = size['width']
                            biggestSrc = size['url']
                        else:
                            continue
                    except IndexError:
                        continue
            content = requests.get(biggestSrc).content
            print(content)
            try:
                with open("parsed/" + album['title'] + "/" + str(i) + ".jpg", "wb") as f:
                    f.write(content)
            except (FileNotFoundError, NotADirectoryError, OSError):
                try:
                    with open("parsed/" + str(album['id']) + "/" + str(i) + ".jpg", "wb") as f:
                        f.write(content)
                except FileNotFoundError:
                    continue

            print("parsed/" + album['title'] + "/" + str(i) + ".jpg")
            i = i + 1


if __name__ == "__main__":
    main()