from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.wcs import WCS
from matplotlib import colormaps


def make_line(user_file_path, angle, xlim=None, ylim=None, wcs_xlim=None, wcs_ylim=None, image_lim_x=None, image_lim_y=None, image_start_x=None, image_start_y=None):

  with fits.open(user_file_path) as hdul:
    hdul.info()
    primary_hdu_user = hdul[0]
    head_user = primary_hdu_user.header
    image_data_user = primary_hdu_user.data
  image_data_squeezed_user = np.squeeze(image_data_user)

  if image_lim_x is not None:
    image_limit_x = image_lim_x
  else:
    image_limit_x = head_user['NAXIS1']

  if image_lim_y is not None:
    image_limit_y = image_lim_y
  else:
    image_limit_y = head_user['NAXIS2']

  if image_start_x is not None:
    image_startcrop_x = image_start_x
  else:
    image_startcrop_x = 0

  if image_start_y is not None:
    image_startcrop_y = image_start_y
  else:
    image_startcrop_y = 0

  image_data_squeezed_user_cut = image_data_squeezed_user[image_startcrop_y:image_limit_y, image_startcrop_x:image_limit_x]

  if wcs_xlim is not None:
    xlim = 'unknown'
  if wcs_ylim is not None:
    ylim = 'unknown'

  highest = -np.inf
  for coords_y, col in enumerate(image_data_squeezed_user):
    for coords_x, val in enumerate(col):
      if val > highest:
        highest = val
        centre = [coords_y, coords_x]

  if type(user_file_path) is not str:
    raise TypeError("File path must be string")

  if type(angle) is not int and type(angle) is not float:
    raise ValueError("angle must be an interger of float")

  if type(xlim) is int and type(ylim) is int:
    xlim = xlim
    ylim = ylim

  elif xlim is None and type(ylim) is int:
    ylim = ylim
    xlim = image_limit_x

  elif type(xlim) is int and ylim is None:
    xlim = xlim
    ylim = image_limit_y

  elif xlim is None and ylim is None:
    ylim = image_limit_y
    xlim = image_limit_x

  else:
    raise TypeError("x or y or both are unsuitable datatypes. Check is they are both integers")

  if xlim > image_limit_x:
    raise ValueError("'xlim' must be less than or equal to the number of pixels in the (possibly cropped) image")

  if ylim > image_limit_y:
    raise ValueError("'ylim' must be less than or equal to the number of pixels in the (possibly cropped) image")

  vertical = ''

  if (angle % 180) == 90:
    vertical = 'yes'
  else:
    endp = centre[0] + (np.tan(np.deg2rad(angle))) * (xlim - centre[1])
    gradient = (endp - centre[0])/(xlim - centre[1])
    vertical = 'no'

  list_pix_x = []
  list_pix_y = []
  pix_x = centre[1]
  prev_pix_y = centre[0]

  if vertical == 'no':
    if xlim < pix_x and ylim < prev_pix_y:
      while pix_x > xlim and prev_pix_y > ylim and prev_pix_y > 0 and pix_x > 0:
        list_pix_x.append(pix_x)
        list_pix_y.append(prev_pix_y - gradient)
        prev_pix_y = prev_pix_y - gradient
        pix_x -= 1
        if prev_pix_y < ylim or prev_pix_y < image_startcrop_y or pix_x < xlim or pix_x < image_startcrop_x:
          list_pix_y.remove(prev_pix_y)
          list_pix_x.remove(pix_x+1)

    elif xlim < pix_x and ylim > prev_pix_y:
      while xlim < pix_x and prev_pix_y < ylim and prev_pix_y > 0 and pix_x > 0:
        list_pix_x.append(pix_x)
        list_pix_y.append(prev_pix_y + gradient)
        prev_pix_y = prev_pix_y + gradient
        pix_x -= 1
        if prev_pix_y > ylim or prev_pix_y > image_limit_y or pix_x < xlim or pix_x < image_startcrop_x:
          list_pix_y.remove(prev_pix_y)
          list_pix_x.remove(pix_x+1)

    elif xlim > pix_x and ylim < prev_pix_y:
      while xlim > pix_x and prev_pix_y > ylim and prev_pix_y > 0 and pix_x > 0:
        list_pix_x.append(pix_x)
        list_pix_y.append(prev_pix_y - gradient)
        prev_pix_y = prev_pix_y - gradient
        pix_x += 1
        if prev_pix_y < ylim or prev_pix_y < image_startcrop_y or pix_x > xlim or pix_x > image_limit_x:
          list_pix_y.remove(prev_pix_y)
          list_pix_x.remove(pix_x-1)

    else:
      while pix_x < xlim and prev_pix_y < ylim and prev_pix_y > 0 and pix_x > 0:
        list_pix_x.append(pix_x)
        list_pix_y.append(prev_pix_y + gradient)
        prev_pix_y = prev_pix_y + gradient
        pix_x += 1
        if prev_pix_y > ylim or prev_pix_y > image_limit_y or pix_x > xlim or pix_x > image_limit_x:
          list_pix_y.remove(prev_pix_y)
          list_pix_x.remove(pix_x-1)

  else:
    if ylim > prev_pix_y and angle < 0:
      print('Warning: Angle being changed to +90')
      angle = 90

    elif ylim < prev_pix_y and angle > 0:
      print('Warning: Angle being changed to -90')
      angle = -90

    if ylim < prev_pix_y and angle < 0:
      while ylim <= prev_pix_y and prev_pix_y > 0:
        list_pix_x.append(pix_x)
        list_pix_y.append(prev_pix_y)
        prev_pix_y -= 1
        if prev_pix_y < (ylim-1) or prev_pix_y < 1:
          list_pix_x.remove(pix_x)
          list_pix_y.remove(prev_pix_y + 1)

    else:
      while ylim >= prev_pix_y and prev_pix_y > 0:
        list_pix_x.append(pix_x)
        list_pix_y.append(prev_pix_y)
        prev_pix_y += 1
        if prev_pix_y > (ylim-1) or prev_pix_y > image_limit_y:
          list_pix_x.remove(pix_x)
          list_pix_y.remove(prev_pix_y - 1)

  pix_y_del = []
  pix_x_del = []
  for idx, row in enumerate(list_pix_y):
    if row > image_limit_y:
      pix_y_del.append(idx)
    elif row < image_startcrop_y:
      pix_y_del.append(idx)
    else:
      continue

  for i in pix_y_del:
    list_pix_y.pop(i)
    list_pix_x.pop(i)

  for idx, row in enumerate(list_pix_y):
    list_pix_y[idx] = np.abs(row - image_startcrop_y)
    
  for idx, col in enumerate(list_pix_x):
    if col > image_limit_x:
      pix_x_del.append(idx)
    elif col < image_startcrop_x:
      pix_x_del.append(idx)
    else:
      continue

  for i in pix_x_del:
    list_pix_x.pop(i)
    list_pix_y.pop(i)

  for idx, col in enumerate(list_pix_x):
    list_pix_x[idx] = np.abs(col - image_startcrop_x)

  list_pix_x.pop()
  list_pix_y.pop()

  fig = plt.figure(figsize=(10, 8))
  ax = fig.add_subplot(111)
  im = ax.imshow(image_data_squeezed_user_cut, cmap='inferno', origin='lower', vmin=np.min(image_data_squeezed_user),
                 vmax=np.max(image_data_squeezed_user))

  ax.set_title("Image with line")

  plt.plot(list_pix_x, list_pix_y)

  fig1 = fig  # captured instead of plt.show()

  vals_on_line = []

  for x, y in zip(list_pix_x, list_pix_y):
    vals_on_line.append(image_data_squeezed_user_cut[int(round(y)), x])

  dist = []
  x1 = centre[1]
  y1 = centre[0]
  for x2, y2 in zip(list_pix_x, list_pix_y):
    dist.append(np.abs(np.sqrt((x2 - x1)**2 + (y2 - y1)**2)))

  fig = plt.figure(figsize=(10, 6))
  ax = fig.add_subplot(111)
  ax.plot(dist, vals_on_line)
  ax.set_xlabel('Distance from star in pixels', fontsize = 18)
  ax.set_ylabel('Pixel intensity', fontsize = 18)
  ax.tick_params(labelsize=20)
  ax.set_title('Radial Intensity Profile')

  fig2 = fig  # captured instead of plt.show()

  return fig1, fig2, dist, vals_on_line