#!/usr/bin/env python


import os
import datetime
from PyPDF3 import PdfFileReader


# constant
points_to_mm = float(1000 * 1/2834.64567)


def pdf_mediabox(filename):
    pdf = PdfFileReader(open(filename, 'rb'))
    page = pdf.getPage(0).mediaBox
    width = page.getWidth()
    height = page.getHeight()
    return "{};{:.0f};{:.0f}\n".format(filename, round(float(width) * points_to_mm), round(float(height) * points_to_mm))


def lookup():
    files = os.listdir('.')
    pdfs = filter(lambda x: x.lower().endswith('.pdf'), files)
    return {'pdf': pdfs}


processors = {
    'pdf': pdf_mediabox,
}


if __name__ == '__main__':
    files = lookup()
    result = []
    for filetype in files:
        processor = processors.get(filetype)
        for filename in files.get(filetype):
            result.append(processor(filename))

    report = open(
        '{}-{}.csv'.format(
            os.path.basename(os.path.dirname(os.path.realpath(__file__))),
            datetime.date.today().strftime('%d-%m-%Y')
        ),    
        'w+'
    )
    report.write('sep=;\n')
    report.writelines(result)
    report.close()
