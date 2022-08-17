import tensorflow as tf
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import math


# import numpy as np
# import tensorflow as tf
# import cv2
#
# input = tf.placeholder(dtype=np.uint8, shape=[640, 1024, 3])
#
# trans_op = tf.contrib.image.transform(input, [1, 0, 0, 0, 1, 0, 0, 0])
#
# img = cv2.imread('test.jpg')
# img = cv2.resize(img, (1024, 640))
#
# with tf.Session() as sess:
#     trans_img = sess.run(trans_op, feed_dict={input: img})
#     cv2.imshow('img', trans_img)
# cv2.waitKey()
# cv2.destroyAllWindows()
h=1

def bilinear_sampler(imgs, coords, output_shape):
    """Construct a new image by bilinear sampling from the input image.

    Points falling outside the source image boundary have value 0.

    Args:
      imgs: source image to be sampled from [batch, height_s, width_s, channels]
      coords: coordinates of source pixels to sample from [batch, height_t,
        width_t, 2]. height_t/width_t correspond to the dimensions of the output
        image (don't need to be the same as height_s/width_s). The two channels
        correspond to x and y coordinates respectively.
    Returns:
      A new sampled image [batch, height_t, width_t, channels]
    """

    def _repeat(x, n_repeats):  # tf.cast(tf.range(coord_size[0]), 'float32') * dim1,coord_size[0] * coord_size[1])
        rep = tf.transpose(
            tf.expand_dims(tf.ones(shape=tf.stack([
                n_repeats,
            ])), 1), [1, 0])
        rep = tf.cast(rep, 'float32')
        x = tf.matmul(tf.reshape(x, (-1, 1)), rep)
        return tf.reshape(x, [-1])

    with tf.name_scope('image_sampling'):
        coords_x, coords_y = tf.split(coords, [1, 1], axis=2)
        inp_size = imgs.get_shape()
        coord_size = coords.get_shape()
        out_size = coords.get_shape().as_list()
        out_size[2] = inp_size[2]
        coords_x = tf.cast(coords_x, 'float32')
        coords_y = tf.cast(coords_y, 'float32')

        x0 = tf.floor(coords_x)
        x1 = x0 + 1
        y0 = tf.floor(coords_y)
        y1 = y0 + 1

        y_max = tf.cast(tf.shape(imgs)[0] - 1, 'float32')
        x_max = tf.cast(tf.shape(imgs)[1] - 1, 'float32')
        zero = tf.zeros([1], dtype='float32')

        x0_safe = tf.clip_by_value(x0, zero, x_max)
        y0_safe = tf.clip_by_value(y0, zero, y_max)
        x1_safe = tf.clip_by_value(x1, zero, x_max)
        y1_safe = tf.clip_by_value(y1, zero, y_max)

        ## bilinear interp weights, with points outside the grid having weight 0
        # wt_x0 = (x1 - coords_x) * tf.cast(tf.equal(x0, x0_safe), 'float32')
        # wt_x1 = (coords_x - x0) * tf.cast(tf.equal(x1, x1_safe), 'float32')
        # wt_y0 = (y1 - coords_y) * tf.cast(tf.equal(y0, y0_safe), 'float32')
        # wt_y1 = (coords_y - y0) * tf.cast(tf.equal(y1, y1_safe), 'float32')

        wt_x0 = x1_safe - coords_x
        wt_x1 = coords_x - x0_safe
        wt_y0 = y1_safe - coords_y
        wt_y1 = coords_y - y0_safe

        ## indices in the flat image to sample from
        dim2 = tf.cast(inp_size[1], 'float32')
        dim1 = tf.cast(inp_size[1] * inp_size[0], 'float32')
        batch = tf.constant(1)
        base = tf.reshape(
            _repeat(
                tf.cast(tf.range(batch), 'float32') * dim1,
                coord_size[0] * coord_size[1]),
            [out_size[0], out_size[1], 1])

        base_y0 = base + y0_safe * dim2
        base_y1 = base + y1_safe * dim2
        idx00 = tf.reshape(x0_safe + base_y0, [-1])
        idx01 = x0_safe + base_y1
        idx10 = x1_safe + base_y0
        idx11 = x1_safe + base_y1

        ## sample from imgs
        imgs_flat = tf.reshape(imgs, tf.stack([-1, inp_size[2]]))
        imgs_flat = tf.cast(imgs_flat, 'float32')
        im00 = tf.reshape(tf.gather(imgs_flat, tf.cast(idx00, 'int32')), out_size)
        im01 = tf.reshape(tf.gather(imgs_flat, tf.cast(idx01, 'int32')), out_size)
        im10 = tf.reshape(tf.gather(imgs_flat, tf.cast(idx10, 'int32')), out_size)
        im11 = tf.reshape(tf.gather(imgs_flat, tf.cast(idx11, 'int32')), out_size)

        w00 = wt_x0 * wt_y0
        w01 = wt_x0 * wt_y1
        w10 = wt_x1 * wt_y0
        w11 = wt_x1 * wt_y1

        output = tf.add_n([
            w00 * im00, w01 * im01,
            w10 * im10, w11 * im11
        ])
        return output


