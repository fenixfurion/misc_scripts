#!/usr/bin/env python3
# symbol finder for symbols inside of vow of the disciple
# using the tutorial from:
# https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_feature_homography/py_feature_homography.html

import os
import glob
import numpy as np
import logging
# from PIL import Image, ImageEnhance, ImageFilter
from matplotlib import pyplot as plt
import cv2
import argparse
from utils import aoc_utils as utils

# set up root log
log = logging.getLogger("root")

class sift_object:
    def __init__(self, name, image, keypoints, descriptors):
        self.name = name
        self.image = image
        self.keypoints = keypoints
        self.descriptors = descriptors

def generate_symbols(sift):
    symbols_path_list = glob.glob("./symbols/*.png")
    # print(symbols_path_list)
    symbols_path_list.sort()
    symbols_list = []
    for path in symbols_path_list:
        log.debug(f"Creating sift object from {path}")
        name = os.path.basename(path).split('.')[0]
        # print(name)
        image = cv2.imread(path, 0)
        # resize image
        scale_percent = 40
        new_w = int(image.shape[1] * (scale_percent/100.0))
        new_h = int(image.shape[0] * (scale_percent/100.0))
        new_dim = (new_w, new_h)
        image = cv2.resize(image, new_dim, interpolation= cv2.INTER_AREA)
        keypoints, descriptors = sift.detectAndCompute(image, None)
        if type(descriptors) == type(None) or type(keypoints) == type(None):
            log.warning(f"Warning: keypoints is {repr(keypoints)} and descriptors is {repr(descriptors)}")
        else:
            log.info(f"Found {len(keypoints)} keypoints and {len(descriptors)} descriptors in {name}")
        obj = sift_object(name, image, keypoints, descriptors)
        symbols_list.append(obj)
    return symbols_list

def main():
    utils.init_logging('log_symbol_finder.py')
    parser = argparse.ArgumentParser(description = "Symbol finder")
    parser.add_argument('filename')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    if not args.debug:
        log.setLevel(level=logging.INFO)
    # initalize the SIFT detector
    sift = cv2.SIFT_create()
    symbols_list = generate_symbols(sift)

    # load test image
    test_image = cv2.imread(args.filename)
    test_kp, test_des = sift.detectAndCompute(test_image, None)
    log.info(f"Loaded {len(test_kp)} keypoints and {len(test_des)} descriptors from {args.filename}")

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # match for each symbol
    MIN_MATCH_COUNT = 10
    symbol_matches = []
    for symbol in symbols_list:
        match_details = dict(name = symbol.name, good = [])
        log.info(f"Matching with {symbol.name}")
        matches = flann.knnMatch(symbol.descriptors, test_des, k=2)

        # store all good matches per Lowe's ratio test
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                match_details['good'].append(m)
        log.debug(f"Found {len(match_details['good'])} good matches with {symbol.name}")
        symbol_matches.append(match_details)
   
    MATCH_FEATURE_RATIO = 0.1
    for index, elem in enumerate(symbol_matches):
        good = elem['good']
        name = elem['name']
        #if len(good) < MIN_MATCH_COUNT:
        # try dynamic min match count
        if len(good) < int(MATCH_FEATURE_RATIO * len(symbols_list[index].keypoints))+1:
            log.debug(f"Not creating match mask for {name}, only {len(good)} matches")
            continue
        log.info(f"Finding {name} in image ({len(good)} matches)")
        src_pts = np.float32([ symbols_list[index].keypoints[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ test_kp[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()

        h,w = symbols_list[index].image.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        # dst = cv2.perspectiveTransform(pts,M)

        #test_image_mod = cv2.polylines(test_image,[np.int32(dst)],True,255,3, cv2.LINE_AA) 
        test_image_mod = test_image

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)

        img3 = cv2.drawMatches(symbols_list[index].image,symbols_list[index].keypoints,test_image_mod,test_kp,good,None,**draw_params)
        RGB_img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)

        plt.imshow(RGB_img3),plt.show()

if __name__ == '__main__':
    main()

