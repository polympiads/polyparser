
from polyparser.parser.result import ParsingResult


def test_enum ():
    assert set(ParsingResult._member_names_) == set([ "SUCCESS", "FAILED", "IGNORED" ])

    assert ParsingResult.FAILED .value == 0
    assert ParsingResult.IGNORED.value == 1
    assert ParsingResult.SUCCESS.value == 2

    assert     ParsingResult.FAILED .is_failed ()
    assert not ParsingResult.FAILED .is_ignored()
    assert not ParsingResult.FAILED .is_success()

    assert not ParsingResult.IGNORED.is_failed ()
    assert     ParsingResult.IGNORED.is_ignored()
    assert not ParsingResult.IGNORED.is_success()

    assert not ParsingResult.SUCCESS.is_failed ()
    assert not ParsingResult.SUCCESS.is_ignored()
    assert     ParsingResult.SUCCESS.is_success()
