from music_classes import Staff

import cv2
import numpy as np


SHEET_PATH = "/app/sheets/"
FILE_NAME = "wheels_on_the_bus_0.png"

LINE_THRESHOLD = 0.2
MASK_PIXEL_TOLERANCE = 100


def apply_preprocess(img):

    #Binarize
    _, binary = cv2.threshold(
        img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    #Noise Removal (Optional)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return binary

def find_staffs(binary):

    #vertical dilation for staff line detection
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    binary = cv2.dilate(binary, kernel)

    height, width = binary.shape

    line_candidates = []

    line_threshold = int(LINE_THRESHOLD * width)

    #detect lines
    for y in range(height):

        row = binary[y]

        run_start = None
        run_length = 0

        for x in range(width):

            if row[x] != 0:
            
                if run_start is None:
                    run_start = x
                    run_length = 1
            
                else:
                    run_length += 1
            
            else:
            
                if run_length >= line_threshold:
                    line_candidates.append((y, run_start, run_length))
            
                run_start = None
                run_length = 0

        # catch run ending at row end
        if run_length >= line_threshold:
            line_candidates.append((y, run_start, run_length))

    #collapse multiple strips into single lines
    last_candidate = (0,0,0)
    lines = []

    for n in range(len(line_candidates)):

        if line_candidates[n][0] == last_candidate[0] + 1: 
            lines[-1].append(line_candidates[n])

        else:
            lines.append([line_candidates[n]])
        
        last_candidate = line_candidates[n]
    
    staffs = []

    for x in range(0, len(lines), 5):

        staffs.append(Staff(lines[x:x+5]))

    return staffs


def apply_mask(binary, staffs):

    mask = np.zeros_like(binary)

    top = max(0, staffs[0].center - MASK_PIXEL_TOLERANCE)
    bottom = min(binary.shape[0], staffs[-1].center + MASK_PIXEL_TOLERANCE)

    mask[top:bottom, :] = 255

    filtered_binary = cv2.bitwise_and(binary, mask)

    return filtered_binary


def remove_staff_lines(filtered_binary,staffs):

    stripped_binary = filtered_binary.copy()
    h,w = stripped_binary.shape

    max_thickness = max(staffs, key=lambda obj: obj.max_thickness).max_thickness

    v_window = int(max_thickness/2) + 1
    h_window = 2

    for staff in staffs:
        for line in staff.lines:

            line_ys = [strip[0] for strip in line]

            for (y, x_start, length) in line:
                for x in range(x_start, x_start + length):

                    keep = False

                    for dy in range(-v_window, v_window + 1):
                        for dx in range(-h_window, h_window + 1):

                            ny = y + dy
                            nx = x + dx

                            if 0 <= ny < h and 0 <= nx < w and ny not in line_ys:
                                if stripped_binary[ny,nx] != 0:
                                    keep = True
                                    break
                        
                        if keep:
                            break

                    if not keep:
                        stripped_binary[y,x] = 0

    return stripped_binary


def extract_symbols(stripped_binary, staffs):

    #vertical dilation for symbol extraction
    max_thickness = max(staffs, key=lambda obj: obj.max_thickness).max_thickness
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 3))
    binary = cv2.dilate(stripped_binary, kernel)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        binary, connectivity=8
    )

    for i in range(1, num_labels):  # skip background
        x, y, w, h, area = stats[i]

        if area < 50:
            continue  # filter tiny noise

        symbol_img = binary[y:y+h, x:x+w]

        closest_staff = (0, 999)

        for i_2 in range(len(staffs)):
            if abs(staffs[i_2].center - y) < closest_staff[1]:
                closest_staff = (i_2, abs(staffs[i_2].center - y))

        staffs[closest_staff[0]].symbols.append({
            
            "bbox": (x, y, w, h),
            "area": area,
            "image": symbol_img
        })
    
    for staff in staffs:
        staff.order_symbols()


if __name__ == "__main__":

    img = cv2.imread(SHEET_PATH + FILE_NAME, cv2.IMREAD_GRAYSCALE)

    binary = apply_preprocess(img)

    cv2.imwrite(SHEET_PATH + "binary.jpg", binary)

    staffs = find_staffs(binary)

    filtered_binary = apply_mask(binary, staffs)

    cv2.imwrite(SHEET_PATH + "filtered_binary.jpg", filtered_binary)

    stripped_binary = remove_staff_lines(filtered_binary, staffs)

    cv2.imwrite(SHEET_PATH + "stripped_binary.jpg", stripped_binary)

    extract_symbols(stripped_binary, staffs)

    for i, s in enumerate(staffs[0].symbols):
        cv2.imwrite(f"symbols/symbol_{i}.png", s["image"])

'''
debug = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

for top, bottom in music_regions:
    cv2.rectangle(
        debug,
        (0, top),
        (debug.shape[1], bottom),
        (0, 255, 0),
        2
    )

cv2.imwrite("debug_mask_regions.png", debug)
    '''