"""
Conversion utilities to handle PPTX files.
"""
import zipfile
import tempfile


import pathlib

from xml.dom.minidom import parse

from structs import Slide, Presentation


def presentation_from_file(path: str) -> Presentation:
    unpacked_path = tempfile.mkdtemp()

    with zipfile.ZipFile(path, "r") as z:
        z.extractall(unpacked_path)

    slides_dir = pathlib.Path(unpacked_path, "ppt", "slides")

    slides: list[Slide] = []

    for file in slides_dir.iterdir():
        if file.suffix != ".xml":
            # File is likely not a slide.
            continue

        slides.append(_slide_from_file(file))

    return Presentation(slides=slides)


def _slide_from_file(path: pathlib.Path) -> Slide:
    """ """
    parsed_slide = parse(str(path))
    return Slide.from_xml(parsed_slide)
