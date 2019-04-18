#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
# totext.py - converts the Mueller report from images to text with OCR
#
# v 0.0.1
# rev 2019-04-18 (created)

"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from PIL import Image
import fnmatch
import pytesseract
from pdf2image import convert_from_path
import os
import subprocess
import re
import multiprocessing as mp

# saves the pdfs to jpgs
def pdf_to_jpg():
    p = re.compile('report_(?P<start>\d{3})-(?P<end>\d{3}).pdf')

    d = os.path.join(os.getcwd(), 'pdf')
    pdfs = file_match(d, 'pdf')

    for pdf in pdfs[:]:
        fshort = os.path.basename(pdf)
        print(fshort)
        m = p.match(fshort)
        start = int(m.groupdict()['start'])
        end = int(m.groupdict()['end'])
        print(start, end)

        pages = convert_from_path(pdf, 500)

        # Iterate through all the pages stored above
        for i, page in enumerate(pages, start=start):
            fshort = "page_{:03d}.jpg".format(i)
            f = os.path.join(os.getcwd(), 'pages', fshort)

            if not os.path.exists(f):
                print(f)
                page.save(f, 'JPEG')

# ocr all
def ocr(runtype='debug'):
    d = os.path.join(os.getcwd(), 'pages')

    jpgs = file_match(d, 'jpg')
    print(len(jpgs))

    n = len(jpgs)

    # number of pages in each batch
    npages = 10

    i0_all = range(0, n, npages)

    list_all = []

    # Iterate from 1 to total number of pages
    for j, i0 in enumerate(i0_all[:]):
        list_short = jpgs[i0:i0+npages]

        if i0 + npages > n:
            endpage = n

        # save file name
        fsave_short = "report_{:03d}-{:03d}.txt".format(i0+1, endpage)
        fsave = os.path.join(os.getcwd(), 'txt', fsave_short)
        list_all.append((fsave, list_short))

    # print(list_all)

    if runtype == 'debug':
        if not os.path.exists(fsave):
            for fsave, list_short in list_all[:2]:
                ocr_kernel(fsave, list_short)

    elif runtype == 'parallel':
        # not efficient at 6 threads ... might be between 3 and 6
        N_threads = 3
        pool = mp.Pool(processes=N_threads)

        # iterate through the sublist
        for fsave, list_short in list_all[:]:
            pool.apply_async(ocr_kernel, args=(fsave, list_short))

        pool.close()
        pool.join()

# break the PDF up into smaller parts
def break_pdf(freport, n):
    npages = 10

    i_all = [a+1 for a in range(0, n, 1)]
    # i_all = np.arange(0, n, 1) + 1
    i0_all = i_all[::npages]

    fout_temp = 'pdf/report_{start:03d}-{end:03d}.pdf'
    ctemp = 'pdftk {} cat {{start:d}}-{{end:d}} output {}'.format(freport, fout_temp)

    for i0 in i0_all[:]:
        start = i0
        end = i0 + npages-1
        if end > n:
            end = n
        fout = fout_temp.format(start=start, end=end)
        c = ctemp.format(start=start, end=end)

        if not os.path.exists(fout):
            print(fout)
            subprocess.call(c, shell=True)

# check directory for existence
def dir_check(d):
    if not os.path.isdir(d):
        return 0

    else:
        return os.path.isdir(d)

# creation of directories - only create if doesn't exist
def dir_create(d):
    if not dir_check(d):
        os.makedirs(d)
        print('Created dir {}'.format(d))

# Get data files matching file_ext in a given directory
def file_match(dsearch, file_ext, local=0):
    """ file_match(dsearch, 'pkl', local=1)
    """
    file_list = []

    if not local:
        if os.path.exists(dsearch):
            for root, dirnames, filenames in os.walk(dsearch):
                # this one is modified to add the period!!
                for fname in fnmatch.filter(filenames, '*.'+file_ext):
                    file_list.append(os.path.join(root, fname))
    else:
        file_list = [os.path.join(dsearch, file) for file in os.listdir(dsearch) if file.endswith(file_ext)]

    # sort file list in place
    file_list.sort()

    return file_list

# one save file and a list of jpgs to OCR
def ocr_kernel(fsave, flist):
    print(fsave)

    for f in flist:
        text = str(((pytesseract.image_to_string(Image.open(f)))))
        text = text.replace('-\n', '')

        print(f)

        # Finally, write the processed text to the file.
        with open(fsave, 'a') as fwrite:
            fwrite.write(text)

# create directories
def create_dirs():
    dhere = os.getcwd()
    list_subs = [
        'pages',
        'pdf',
        'txt',
    ]
    for dsub in list_subs:
        d = os.path.join(dhere, dsub)
        dir_create(d)

if __name__ == '__main__':
    freport = 'report.pdf'
    ntotal = 448

    create_dirs()
    break_pdf(freport, ntotal)
    pdf_to_jpg()
    ocr(runtype='parallel')
