#!/usr/bin/python

import cv2
import numpy as np
try:
    import tesseract
except ImportError:
    print 'Skipping tesseract...'

import search
import vision.squares

IMAGE_SIZE = 480


def find_and_rotate_image(image):
    scratch = image.copy()
    scratch = cv2.cvtColor(scratch, cv2.COLOR_BGR2GRAY)

    # Crop image to square
    scratch = scratch[0:IMAGE_SIZE, 0:IMAGE_SIZE]

    # Rotate image
    height, width = scratch.shape[:2]
    matrix = cv2.getRotationMatrix2D((width/2, height/2), 90, 1)
    return cv2.warpAffine(scratch, matrix, (width, height))


def find_grid_squares(image):
    ''' Returns {
        'square_rows': [[]],
     } or None '''
    # Find squares, so we can warp image to include only them.
    grid_squares = vision.squares.find_grid_squares(image, search.GRID_SIZE**2)

    if not grid_squares:
        return None

    square_rows = _arrange_in_grid(grid_squares)
    return {
        'square_rows': square_rows
    }


def warp_image_to_squares(image, square_rows):
    ''' Returns {
        'warped_image': image,
        'new_squares': [[]]
    '''

    tl = square_rows[0][0][0]
    tr = square_rows[0][-1][1]
    bl = square_rows[-1][0][3]
    br = square_rows[-1][-1][2]
    src_points = np.float32([
        (tl[0]-5, tl[1]-5),
        (tr[0]+5, tr[1]-5),
        (bl[0]-5, bl[1]+5),
        (br[0]+5, br[1]+5)
    ])
    dst_points = np.float32([[0, 0], [IMAGE_SIZE, 0], [0, IMAGE_SIZE], [IMAGE_SIZE, IMAGE_SIZE]])
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    return cv2.warpPerspective(image, matrix, (IMAGE_SIZE, IMAGE_SIZE))


def squares_to_text(image, squares):
    ''' Returns grid text. '''

    scratch = image.copy()
    squares = [x for y in squares for x in y]
    shrunk_grid_squares = [_shrink_square(x, 3, 20) for x in squares]
    thresholded = cv2.threshold(scratch, 160, 250, cv2.THRESH_BINARY_INV)[1]
    cv2.imshow('threshold', thresholded)

    shrunk_grid_squares = _arrange_in_grid(shrunk_grid_squares)
    text = ''
    for row in shrunk_grid_squares:
        for square in row:
            square_text, confidence = _ocr(_crop_to_rect(thresholded, square))
            square_text = square_text or 'I'
            text += square_text

    return text.lower()


def draw_squares(image, square_rows):
    ''' Returns marked up image. '''
    scratch = image.copy()
    squares = [x for y in square_rows for x in y]
    cv2.drawContours(scratch, squares, -1, (0, 0, 255), 3)
    return scratch


def draw_letters_at_squares(image, text, square_rows):
    scratch = image.copy()
    for row_index, row in enumerate(square_rows):
        for col_index, square in enumerate(row):
            _print_text(scratch, square, '%i:%i (%s)' % (row_index, col_index, text[0]))
            text = text[1:]
    return scratch


def _trash():
    for row_index, row in enumerate(square_rows):
        for col_index, square in enumerate(row):
            _print_text(vis, square, '%i:%i' % (row_index, col_index))

    cv2.imshow('squares', vis)


    shrunk_grid_squares = [_shrink_square(x, 3, 20) for x in deskewed_grid_squares]
    cv2.drawContours(deskewed, shrunk_grid_squares, -1, (0, 0, 255), 3)
    cv2.imshow('deskewed squares', deskewed)

    thresholded = cv2.threshold(deskewed, 160, 250, cv2.THRESH_BINARY_INV)[1]

    cv2.imshow('threshold', thresholded)

    text = ''
    deskewed_square_rows = _arrange_in_grid(deskewed_grid_squares)
    for row in deskewed_square_rows:
        for square in row:
            square_text, confidence = _ocr(_crop_to_rect(thresholded, square))
            square_text = square_text or 'I'
            cv2.imshow('cropped', _crop_to_rect(thresholded, square))
            print square_text, confidence

            text += square_text
    print text.lower()


def _ocr(image):
    api = tesseract.TessBaseAPI()
    api.Init('/usr/share/tesseract-ocr', 'eng', tesseract.OEM_DEFAULT)
    api.SetVariable('tessedit_char_whitelist', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ/')
    api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)

    ocr_image = cv2.cv.CreateImageHeader((image.shape[1], image.shape[0]), cv2.IPL_DEPTH_8U, 1)
    cv2.cv.SetData(ocr_image, image.tostring(), image.dtype.itemsize*image.shape[1])
    tesseract.SetCvImage(ocr_image, api)
    return api.GetUTF8Text().strip(), api.MeanTextConf()


def _arrange_in_grid(grid_squares):
    grid_squares.sort(key=lambda x: vision.squares.square_min_max(x, 1))
    square_rows = search.load_from_string(grid_squares)
    for row in square_rows:
        row.sort(key=lambda x: vision.squares.square_min_max(x, 0))
    return square_rows


def _print_text(image, square, text):
    coords = (
        vision.squares.square_min_max(square, 0)[0],
        vision.squares.square_min_max(square, 1)[0]
    )
    cv2.putText(image, text, (coords[0]+1, coords[1]+1), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 0),
                lineType=cv2.CV_AA, thickness=2)
    cv2.putText(image, text, coords, cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), lineType=cv2.CV_AA)


def _shrink_square(square, x, y):
    for i in [0, 3]:
        square[i][0] += x
    for i in [1, 2]:
        square[i][0] -= x
    for i in [0, 1]:
        square[i][1] += y
    for i in [2, 3]:
        square[i][1] -= y
    return square


def _crop_to_rect(image, r):
    return image[r[0][1]:r[2][1], r[0][0]:r[2][0]]

