# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import tensorflow as tf

# read raw data of image
image_raw_data = tf.gfile.FastGFile("/home/liuxun/Clobotics/Data/DPData/cat13.jpg",'r').read()

with tf.Session() as sess:
    #decode jpg to get 3-D's raw data
    img_data = tf.image.decode_jpeg(image_raw_data)
    
    print img_data.eval()
    
    
    #convert img_data's data to float to do image handling
    img_data = tf.image.convert_image_dtype(img_data, dtype=tf.float32)
    
    #plt.imshow(img_data.eval())
    
    #resized = tf.image.resize_images(img_data, [300, 300], method=2)
    #print resized.get_shape()
    
    #cliped = tf.image.resize_image_with_crop_or_pad(img_data, 2000, 2000)
    
    #central_cropped = tf.image.central_crop(img_data, 0.2)
    
    #turn image up to down
    #flipped = tf.image.flip_up_down(img_data)
    
    #turn image left ot right
    #flipped = tf.image.flip_left_right(img_data)
    
    #transpose image
    #transposed = tf.image.transpose_image(img_data)
    
    # turn image up to down randomly
    #flipped = tf.image.random_flip_up_down(img_data)
    
    #adjust brightness
    #adjusted = tf.image.adjust_brightness(img_data, 0.1)
    
    #adjust contrast
    #adjusted = tf.image.adjust_contrast(img_data, 5)
    
    #adjust hue
    #adjusted = tf.image.adjust_hue(img_data, 0.2)
    
    #adjust saturation
    #adjusted = tf.image.adjust_saturation(img_data, 5)
    
    #standardization
    #adjusted = tf.image.per_image_standardization(img_data)
    
    #plt.imshow(adjusted.eval())
    #plt.show()

    #resized = tf.image.convert_image_dtype(resized, dtype=tf.uint8)
    
    #encode the img_data to jpg and store it
    #encoded_image = tf.image.encode_jpeg(resized)
    #with tf.gfile.GFile("/home/liuxun/Clobotics/Data/DPData/cat13_resized_2.jpg","wb") as f:
        #f.write(encoded_image.eval())
        
        
    img_data = tf.image.resize_images(img_data, [180, 267], method=1)
    
    batched = tf.expand_dims(tf.image.convert_image_dtype(img_data, tf.float32), 0)
    
    boxes = tf.constant([[0.05, 0.05, 0.9, 0.7], [0.35, 0.47, 0.5, 0.56]])
    
    result = tf.image.draw_bounding_boxes(batched, boxes)
    
    print result.get_shape()
    
    result = tf.image.convert_image_dtype(result, tf.float32)
    
    plt.imshow(result.eval())
    plt.show()