from discogs_tag.cli import merge_metadata, apply_metadata, parse_options, list_files, rename_component, rename_path, rename_file
import pytest
import json

def test_list_files():
  files = list_files('tests/glob')
  assert files == [
    'tests/glob/01.mp3',
    'tests/glob/02.flac',
    'tests/glob/04.flac',
    'tests/glob/05.mp3',
    'tests/glob/sub1/01.flac',
    'tests/glob/sub2/01.mp3'
  ]

def test_merge_metadata():
  audio = merge_metadata({
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
  }, { 'title': 'Some other title' }, parse_options({ 'skip': None }))
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

def test_rename_component():
  assert '1-02 Title' == rename_component({
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  assert '02 Title' == rename_component({
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  with pytest.raises(IndexError) as error:
    rename_component({
      'artist': ['Artist'],
      'albumartist': ['Album Artist'],
      'album': ['Album'],
      'composer': ['Composer'],
      'discnumber': [],
      'genre': ['Genre'],
      'tracknumber': [2],
      'title': ['Title'],
      'date': ['2024']
    }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  assert "list index out of range" in str(error.value)

def test_rename_path():
  assert ('/src/path/Album Artist - (2024) Album', '/src/path/Album Artist - (2024) Album') == rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  assert ('/src/path/Album Artist - (2024) Album1 - Album2', '/src/path/Album Artist - (2024) Album1 - Album2') == rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album1 / Album2'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  assert ('/src/path/from', '/src/path/from') == rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  assert ('/src/path/Album Artist/(2024) Album', '/src/path/Album Artist') == rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z/(%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))

def test_rename_file():
  assert '/dest/path/to/1-02 Title.flac' == rename_file('/src/path/from/test.flac', '/dest/path/to', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  assert '/dest/path/to/1-02 Artist1 - Artist2 - Title1 - Title2.flac' == rename_file('/src/path/from/test.flac', '/dest/path/to', {
    'artist': ['Artist1 / Artist2'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title1 / Title2'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %a - %t', parse_options({ 'dry': True, 'ignore': False }))
  assert '/dest/path/to/test.flac' == rename_file('/src/path/from/test.flac', '/dest/path/to', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/', parse_options({ 'dry': True, 'ignore': False }))
