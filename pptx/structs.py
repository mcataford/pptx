import typing
from dataclasses import dataclass

from xml.dom.minidom import Element


@dataclass
class TextRun:
    """
    Representation of a text segment within a paragraph.

    See Paragraph documentation.
    """

    text: str
    props: typing.Dict[str, str]

    @classmethod
    def from_xml(cls, element: Element) -> "TextRun":
        text = element.getElementsByTagName("a:t")[0]
        props_xml = element.getElementsByTagName("a:rPr")
        props = props_xml[0].attributes if props_xml else None

        extracted_properties: typing.Dict[str, str] = {}

        if props:
            for prop_index in range(props.length):
                extracted_properties[props.item(prop_index).name] = props.item(
                    prop_index
                ).value

        extracted_text = text.firstChild.nodeValue if text.hasChildNodes() else ""

        return cls(text=extracted_text, props=extracted_properties)


@dataclass
class Paragraph:
    """
    Representation of a paragraph within the text body of a shape.

    See: https://web.archive.org/web/20220627001219/http://officeopenxml.com/drwSp-text-paragraph.php
    """

    runs: typing.List[TextRun]

    @classmethod
    def from_xml(cls, element: Element) -> "Paragraph":
        runs = [
            TextRun.from_xml(child) for child in element.getElementsByTagName("a:r")
        ]
        return cls(runs=runs)


@dataclass
class TextBody:
    """
    Representation of the text body of a shape.

    See: https://web.archive.org/web/20220627002331/http://officeopenxml.com/drwSp-text.php
    """

    paragraphs: typing.List[Paragraph]

    @classmethod
    def from_xml(cls, element: Element) -> "TextBody":
        paragraphs = [
            Paragraph.from_xml(child) for child in element.getElementsByTagName("a:p")
        ]
        return cls(paragraphs=paragraphs)


@dataclass
class Shape:
    """
    Representation of a single element on a slide.

    See: https://web.archive.org/web/20231226205058/http://officeopenxml.com/drwShape.php
    """

    id: str
    name: str
    is_text_box: bool
    text: TextBody

    @classmethod
    def from_xml(cls, element: Element) -> "Shape":
        shape_non_visual_props = element.getElementsByTagName("p:nvSpPr")[0]
        common_non_visual_props = shape_non_visual_props.getElementsByTagName(
            "p:cNvPr"
        )[0]
        common_non_visual_shape_properties = (
            shape_non_visual_props.getElementsByTagName("p:cNvSpPr")[0]
        )

        shape_name = common_non_visual_props.getAttribute("name")
        shape_id = common_non_visual_props.getAttribute("id")
        is_text_box = common_non_visual_shape_properties.getAttribute("txBox") == "1"

        text_nodes = element.getElementsByTagName("p:txBody")[0]

        text_body = TextBody.from_xml(text_nodes)

        return cls(
            id=shape_id, name=shape_name, is_text_box=is_text_box, text=text_body
        )


@dataclass
class Slide:
    """
    Representation of a single slide part of a slideset.
    """

    raw_xml: str
    shapes: typing.List[Shape]

    @classmethod
    def from_xml(cls, element: Element) -> "Slide":
        shapes: list[Shape] = []

        for shape_xml in element.getElementsByTagName("p:sp"):
            shapes.append(Shape.from_xml(shape_xml))

        return cls(raw_xml=element.toxml(), shapes=shapes)


@dataclass
class Presentation:
    """
    Representation of the unpacked content of the slideset.
    """

    slides: typing.List[Slide]
