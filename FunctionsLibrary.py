# Importing standard libraries
from urllib import request as r
from bs4 import BeautifulSoup
from re import search
from os import makedirs, remove
from time import strftime, localtime
from sys import path
print(path[0])
# Importing custom modules
from . import Constants as c
from . import Helpers  as h


# Defining request with necessary headers.
# Headers are necessary to avoid protection
# on some web sites based on User-Agent identification:
def targetRequest(uri):
    response_object = r.urlopen((r.Request (uri, headers=c.HEADERS2)))
    return response_object

# Getting HTTP response code for given URI:
def getHTTPCodeFromURI(uri):
    code =  targetRequest(uri).getcode()
    return code

# Getting web page URI from command prompt:
def getWebPageURIFromPrompt(txt):
    # inputIsOk is used for primitive user input validation.
    inputIsOk = False
    uri = ""
    while not inputIsOk:
        uri = str(input(txt))
        c.site = uri
        # Verifying that URI is not empty
        if uri != "":
            # Verifying that URI contains protocol:
            if any(protocol in uri for protocol in ["http://", "https://"]):
                try:
                    code = getHTTPCodeFromURI(uri)
                    if code == 200:
                        inputIsOk = True
                    else:
                        print(c.ERROR_URI_OTHER + "\nHTTP response: " + str(code))
                except KeyError as e:
                    print(c.ERROR_URI_OTHER + str(e))
            else:
                print(c.ERROR_URI__PROTOCOL)
        else:
            print(c.ERROR_URI_NONE)
    return uri

# Getting target directory from prompt
def getTargetDirectory(txt):
    dir = str(input(txt))
    if dir == "":
        # Adding intermediate folder for default catalogue:
        dir += path[0].replace("\\", "/") + "/" \
               + c.INTERMEDIATE_CATALOGUE_NAME
    else:
        # Simplified directory validation:
        if any(splitter in dir for splitter in [":/", ":\\"]):
            # Adding trailing slash for the case it's missing:
            dir = h.lastSlashChecker(dir)
            # Creating requested directory if it doesn't exist:
    makedirs(dir, exist_ok=True)
    return dir

# Image URI are usually located in <a> tags within "href" attribute
# or in <img> tags within "src" attribute. Following function
# helps to pull image URI from both:
def gettingImgURIsByTagNAttribute(uri, tag, attribute):
    src_attribute = tag[attribute]
    img_uri = ""
    if any(extension in src_attribute for extension in c.IMG_EXTENSIONS):
        # Some image URIs are missing hosting site in the beginning.
            # Following check will add web site host for such cases:
            #if any(protocol in src_attribute for protocol in ["http://", "https://"]):
            if src_attribute[:4] == "http":
                img_uri = src_attribute
                print("NOTHING DONE: " + str(img_uri)) #DEBUG
            elif str(src_attribute[:2]) == ("//" or "\\\\"):
                img_uri = h.gettingProtocolFromUri(uri) \
                          + ":" + src_attribute
                print("PROTOCOL ADDED: " + str(img_uri))  #DEBUG
            else:
            #if any(protocol in src_attribute for protocol in ["http://", "https://"]):
                #img_uri = "http://" + src_attribute
                img_uri = h.gettingProtocolNDomainNameFromURI(uri) \
                          + src_attribute
                print("DOMAIN ADDED: " + str(img_uri))  #DEBUG
    else:
        raise ValueError
    return img_uri

