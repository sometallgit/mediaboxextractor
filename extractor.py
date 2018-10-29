#!/usr/bin/env python

import os
import datetime
import exifread

from PyPDF3 import PdfFileReader


# constant
points_to_mm = float(1000 * 1/2834.64567)
inch_to_mm = float(25.4)


def result_line(filename, height, width):
    return "{};{:.0f};{:.0f}\n".format(filename, width, height)


def pdf_mediabox(filename):
    pdf = PdfFileReader(open(filename, 'rb'))
    page = pdf.getPage(0).mediaBox
    width = page.getWidth()
    height = page.getHeight()
    return result_line(filename, round(float(height) * points_to_mm), round(float(width) * points_to_mm))


# hella dirty trick, but works
def prn_ps_eps_boundingbox(filename):
    keywords = [b'BoundingBox', b'PageBoundingBox']
    with open(filename, 'rb') as psfile:
        line = True
        while line:
            line = psfile.readline()
            if any([kw in line and b'atend' not in line for kw in keywords]):
                splited_line = line.decode().split()
                height = splited_line[-1]
                width = splited_line[-2]
                return result_line(filename, round(float(height) * points_to_mm), round(float(width) * points_to_mm))




def tif_boxsize(filename):
    with open(filename, 'rb') as tiff_file:
        exif_info = exifread.process_file(tiff_file)

    width = exif_info.get('Image ImageWidth').values[0]
    height = exif_info.get('Image ImageLength').values[0]
    dpi = exif_info.get('Image XResolution').values[0].num
    return result_line(filename, round(float(height)/float(dpi) * inch_to_mm), round(float(width)/float(dpi) * inch_to_mm))


def lookup():
    files = os.listdir('.')
    pdfs = filter(lambda x: x.lower().endswith('.pdf'), files)
    pss = filter(lambda x: x.lower().endswith('.ps'), files)
    epss = filter(lambda x: x.lower().endswith('.eps'), files)
    prns = filter(lambda x: x.lower().endswith('.prn'), files)
    tifs = filter(lambda x: x.lower().endswith('.tiff') or x.lower().endswith('.tif'), files)
    return {'pdf': pdfs, 'prn': prns, 'eps': epss, 'ps': pss, 'tiff': tifs}


processors = {
    'pdf': pdf_mediabox,
    'ps': prn_ps_eps_boundingbox,
    'prn': prn_ps_eps_boundingbox,
    'eps': prn_ps_eps_boundingbox,
    'tiff': tif_boxsize,
}


if __name__ == '__main__':
    files = lookup()
    result = []
    for filetype in files:
        processor = processors.get(filetype)
        for filename in files.get(filetype):
            result.append(processor(filename))

    dirname = os.path.dirname(os.path.realpath(__file__))
    report = open(
        '{}_{}-{}.csv'.format(
            os.path.basename(dirname),
            os.path.basename(os.path.dirname(dirname)),
            datetime.date.today().year
        ),
        'w+'
    )
    report.write('sep=;\n')
    report.writelines(result)
    report.close()
