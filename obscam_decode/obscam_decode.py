#!/usr/bin/env python3
"""
write me a python script that opens a socket at an address:port taken as an argument, 
and stores the video feed as an mp4 file. the data stream is an H264 video stream.
"""
import socket
import struct
import logging
from io import BytesIO
from PIL import Image
import argparse
import os
import cv2
import numpy as np
import pytesseract
import time


def send_initial_packet(sock):
    initial_packet = "GET /v4/video/jpg/1920x1080/port/1/os/win11.0/obs/29/client/220/nonce/5912/"
    sock.sendall(initial_packet.encode())

def display_image(img_data):
    img = Image.open(BytesIO(img_data))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imshow("Video Stream", img)
    cv2.waitKey(1)  # Adjust the wait time as needed

def save_image(img_data, output_folder, pts):
    img = Image.open(BytesIO(img_data))
    img.save(os.path.join(output_folder, f"frame_{pts}.jpg"))
    logging.info(f"Saved image to {os.path.join(output_folder, f'frame_{pts}.jpg')}.")

def ocr_image(img_data):
    img = Image.open(BytesIO(img_data))
    result = pytesseract.image_to_string(img, config='--psm 6 digits')
    coordinates = pytesseract.image_to_osd(img, output_type=pytesseract.Output.STRING)
    return result, coordinates

def receive_video_feed(host, port, output_folder, display_images, file_output_interval, ocr_mode, ocr_interval, debug):
    # setup_logging(debug)

    # Create a socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        logging.info(f"Connected to {host}:{port}")
        send_initial_packet(sock)  # Send the initial packet
    except ConnectionRefusedError:
        logging.error("Connection refused. Make sure the server is running.")
        return

    last_file_output_time = 0
    last_ocr_time = 0

    try:
        while True:
            header = b''
            while len(header) < 12:
                chunk = sock.recv(12 - len(header))
                if not chunk:
                    logging.error("Connection closed by the server.")
                    break
                header += chunk

            if not header:
                break

            # Extract PTS (8 bytes, big-endian) and length (4 bytes, big-endian)
            pts, length = struct.unpack('>QI', header)
            if debug:
                logging.debug(f"PTS: {pts}, Length: {length}")

            data = b''
            while len(data) < length:
                chunk = sock.recv(length - len(data))
                if not chunk:
                    logging.error("Connection closed by the server.")
                    break
                data += chunk

            if debug:
                logging.debug(f"Received Data Length: {len(data)}")  # Print the length of received data

            if not data:
                break

            current_time = time.time()

            try:
                if display_images:
                    display_image(data)

                if file_output_interval > 0 and current_time - last_file_output_time >= file_output_interval:
                    save_image(data, output_folder, pts)
                    last_file_output_time = current_time

                if ocr_mode and ocr_interval > 0 and current_time - last_ocr_time >= ocr_interval:
                    try:
                        ocr_result, ocr_coordinates = ocr_image(data)
                    except Exception as e:
                        logging.error(f"Error with OCR: {e}")
                    last_ocr_time = current_time
                    logging.info(f"OCR Result: {ocr_result.strip()}")
                    logging.info(f"OCR Coordinates:\n{ocr_coordinates.strip()}")

            except Exception as e:
                logging.error(f"Error handling the image: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture a video stream as JPEG images with various modes")
    parser.add_argument("host", type=str, help="Hostname or IP address of the server")
    parser.add_argument("port", type=int, help="Port number for the server")
    parser.add_argument("--output_folder", type=str, help="Folder to save the images")
    parser.add_argument("--display", action="store_true", help="Display images")
    parser.add_argument("--file_output_interval", type=float, default=0, help="File output interval in seconds (0 for continuous)")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR mode to extract digits and their coordinates")
    parser.add_argument("--ocr_interval", type=float, default=2.5, help="OCR interval in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug verbosity")

    args = parser.parse_args()

    logging.basicConfig(filename='video_capture.log', level=logging.DEBUG if args.debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if args.debug else logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    if not args.display and not args.output_folder and not args.ocr:
        logging.error("You must provide at least one of --display, --output_folder, or --ocr.")
    else:
        if args.output_folder and not os.path.exists(args.output_folder):
            os.makedirs(args.output_folder)

        logging.info(f"Connecting to {args.host}:{args.port}...")
        receive_video_feed(
            args.host,
            args.port,
            args.output_folder,
            args.display,
            args.file_output_interval,
            args.ocr,
            args.ocr_interval,
            args.debug
        )
        logging.info("Video stream capture completed.")