# Getting list of image URIs located under given web page
def getImgListFromURI_2(uri):
    # Getting HTML from target URI
    html = targetRequest(uri)
    print(html) #DEBUG
    # Forming beautiful soup object
    bs_obj = BeautifulSoup(html.read().decode(encoding="iso-8859-1"), "html.parser")
    # Getting img from tags:
    img_tags = bs_obj.find_all('img')
    print(img_tags) #DEBUG

    a_tags = bs_obj.find_all('a')
    print(a_tags)  # DEBUG

    source_tags = bs_obj.find_all('source')
    print(source_tags)  # DEBUG
    # Getting URIs om images from "src" attributes of img "tags"
    img_uris = []

    print("\n\n START LOOKING FOR IMG URLS BY IMG/SRC \n\n")
    for tag in img_tags:
        try:
            img_uri = gettingImgURIsByTagNAttribute(uri, tag, 'src').split("?",1)[0]
            print(img_uri + " by 'src'") #DEBUG
            img_uris.append(img_uri)
        except (KeyError, ValueError):
            #print("FAILED gettingImgURIsByTagNAttribute by src")
            pass

    print("\n\n START LOOKING FOR IMG URLS BY IMG/data-layzr-srcset \n\n")
    for tag in img_tags:
        try:
            img_uri = gettingImgURIsByTagNAttribute(uri, tag, 'data-layzr-srcset').split("?",1)[0]
            print(img_uri + " by 'src'") #DEBUG
            img_uris.append(img_uri)
        except (KeyError, ValueError):
            #print("FAILED gettingImgURIsByTagNAttribute by data-layzr-srcset")
            pass

    print("\n\n START LOOKING FOR IMG URLS BY A/HREF \n\n")
    for tag in a_tags:
        try:
            img_uri = gettingImgURIsByTagNAttribute(uri, tag, 'href').split("?",1)[0]
            print(img_uri + " by 'href'")  # DEBUG
            img_uris.append(img_uri)
        except (KeyError, ValueError):
            #print("FAILED gettingImgURIsByTagNAttribute by href")
            pass

    print("\n\n START LOOKING FOR IMG URLS BY SOURCE/DATA-SRCSET \n\n")
    for tag in source_tags:
        try:
            source_dirty_uri = gettingImgURIsByTagNAttribute(uri, tag, 'data-srcset')
            source_uri = source_dirty_uri.split("?", 1)[0]
            print(source_uri + " by 'data-srcset'") #DEBUG
            img_uris.append(source_uri)
        except (KeyError, ValueError):
            #print("FAILED gettingImgURIsByTagNAttribute by data-srcset")
            pass
    print(img_uris)
    return img_uris

# Getting list of image names from image URIs:
def getImgNamesFromImgURIs(uri_lst):
    img_names = []
    img_extensions_str = h.lstToStrWithOr(c.IMG_EXTENSIONS)
    # Using regular expression for pulling image names
    # with corespondent extensions:
    for uri in uri_lst:
        uri = str(uri)
        try:
            img_name = search(r'([\w\.\(\)_-]+[.](' + img_extensions_str + '))', uri)\
                       .group(0)
            img_names.append(img_name)
        except:
            pass
    return img_names


# Loading images and report:
def loadImagesAndReport(uri, dir):
    #uri_lst = getImgListFromURI(uri)
    uri_lst = getImgListFromURI_2(uri)
    print(uri_lst) #DEBUG
    name_lst = getImgNamesFromImgURIs(uri_lst)
    # Getting time for naming catalogue with image and report:
    load_start_time = strftime("%Y-%m-%d_%H-%M-%S",localtime())
    # Getting site name for naming catalogue with image and report:
    site_name = h.gettingSiteNameFromUri(uri)
    # Composing catalogue name for storing loaded images
    img_file_path = dir + site_name + "_" + load_start_time
    # Creating catalogue for image storage:
    makedirs(img_file_path, exist_ok=True)

    # Composing report file full path and name
    report_file_path_name = dir + site_name + "_" + load_start_time + "_Report.txt"
    # Declaring empty strings for collecting URIs to reports...
    # ...with successfully loaded images and...
    report_success = ""
    # ...images failed to load:
    report_failures = ""

    for i in range(len(uri_lst)):
        # Composing image full path and name:
        try:
            img_file_path_name = img_file_path + "/" + name_lst[i]
        except:
            pass
        load_success = True
        with open(img_file_path_name, 'wb') as img_file:
            try:
                # Writing image to new file:
                img_file.write(targetRequest(uri_lst[i]).read())
                # Adding successful URI to related list if it's unique:
                if str(uri_lst[i]) not in report_success:
                    report_success += str(uri_lst[i]) + "\n"
            except Exception as e:
                # Adding broken URI to related list if it's unique:
                load_success = False
                if str(uri_lst[i]) not in report_failures:
                    report_failures += "    " + str(uri_lst[i]) + " Error: " + str(e) + "\n"
        # Removing image file in case of handled load error
        if load_success == False:
            remove(img_file_path_name)
        # Adding progress notification:
        h.progressNotification(i, uri_lst)

    # Writing report to root folder of target direction:
    with open(report_file_path_name, "w") as report_file:
        report_file.write(c.TEXT_REPORT % (report_success, report_failures))
