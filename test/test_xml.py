
import lully as ll

def test_xml_as_dict():
    assert ll.xml.asdict("""
    <AssumeRoleWithCustomTokenResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/"><AssumeRoleWithCustomTokenResult><Credentials><AccessKeyId>KYAS7KTIW1PH1K79ULWH</AccessKeyId><SecretAccessKey>0st8gsxHSxobNXqW+eU8AOgrmc0JEwB2xKcHyz9e</SecretAccessKey><SessionToken>eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9</SessionToken><Expiration>2024-04-23T15:28:10Z</Expiration></Credentials><AssumedUser>custom:yolo</AssumedUser></AssumeRoleWithCustomTokenResult><ResponseMetadata><RequestId>17C8EF0B542BDC0E</RequestId></ResponseMetadata></AssumeRoleWithCustomTokenResponse>
    """) == {
        'AccessKeyId': 'KYAS7KTIW1PH1K79ULWH', 'SecretAccessKey': '0st8gsxHSxobNXqW+eU8AOgrmc0JEwB2xKcHyz9e', 'SessionToken': 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9', 'Expiration': '2024-04-23T15:28:10Z', 'AssumedUser': 'custom:yolo', 'RequestId': '17C8EF0B542BDC0E'
    }

    assert ll.xml.asdict('<ErrorResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/"><Error><Type></Type><Code>InternalError</Code><Message>bad token</Message></Error><RequestId>17C8EF35FA1A41AA</RequestId></ErrorResponse>') == {'Type': None, 'Code': 'InternalError', 'Message': 'bad token', 'RequestId': '17C8EF35FA1A41AA'}

