#!/usr/bin/python

import cv2
import numpy as np
import os
import pytesser


def read_board():
    image = _acquire_image()

    cv2.namedWindow('edge')
    
    threshold1 = 2000
    threshold2 = 5000

    while True:
        scratch = image.copy()
        edge = cv2.Canny(scratch, threshold1, threshold2, apertureSize=5)
        vis = image.copy()
        vis /= 2
        vis[edge != 0] = (0, 255, 0)
        squares = find_squares(vis)
        avg_sizes = []
        for square in squares:
            width, height = _calc_width_height(square)
            print width, height
            avg_sizes.append((width + height) / 2)
            continue

        avg_size = sum(avg_sizes) / len(avg_sizes)
        squares = filter(lambda x: abs(_calc_width_height(x)[0] - avg_size) < (avg_size / 5), squares)

        cv2.drawContours(vis, squares, -1, (0, 0, 255), 3)

        print [squares[0][0], squares[0][2]]

        reverse = image
        reverse = (255-reverse)
        cv2.imshow('edge', reverse)
        cv2.waitKey(5000)
        res = pytesser.mat_to_string(_crop_to_rect(reverse, squares[0]))
        print 'res', res
        res = image[228:267, 335:376]#[335:228, 376:267]
        res = _crop_to_rect(reverse, squares[0])
        cv2.imshow('edge', res)
        ch = cv2.waitKey(500) & 0xFF
        if ch == 27:
            break
    cv2.destroyAllWindows()


def _crop_to_rect(image, rect):
    r = rect
    return image[r[0][1]:r[2][1], r[0][0]:r[2][0]]


def _calc_width_height(square):
    tl, bl, br, tr = square
    width = tr[0] - tl[0]
    height = br[1] - tr[1]
    return width, height


def angle_cos(p0, p1, p2):
    ''' Stolen from squares.py opencv sample. '''
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1)*np.dot(d2, d2)))


def find_squares(img):
    ''' Stolen from squares.py opencv sample. '''
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv2.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos(cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4]) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
    return squares


def _acquire_image():
    our_dir = os.path.dirname(os.path.abspath(__file__))
    for entry in os.listdir(our_dir):
        if entry.lower().endswith('.jpg'):
            return cv2.imread(os.path.join(our_dir, entry))

if __name__ == '__main__':
    read_board()
