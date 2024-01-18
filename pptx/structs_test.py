import pathlib
from xml.dom.minidom import parse, Element
import zipfile

import pytest

from pptx.structs import Slide


@pytest.fixture()
def get_sample(tmp_path):
    """Retrieves a sample slideset from the /samples directory by name."""

    def _get_sample_slide(label: str, index: int) -> Element:
        sample_path = pathlib.Path("samples", f"{label}.pptx")
        with zipfile.ZipFile(sample_path, "r") as z:
            z.extractall(tmp_path)

        slide_path = pathlib.Path(tmp_path, "ppt", "slides", f"slide{index+1}.xml")

        return parse(str(slide_path))

    return _get_sample_slide


def test_extracts_no_shapes_from_empty_slide(get_sample):
    """Shapes store content, an empty slide has no content nor shapes."""
    sample = get_sample("single_empty_slide", 0)

    slide = Slide.from_xml(sample)

    assert len(slide.shapes) == 0


def test_extracts_shape_from_nonempty_slide(get_sample):
    """A slide with exactly one element has exactly one shape."""
    sample = get_sample("text_samples", 0)

    slide = Slide.from_xml(sample)

    assert len(slide.shapes) == 1


def test_extracts_multiple_shapes_from_slide(get_sample):
    sample = get_sample("text_samples", 1)

    slide = Slide.from_xml(sample)

    assert len(slide.shapes) == 3


def test_extracts_paragraphs_from_shape_with_text(get_sample):
    """A slide containing a text box with one block of text has one paragraph."""
    sample = get_sample("text_samples", 0)

    slide = Slide.from_xml(sample)
    shape = slide.shapes[0]
    shape_text = shape.text

    assert len(shape_text.paragraphs) == 1


def test_extracts_text_runs_from_shape_with_text(get_sample, snapshot):
    """A paragraph is made of runs."""
    sample = get_sample("text_samples", 0)

    slide = Slide.from_xml(sample)
    shape = slide.shapes[0]
    shape_text = shape.text
    paragraphs = shape_text.paragraphs
    runs = paragraphs[0].runs

    assert len(runs) == 1

    run = runs[0]

    assert run.text == snapshot
    assert run.props == snapshot


@pytest.mark.parametrize(
    "run_text,expected_props",
    [["boldness", {"b": "1"}], ["italics", {"i": "1"}]],
    ids=["bold", "italics"],
)
def test_extracts_text_formatting_properties_from_shape_with_text(
    get_sample, snapshot, run_text, expected_props
):
    sample = get_sample("text_samples", 2)

    paragraph = Slide.from_xml(sample).shapes[0].text.paragraphs[0]
    runs = paragraph.runs

    selected_run = [run for run in runs if run.text == run_text][0]

    for prop in expected_props:
        assert expected_props[prop] == selected_run.props[prop]
