from discogs_tag.cli import merge_metadata, apply_metadata
import pytest
import json

def test_merge_metadata():
  audio = {}
  merge_metadata({
    'year': 2002,
  }, {
    'title': 'Title',
    'artists': [{
      'anv': 'Artist 1'
    }, {
      'name': 'Artist 2'
    }, {
      'anv': '',
      'name': 'Artist 3 (56)'
    }],
    'position': '1-02',
    'extraartists': [{
      'role': 'Guitar',
      'name': 'Guitarist'
    }, {
      'role': 'Written-By',
      'name': 'Composer'
    }]
  }, audio, {
    'skip_artist': False,
    'skip_composer': False,
    'skip_title': False,
    'skip_position': False,
    'skip_year': False
  })
  assert audio['title'] == 'Title'
  assert audio['artist'] == 'Artist 1, Artist 2, Artist 3, Guitarist'
  assert audio['discnumber'] == '1'
  assert audio['tracknumber'] == '02'
  assert audio['composer'] == 'Composer'
  assert audio['date'] == '2002'

def test_apply_metadata():
  with open('tests/18051880.json') as release:
    data = json.load(release)

    # Test that files must match API results.
    with pytest.raises(Exception) as error:
      apply_metadata(data, [], { 'dry': False, 'ignore': False, 'skip_subtrack': False })
    assert "Expecting 28 files" in str(error.value)

def test_count_subtracks():
  with open('tests/21343819.json') as release:
    data = json.load(release)

    # Test that files must match API results.
    with pytest.raises(Exception) as error:
      apply_metadata(data, [], { 'dry': False, 'ignore': False, 'skip_subtrack': False })
    assert "Expecting 18 files" in str(error.value)
