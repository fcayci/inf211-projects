import flask
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect, url_for

from ast import literal_eval


def generate_random(row, column):
    from random import randint

    x = []
    for i in range(row):
        y = []
        for j in range(column):
            y.append(
                    {'red': randint(0, 255),
                     'green': randint(0, 255),
                     'blue': randint(0, 255)})
        x.append(y)
    return x


def convert_to_image(s):
    s = literal_eval(s).strip()
    lines = s.split('\n')
    a = []
    for line in lines:
        b = line.split(',')
        y = []
        for pixel in b:
            y.append(
                    {'red': int(pixel[:2], 16),
                    'green': int(pixel[2:4], 16),
                    'blue': int(pixel[4:], 16)})
        a.append(y)

    return a


def clear(img):
    for i in range(len(img)):
        for j in range(len(img[0])):
            img[i][j]['red'] = 0
            img[i][j]['green'] = 0
            img[i][j]['blue'] = 0


def set_value(img, value, channel='rgb'):
    for i in range(len(img)):
        for j in range(len(img[0])):
            if 'r' in channel:
                img[i][j]['red'] = value
            if 'g' in channel:
                img[i][j]['green'] = value
            if 'b' in channel:
                img[i][j]['blue'] = value

def fix_pix(v):
    if v < 0:
        return 0
    elif v > 255:
        return 255
    else:
        return round(v)


def fix(img):
    for i in range(len(img)):
        for j in range(len(img[0])):
            img[i][j]['red'] = fix_pix(img[i][j]['red'])
            img[i][j]['green'] = fix_pix(img[i][j]['green'])
            img[i][j]['blue'] = fix_pix(img[i][j]['blue'])

def mirror_x(img):
    for i in range(len(img)):
        img[i].reverse()

def mirror_y(img):
    img.reverse()

def rotate90(img):
    r = len(img)
    c = len(img[0])
    a = []
    for i in range(c):
        b = []
        for j in range(r-1, -1, -1):
            b.append(img[j][i])
        a.append(b)
    return a

def rotate180(img):
    a = rotate90(img)
    return rotate90(a)

def rotate270(img):
    a = rotate90(img)
    a = rotate90(a)
    return rotate90(a)

def enhance(img, value, channel='rgb'):
    for i in range(len(img)):
        for j in range(len(img[0])):
            if 'r' in channel:
                img[i][j]['red'] = fix_pix(img[i][j]['red'] * value)
            if 'g' in channel:
                img[i][j]['green'] = fix_pix(img[i][j]['green'] * value)
            if 'b' in channel:
                img[i][j]['blue'] = fix_pix(img[i][j]['blue'] * value)


def display(img):
    import matplotlib.pyplot as plt

    img[i][j]['red'] = fix_pix(img[i][j]['red'] * value)
    if 'g' in channel:
        img[i][j]['green'] = fix_pix(img[i][j]['green'] * value)
    if 'b' in channel:
        img[i][j]['blue'] = fix_pix(img[i][j]['blue'] * value)


    plt.imshow(img)
    plt.show()

def grayscale(img, mode=1):
    x = []
    for i in range(len(img)):
        y = []
        for j in range(len(img[0])):
            if mode == 1:
                val = round( (img[i][j]['red'] + img[i][j]['green'] + img[i][j]['blue']) / 3)
            if mode == 2:
                val = round( 0.299 * img[i][j]['red'] + 0.587 * img[i][j]['green'] + 0.114 * img[i][j]['blue'])
            if mode == 3:
                val = round( 0.2126 * img[i][j]['red'] + 0.7152 * img[i][j]['green'] + 0.0722 * img[i][j]['blue'])
            if mode == 4:
                val = round( 0.2627 * img[i][j]['red'] + 0.678 * img[i][j]['green'] + 0.0593 * img[i][j]['blue'])
            # y.append(val)
            y.append({'red':val, 'green':val, 'blue': val})

        x.append(y)
    return x

