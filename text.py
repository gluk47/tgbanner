def normalize(txt: str) -> str:
    txt_orig = txt.lower()
    txt = txt.translate(str.maketrans(
        'BHN',
        'ВНН',
    ))
    txt = txt.lower()

    translit = [
        'ykehx3zfvanpo0ld4cmuitbё ',
        'укенхззфвапроолдчсмиитье ',
    ]

    ipa = [
        'ɑɛʌʍʙᴀᴄᴅᴇᴍᴎᴋᴏᴑᴘᴙᴛᴢᴣᴦᴧᴨᴩᴫɯ',
        'аелмвасдемикоорятззглпрлш',
    ]

    glyph_table = [
        translit[0] + ipa[0],
        translit[1] + ipa[1],
    ]
    txt = txt.translate(str.maketrans(*glyph_table))
    if txt == txt_orig:
        return txt
    else:
        return ' '.join([txt_orig, txt])