def warpperspective(img, perpective, output_shape=None):
    """Inverse warp a source image to the target image plane based on projection.

    Args:
      img: the source image [batch, height_s, width_s, 3]
      depth: depth map of the target image [batch, height_t, width_t]
      pose: target to source camera transformation matrix [batch, 6], in the
            order of tx, ty, tz, rx, ry, rz
      intrinsics: camera intrinsics [batch, 3, 3]
    Returns:
      Source image inverse warped to the target image plane [batch, height_t,
      width_t, 3]
    """
    if output_shape is None:
        output_shape = img.get_shape()

    # Convert pose vector to matrix

    # Construct homogeneous pixel grid coordinates
    pixel_coords = meshgrid(output_shape[0], output_shape[1])
    # Get a 4x4 transformation matrix from 'target' camera frame to 'source'
    # pixel frame.

    src_pixel_coords = transform(pixel_coords, perpective)

    output_img = bilinear_sampler(img, src_pixel_coords, output_shape)

    return src_pixel_coords, output_img


def meshgrid(height, width, is_homogeneous=True):
    """Construct a 2D meshgrid.

    Args:
      batch: batch size
      height: height of the grid
      width: width of the grid
      is_homogeneous: whether to return in homogeneous coordinates
    Returns:
      x,y grid coordinates [batch, 2 (3 if homogeneous), height, width]
    """
    x_t = tf.matmul(tf.ones(shape=tf.stack([height, 1])),
                    tf.transpose(tf.expand_dims(
                        tf.linspace(-1.0, 1.0, width), 1), [1, 0]))
    y_t = tf.matmul(tf.expand_dims(tf.linspace(-1.0, 1.0, height), 1),
                    tf.ones(shape=tf.stack([1, width])))
    x_t = (x_t + 1.0) * 0.5 * tf.cast(width - 1, tf.float32)
    y_t = (y_t + 1.0) * 0.5 * tf.cast(height - 1, tf.float32)
    if is_homogeneous:
        ones = tf.ones_like(x_t)
        coords = tf.stack([x_t, y_t, ones], axis=0)
    else:
        coords = tf.stack([x_t, y_t], axis=0)

    return coords


def transform(cam_coords, proj):
    """Transforms coordinates in a camera frame to the pixel frame.

    Args:
      cam_coords: [3, height, width]
      proj: [3*3][[a1,a2,a3][b1,b2,b3][0,0,1]]
    Returns:
      Pixel coordinates projected from the camera frame [batch, height, width, 2]
    """
    shape = tf.shape(cam_coords)
    height = shape[1]
    width = shape[2]

    cam_coords = tf.reshape(cam_coords, [3, -1])  # [3,height*width]
    unnormalized_pixel_coords = tf.matmul(proj, cam_coords)
    x_u = tf.slice(unnormalized_pixel_coords, [0, 0], [1, -1])
    y_u = tf.slice(unnormalized_pixel_coords, [1, 0], [1, -1])

    pixel_coords = tf.concat([x_u, y_u], axis=0)
    pixel_coords = tf.reshape(pixel_coords, [2, height, width])
    return tf.transpose(pixel_coords, perm=[1, 2, 0])

def test():
    if h==0:
        return tf.constant(1)
    else:
        return tf.constant(2)

def M2T_tf(M):
    scale = tf.sqrt(M[0, 0] ** 2 + M[0, 1] ** 2)
    rotation = tf.atan(M[1, 0] / M[0, 0])
    rotation = rotation / math.pi * 180
    x = M[0, 2]
    y = M[1, 2]
    return tf.Variable([x, y, rotation, scale])


def main():
    img = cv.imread("test.jpg")
    M = np.mat([[-9.99964605e-01, -8.41362556e-03, 2.12364632e+03],
                [8.41362556e-03, -9.99964605e-01, 8.32779971e+02],
                [0, 0, 1]])
    a_tf = M2T_tf(M)

    img_cv = cv.warpPerspective(img, M, (1500, 999))
    # result of cv-perspective

    input = tf.constant(img, name='input', dtype=tf.float32)
    a = tf.Variable(M)
    a = tf.cast(a, 'float32')

    vector = [a]

    coord, train_op = warpperspective(input, a, output_shape=[866, 1301])
    # (3*3)M:[[-9.99964605e-01, -8.41362556e-03, 2.12364632e+03],[8.41362556e-03, -9.99964605e-01, 8.32779971e+02],[0, 0, 1]]
    # ---------------------->8_dims-vector :[-9.99964605e-01, -8.41362556e-03, 2.12364632e+03, 8.41362556e-03,-9.99964605e-01, 8.32779971e+02, 0, 0]

    a = tf.Variable(2)
    b = tf.constant(3)
    x = tf.constant(4)
    y = tf.constant(5)
    z = tf.multiply(a, b)
    result = tf.cond(x <= 0, lambda: tf.add(x, z), lambda: tf.square(y))

    test_res=test()
    output_img = tf.cast(train_op, tf.uint8)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        coord_img = sess.run(coord)
        result = sess.run(z)
        test_res1=sess.run(test_res)

        global h
        h=0
        test_res2=sess.run(test())
        trans_img = sess.run(output_img)
        plt.figure(1)
        plt.imshow(trans_img)
        plt.show()

    plt.figure(2)
    plt.imshow(trans_img)

    plt.imshow(img_cv)
    plt.show()


if __name__ == '__main__':
    main()
