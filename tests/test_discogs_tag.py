from discogs_tag.cli import merge_metadata, apply_metadata, parse_options, get_files
import pytest
import json

def test_get_files():
  files = get_files('tests/glob')
  assert files == [
    'tests/glob/01.mp3',
    'tests/glob/02.flac',
    'tests/glob/04.flac',
    'tests/glob/05.mp3',
    'tests/glob/sub1/01.flac',
    'tests/glob/sub2/01.mp3'
  ]

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
  }, audio, parse_options({ 'skip': None }))
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
      apply_metadata(data, [], parse_options({ 'dry': False, 'ignore': False, 'skip': None }))
    assert "Expecting 28 files" in str(error.value)

def test_count_subtracks():
  with open('tests/21343819.json') as release:
    data = json.load(release)

    # Test that files must match API results.
    with pytest.raises(Exception) as error:
      apply_metadata(data, [], parse_options({ 'dry': False, 'ignore': False, 'skip': None }))
    assert "Expecting 18 files" in str(error.value)
