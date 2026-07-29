"""Seam: vnknowledge.sources.vbpl.parser.extract_body / extract_subject — pure functions
over raw fetch payloads, fixtures are real (anonymized-free, public) vbpl.vn responses."""

from pathlib import Path

from vnknowledge.sources.vbpl.parser import extract_body, extract_subject

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "vbpl"


def test_extract_body_returns_flat_text_from_rsc_payload():
    rsc_text = (FIXTURES / "sample_body.rsc.txt").read_text(encoding="utf-8")

    body = extract_body(rsc_text)

    assert body is not None
    assert "BỘ CÔNG THƯƠNG" in body
    assert "Điều 1." in body
    assert "<" not in body


def test_extract_body_returns_none_when_no_text_segment():
    assert extract_body('0:["$@1",["x",null]]\n') is None


def test_extract_subject_reads_title_from_document_record_row():
    rsc_text = (FIXTURES / "sample_body.rsc.txt").read_text(encoding="utf-8")

    subject = extract_subject(rsc_text)

    assert subject is not None
    assert "hạn ngạch thuế quan nhập khẩu" in subject


def test_extract_subject_prefers_docabs_over_title_when_present():
    rsc_text = '2:T5,<p>x</p>\n1:{"id":"1","title":"citation title","docAbs":"the real abstract"}'

    assert extract_subject(rsc_text) == "the real abstract"


def test_extract_subject_returns_none_without_document_record_row():
    assert extract_subject("2:T5,<p>x</p>\n") is None
