A script to convert a PDF without searchable text into plain text using OCR. Tested on the Justice Department report from Special Counsel Robert S. Muller III.

Requires:

* python 3.x
* pytesseract
* tesseract
* pdf2image
* PIL
* other standard modules

Tested on python 3.6.7.

Add this file and the PDF in question to a new directory. Change the freport accordingly.

Run the functions in order:

    create_dirs()

    break_pdf(freport, ntotal)

    pdf_to_jpg()

    ocr(runtype='parallel')