def get_freq(img, channel='rgb', bin_size=16):

    r = len(img)
    c = len(img[0])

    if 'r' in channel:
        rr = [0] * (256/bin_size)
    if 'g' in channel:
        gg = [0] * (256/bin_size)
    if 'b' in channel:
        bb = [0] * (256/bin_size)

    for i in range(r):
        for j in range(c):
            if 'r' in channel:
                rr[img[i][j]['red'] // bin_size] += 1
            if 'g' in channel:
                gg[img[i][j]['red'] // bin_size] += 1
            if 'b' in channel:
                bb[img[i][j]['red'] // bin_size] += 1
    x = {}
    x['bin_size'] = bin_size
    if 'r' in channel:
        x['red'] = rr
    if 'g' in channel:
        x['green'] = gg
    if 'b' in channel:
        x['blue'] = bb

    return x

def scale_up_crapy(img, N):
    r = len(img)
    c = len(img[0])

    a = []
    for i in range(r):
        b = []
        for j in range(c):
            sr = img[i][j]['red']
            sg = img[i][j]['green']
            sb = img[i][j]['blue']

            for _ in range(N):
                b.append({'red':sr, 'green':sg, 'blue':sb})

        for _ in range(N):
            a.append(b)

    return a


def scale_down(img, N):
    r = len(img)
    c = len(img[0])

    a = []
    for i in range(0, r, N):
        b = []
        for j in range(0, c, N):

            sr, sg, sb = 0, 0, 0
            for ii in range(N):
                for jj in range(N):
                    sr += img[min(i+ii, r-1)][min(j+jj, c-1)]['red']
                    sg += img[min(i+ii, r-1)][min(j+jj, c-1)]['green']
                    sb += img[min(i+ii, r-1)][min(j+jj, c-1)]['blue']
            sr = round(sr / (N**2))
            sg = round(sg / (N**2))
            sb = round(sb / (N**2))
            b.append({'red':sr, 'green':sg, 'blue':sb})
        a.append(b)

    return a


def apply_filter(img, window):
    r = len(img)
    c = len(img[0])

    ws = len(window)

    a = []
    for i in range(r):
        b = []
        for j in range(c):

            sr, sg, sb = 0, 0, 0
            for ii in range(-ws//2 + 1, ws//2 + 1):
                for jj in range(-ws//2 + 1, ws//2 + 1):
                    idx = min( max(0, i+ii), r-1)
                    jdx = min( max(0, j+jj), c-1)
                    sr += img[idx][jdx]['red']*window[ii+ws//2][jj+ws//2]
                    sg += img[idx][jdx]['green']*window[ii+ws//2][jj+ws//2]
                    sb += img[idx][jdx]['blue']*window[ii+ws//2][jj+ws//2]

            sr = fix_pix(sr)
            sg = fix_pix(sg)
            sb = fix_pix(sb)
            b.append({'red':sr, 'green':sg, 'blue':sb})
        a.append(b)

    return a


def write_to_file(img, filename='hede.txt'):
    s = ''
    for i in range(len(img)):
        for j in range(len(img[0])):
            s += "{:02x}".format(img[i][j]['red']) + "{:02x}".format(img[i][j]['green']) + "{:02x}".format(img[i][j]['blue']) 
            s += ','
        s = s[:-1] # last comma
        s += '\n'

    with open(filename, 'w') as f:
        f.write(s)

def convert_to_string(img):
    s = ''
    for i in range(len(img)):
        for j in range(len(img[0])):
            s += "{:02x}".format(img[i][j]['red']) + "{:02x}".format(img[i][j]['green']) + "{:02x}".format(img[i][j]['blue']) 
            s += ','
        s = s[:-1] # last comma
        s += '\n'
    return s



def read_from_png():
    try:
        import cv2
    except:
        print("install opencv")
        exit()

    x = cv2.imread('image7.png')
    y = x.copy()
    r = x[:,:,2].tolist()
    g = x[:,:,1].tolist()
    b = x[:,:,0].tolist()

    a = []
    for i in range(len(r)):
        z = []
        for j in range(len(r[0])):
            z.append(
                    {'red': r[i][j],
                     'green': g[i][j],
                     'blue': b[i][j]} )
        a.append(z)
    return a


app = Flask(__name__)

img = read_from_png()
# img = generate_random(5, 5)

@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'GET':
        img2 = scale_down(img, 1)

        x = repr(convert_to_string(img2))
        return render_template('image.html', img=x)

    else:
        comm = request.form['command']

        if comm == 'Reset':
            return redirect(url_for('start'))

        if comm == 'Scale Up':
            N = int(request.form['scaleup'])
            img2 = convert_to_image(request.form['image'])
            img2 = scale_up_crapy(img2, N)

        if comm == 'Scale Down':
            N = int(request.form['scaledown'])
            img2 = convert_to_image(request.form['image'])
            img2 = scale_down(img2, N)

        if comm == 'Clear':
            img2 = convert_to_image(request.form['image'])
            clear(img2)

        if comm == 'Generate Random Image':
            # img2 = convert_to_image(request.form['image'])
            row = int(request.form['rows'])
            col = int(request.form['columns'])
            img2 = generate_random(row, col)

        if comm == 'Set':
            img2 = convert_to_image(request.form['image'])
            try:
                N = int(request.form['setvalue'])
            except ValueError:
                N = 100
            set_value(img2, N)

        if comm == 'Enhance':
            img2 = convert_to_image(request.form['image'])
            try:
                N = int(request.form['enhancevalue'])
            except ValueError:
                N = 20
            N /= 10

            enhance(img2, N)

        if comm == 'Grayscale':
            img2 = convert_to_image(request.form['image'])
            N = int(request.form['mode'])
            img2 = grayscale(img2, N)

        if comm == 'Mirror X':
            img2 = convert_to_image(request.form['image'])
            mirror_x(img2)

        if comm == 'Mirror Y':
            img2 = convert_to_image(request.form['image'])
            mirror_y(img2)

        if comm == 'Rotate 90':
            img2 = convert_to_image(request.form['image'])
            img2 = rotate90(img2)

        if comm == 'Rotate 180':
            img2 = convert_to_image(request.form['image'])
            img2 = rotate180(img2)

        if comm == 'Rotate 270':
            img2 = convert_to_image(request.form['image'])
            img2 = rotate270(img2)

        if comm == "Identity":
            img2 = convert_to_image(request.form['image'])
            N = int(request.form['windowsize'])
            if N == 5:
                window = [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0]]
            else:
                window = [
                    [0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0]]

            img2 = apply_filter(img2, window)

        if comm == "Box Blur":
            img2 = convert_to_image(request.form['image'])
            N = int(request.form['windowsize'])
            if N == 5:
                window = [
                    [1/25, 1/25, 1/25, 1/25, 1/25],
                    [1/25, 1/25, 1/25, 1/25, 1/25],
                    [1/25, 1/25, 1/25, 1/25, 1/25],
                    [1/25, 1/25, 1/25, 1/25, 1/25],
                    [1/25, 1/25, 1/25, 1/25, 1/25]]
            else:
                window = [
                    [1/9, 1/9, 1/9],
                    [1/9, 1/9, 1/9],
                    [1/9, 1/9, 1/9]]

            img2 = apply_filter(img2, window)

        if comm == "Gaussian Blur":
            img2 = convert_to_image(request.form['image'])
            N = int(request.form['windowsize'])
            if N == 5:
                window = [
                    [1/256,  4/256,  6/256,  4/256, 1/256],
                    [4/256, 16/256, 24/256, 16/256, 4/256],
                    [6/256, 24/256, 36/256, 24/256, 6/256],
                    [4/256, 16/256, 24/256, 16/256, 4/256],
                    [1/256,  4/256,  6/256,  4/256, 1/256]]

            else:
                window = [
                    [1/16, 2/16, 1/16],
                    [2/16, 4/16, 2/16],
                    [1/16, 2/16, 1/16]]

            img2 = apply_filter(img2, window)


        if comm == "Sharpen":
            img2 = convert_to_image(request.form['image'])
            window = [
                [0,  -1,  0],
                [-1,  5, -1],
                [0,  -1,  0]]

            img2 = apply_filter(img2, window)


        if comm == "Edge Detect":
            img2 = convert_to_image(request.form['image'])
            window = [
                [-1, -1, -1],
                [-1,  8, -1],
                [-1, -1, -1]]

            img2 = apply_filter(img2, window)


        return render_template('image.html', img=repr(convert_to_string(img2)))

if __name__ == "__main__":
    app.secret_key = '12345'
    app.run(host="0.0.0.0", port=5001, debug=False)
