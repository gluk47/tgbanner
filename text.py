import re

class Normalizer:
    def __init__(self):
        self.discard = re.compile(pattern = '['
            u'\U0001F600-\U0001F64F'  # emoticons
            u'\U0001F300-\U0001F5FF'  # symbols & pictographs
            u'\U0001F680-\U0001F6FF'  # transport & map symbols
            u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
            u'\U00002702-\U000027B0'
            u'\U000024C2-\U0001F251'
            u'\U0001f926-\U0001f937'
        ']+', flags = re.UNICODE)

        self.upper_table = str.maketrans(
            'BHN',
            'ВНН',
        )

        lower_map = {
            'ykehx3zfvanpo0ld4cmuitbё ':
            'укенхззфвапроолдчсмиитье ',

            'ɑɛʌʍʙᴀᴄᴅᴇᴍᴎᴋᴏᴑᴘᴙᴛᴢᴣᴦᴧᴨᴩᴫɯ':
            'аелмвасдемикоорятззглпрлш',

            '«»' "'":
            '""' '"',
        }

        self.lower_table = str.maketrans(
            ''.join(lower_map.keys()),
            ''.join(lower_map.values()),
        )

    def apply(self, text):
        text_orig = text.lower()
        text = self.discard.sub('', text)
        text = (
            text
            .translate(self.upper_table)
            .lower()
            .translate(self.lower_table)
        )
        if text == text_orig:
            return text
        else:
            return ' '.join([text_orig, text])

_NORMALIZER = Normalizer()


def normalize(txt: str) -> str:
    ret = _NORMALIZER.apply(txt)
    print(f'«{txt}» -> «{ret}»')
    return ret

