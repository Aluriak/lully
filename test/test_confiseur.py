

import json
from lully import Confiseur, Bonbon


class MyConfig(Confiseur):

    def bonbons(self) -> [Bonbon]:
        return (
            Bonbon('key', 'subkeyA', default='value', type=str),
            ('key', 'subkeyB', 'value'),  # a tuple is valid too, with 3 or 4 elements
            ('key', 'subkeyC', 'a value', str),  # here with type
            ('server options', 'max instances', 3),
            Bonbon('global', 'numbers', default='zero=0,one=1', type=int, dict_as_str=True),  # handling of dict as string
        )

    def validate(self, cfg):
        if cfg['server options']['max instances'] > 10:
            self.add_error(f"Can't handle more than ten instances. Provided: {cfg['server options']['max instances']}.")


def test_no_input_file():

    myconfig = MyConfig()
    assert myconfig['global']['numbers'] == {'zero': 0, 'one': 1}
    assert myconfig.raw == {}
    assert not myconfig.errors

def test_inlined_input_file():
    json_data = {"server options": { "max instances": 11 }}
    myconfig = MyConfig(json.dumps(json_data), filetype='json')
    assert myconfig.raw == json_data
    assert myconfig['server options']['max instances'] == 11
    assert len(myconfig.errors) == 1
    assert myconfig.errors[0].startswith("Can't handle more than ten instances. Provided: 11.")

def test_multiple_inputs():
    json_dataA = {"server options": { "max instances": 4 }}
    json_dataB = {"server options": { "max instances": 11 }, "key": {"subkeyC": "plouf"}}
    myconfig = MyConfig(json.dumps(json_dataA), json.dumps(json_dataB), filetype='json')
    assert myconfig.raw == {"server options": { "max instances": 4 }, "key": {"subkeyC": "plouf"}}
    assert myconfig['server options']['max instances'] == 4
    assert myconfig['key']['subkeyC'] == 'plouf'
    assert not myconfig.errors
