import mimetypes
import os
import tempfile
import urllib.parse
from functools import lru_cache
from io import BytesIO

import cairosvg
import requests
from bs4 import BeautifulSoup
from PIL import Image
from serpapi import GoogleSearch

from .cg_logger import log

if "SERP_API_KEY" in os.environ:
    SERP_API_KEY = os.environ.get("SERP_API_KEY")
else:
    log.debug("Var not found in OS Env, will look for `constants.py`")
    try:
        from constants import SERP_API_KEY
    except ImportError: 
        log.error(
            "`constants.py` file not found please make sure to put it in the current working directory."
        )
        exit(-1)


class LogoProcessor:
    def __init__(self):
        self.min_size = 200
        self.valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".svg"}
        self.downloads_folder = os.path.join(tempfile.gettempdir(), "downloaded_logos")

        os.makedirs(self.downloads_folder, exist_ok=True)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
        }

    @lru_cache(maxsize=32)
    def get(self, **kwargs):
        response = requests.get(**kwargs, timeout=15, headers=self.headers)
        return response

    def download(self, url, output_filename):
        try:
            log.info(f"Download file: {url}")
            response = self.get(url=url, stream=True)
            output_filename = os.path.join(self.downloads_folder, output_filename)

            if response.status_code == 200:
                with open(output_filename, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                return output_filename
            else:
                log.error(
                    f"Failed to download the file. Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            log.error(f"Error occurred while downloading the file: {e}")
            return False

    def fetch(self, company_name, company_website):
        log.debug(f"fetching logo, args: {company_name}, {company_website}")
        try:
            logo_url, logo_ext = self.fetch_from_google(company_name, company_website)
            if logo_url and logo_ext:
                if "svg" in logo_ext:
                    local_path = self.svg_to_png(logo_url, company_name)
                else:
                    local_path = self.download(
                        logo_url, company_name.lower().replace(" ", "_") + logo_ext
                    )
                return local_path, logo_url, logo_ext

            logo_url, logo_ext = self.fetch_from_clearbit(company_website)
            if logo_url and logo_ext:
                local_path = self.download(
                    logo_url, company_name.lower().replace(" ", "_") + logo_ext
                )
                return local_path, logo_url, logo_ext

            logo_url, logo_ext = self.fetch_from_website(company_website)
            if logo_url and logo_ext:
                if "svg" in logo_ext:
                    local_path = self.svg_to_png(logo_url, company_name)
                else:
                    local_path = self.download(
                        logo_url, company_name.lower().replace(" ", "_") + logo_ext
                    )
                return local_path, logo_url, logo_ext

        except Exception as e:
            log.error(f"Exception while fetching logo: {e}")
            return None, None, None

    def fetch_from_clearbit(self, website):
        try:
            log.debug(f"fetching logo from clearbit, args: {website}")
            domain_name = urllib.parse.urlparse(website).netloc
            logo_url = f"https://logo.clearbit.com/{domain_name}?size=400&format=png"
            response = self.get(url=logo_url, stream=True)
            if response.status_code // 100 == 2:
                width, height = self.get_dimensions(logo_url)
                # Upon tests, it seems that ClearBit isn't that reliable, sometimes
                # it returns very small logos like (32x32), or an invalid logo
                # so we gotta make sure to get the best logo most of the time.
                if width < self.min_size and height < self.min_size:
                    return (None, None)
                log.warning(
                    "This logo was found using Clearbit's logo API, "
                    "for commercial use please make sure to provide"
                    " attribution to Clearbit on the pages where this "
                    "logo is used, more info: "
                    "'https://help.clearbit.com/hc/en-us/articles/6987867587607-Logo-API-I-FAQ'"
                )
                return logo_url, ".png"
            return None, None
        except Exception as e:
            log.debug(f"exception while fetching logo from clearbit: {e}")
            return None, None

    def fetch_from_google(self, company_name, company_website):
        try:
            log.debug(
                f"fetching logo from google, args: {company_name} {company_website}"
            )
            domain_name = urllib.parse.urlparse(company_website).netloc
            if not len(domain_name):
                domain_name = company_name.replace("https://", "").replace(
                    "http://", ""
                )

            google_results = self.search_google(
                f"{repr(domain_name)} {repr(company_name)} transparent logo"
            )
            logo_url = None

            for result in google_results.get("images_results", []):
                url = result.get("original")
                log.debug(f"testing logo from url: {url}")
                if url:
                    try:
                        response = self.get(url=url, stream=True)
                        content_type = response.headers["content-type"]
                        image_extensions = mimetypes.guess_all_extensions(content_type)

                        if any(
                            [ext in self.valid_extensions for ext in image_extensions]
                        ):
                            width = result.get("original_width", 0)
                            height = result.get("original_height", 0)
                            is_product = result.get("is_product", False)
                            if is_product:
                                continue
                            if (width < self.min_size) and (height < self.min_size):
                                log.info("Logo too small, trying next one ...")
                                continue

                            log.info(f"Valid logo: {url}")
                            logo_url = url
                            extension = image_extensions[0]
                            return logo_url, extension

                    except requests.exceptions.RequestException:
                        log.debug("Logo url timed out: trying next url ...")
                else:
                    log.info("Invalid logo, trying next one ...")
        except Exception as e:
            log.debug(f"exception while fetching logo from Google: {e}")
            return None

    def fetch_from_website(self, website):
        log.debug(f"fetching logo from company's website: {website}")
        try:
            response = self.get(url=website)
            soup = BeautifulSoup(response.content, features="lxml")

            # Try with OpenGraph tags:
            for meta in soup.find_all("meta"):
                if "logo" in meta.get("property", []):
                    content_type = response.headers["content-type"]
                    extension = mimetypes.guess_all_extensions(content_type)[0]

                    return (urllib.parse.join(website, meta.get("content")), extension)

            # Try with images
            for img in soup.find_all("img"):
                if "logo" in str(img).lower():
                    src = img.get("src")
                    width = img.get("width")
                    height = img.get("height")

                    src = urllib.parse.urljoin(website, src)

                    if src is None:
                        continue

                    elif "base64" in src.lower():
                        continue

                    elif "svg" in src.lower():
                        # normally we can specify any width, height in an svg image
                        width, height = (400, 400)

                    if (width is None) or (height is None):
                        width, height = self.get_dimensions(src)

                    if width >= self.min_size or height >= self.min_size:
                        extension = os.path.splitext(urllib.parse.urlparse(src).path)[1]
                        return src, extension

            log.debug("no logo found in company's website")
            return (None, None)

        except Exception as e:
            log.debug(f"Exception occured while fetching logo from website {e}")
            return (None, None)

    @lru_cache(maxsize=128)
    def get_ext(self, url):
        response = self.get(url=url)
        content_type = response.headers["content-type"]
        extension = mimetypes.guess_all_extensions(content_type)[0]
        return extension

    @lru_cache(maxsize=128)
    def get_dimensions(self, url):
        log.debug(f"getting image dimensions, url: {url}")
        try:
            response = self.get(url=url, stream=True)
            # Check if the response status code indicates success (2xx)
            if response.status_code // 100 == 2:
                with Image.open(BytesIO(response.content)) as img:
                    return img.width, img.height

            log.debug("couldn't get dimensions")
            return (0, 0)
        except Exception as e:
            log.debug(f"exception occured while trying to get dimensions: {e}")
            return (0, 0)

    def search_google(self, query):
        log.debug(f"searching google, query: {query}")

        params = {
            "engine": "google_images",
            "q": query,
            "location": "Austin, TX, Texas, United States",
            "api_key": SERP_API_KEY,
            "tbs": "ic:trans",
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        return results

    def svg_to_png(self, logo_url, company_name):
        log.debug("Converting logo from SVG format to PNG")
        response = self.get(url=logo_url)
        tmpfile = os.path.join(tempfile.gettempdir(), tempfile.mktemp() + ".svg")
        file_name = os.path.join(
            self.downloads_folder, company_name.replace(".", "_") + "_logo.png"
        )

        with open(tmpfile, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        cairosvg.svg2png(url=logo_url, write_to=file_name, output_width=400)

        return file_name
