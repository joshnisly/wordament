
import cv2
import numpy as np


def find_grid_squares(image, expected_count):
    squares = _find_squares(image)
    avg_sizes = []
    for square in squares:
        avg_size = _calc_avg_size(square)
        if avg_size:
            avg_sizes.append(avg_size)

    if not avg_sizes:
        return []

    avg_sizes.sort()
    med_size = avg_sizes[int(len(avg_sizes) / 2)]
    squares = filter(lambda x: abs(_calc_avg_size(x) - med_size) < (med_size / 3), squares)
    squares = _remove_dups(squares)

    if len(squares) != expected_count:
        return []

    return [_normalize_square(x) for x in squares]


def square_min_max(square, index):
    xs = [x[index] for x in square]
    return min(xs), max(xs)


# ############ Helpers


def _remove_dups(squares):
    def _center(square):
        def _get_avg(index):
            min_, max_ = square_min_max(square, index)
            return min_ + (max_ - min_) / 2

        return [_get_avg(0), _get_avg(1)]

    def _is_in_square(point, square):
        def _in_range(val, index):
            min_, max_ = square_min_max(square, index)
            return val > min_ and val < max_

        return _in_range(point[0], 0) and _in_range(point[1], 1)

    unduped = []
    for square in squares:
        center = _center(square)
        assert _is_in_square(center, square)
        matches = filter(lambda x: _is_in_square(center, x), unduped)
        if not matches:
            unduped.append(square)

    return unduped


def _normalize_square(square):
    square_list = list(square)
    square_list.sort(key=lambda x: x[1])
    square = np.int32(sorted(square_list[:2], key=lambda x: x[0]) +
                      sorted(square_list[2:], key=lambda x: x[0], reverse=True))
    return square


def _calc_width_height(square):
    xs = [x[0] for x in square]
    ys = [x[1] for x in square]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    return width, height


def _calc_avg_size(square):
    return sum(_calc_width_height(square)) / 2


def angle_cos(p0, p1, p2):
    ''' Stolen from squares.py opencv sample. '''
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1)*np.dot(d2, d2)))


def _find_squares(img):
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

