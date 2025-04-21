from PIL import Image # Image module in the Python Imaging Library (PIL - pillow)
import numpy as np # numpy is a fundamental package for scientific computing
import os # os module is used for file and directory operations

# Function that reads a PIL image from a file with a given path
def read_image_from_file(img_file_path):
    img = Image.open(img_file_path)
    return img

# Function that writes a given PIL image to a file with a given path
def write_image_to_file(img, img_file_path):
    img.save(img_file_path, 'bmp') # save as a bmp image (an uncompressed format)

# Function that converts a given color image (RGB) to grayscale
def color_to_gray(img): # img is a PIL image
    img_gray = img.convert('L')
    return img_gray

# Function that converts a given PIL image to a numpy array
def PIL_to_np(img):
   img_array = np.array(img)
   return img_array

# Function that converts a given numpy array to a PIL image
def np_to_PIL(img_array):
   img = Image.fromarray(np.uint8(img_array))
   return img

def demo():
    # get the current directory where this program is placed
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # read a color (RGB) image from a file
    input_file_path = current_directory + '/panda.bmp'
    color_image = read_image_from_file(input_file_path)
    # print the numbers of the rows and the columns in the image
    num_cols = color_image.size[0]
    num_rows = color_image.size[1]
    print("Num rows:", num_rows, "and Num cols:", num_cols)
    # display the color image
    color_image.show()

    # convert the color image to a numpy array
    image_array = PIL_to_np(color_image)
    # print information on the shape of the array
    print("Array shape (RGB): ", image_array.shape)
    # convert the numpy array back to a PIL image
    color_image2 = np_to_PIL(image_array)
    # display the image
    color_image2.show()

    # convert the color image to grayscale
    grayscale_image = color_to_gray(color_image)
    # display the grayscale image
    grayscale_image.show()
    # write the grayscale image to a file
    output_file_path = current_directory + '/panda_grayscale.bmp'
    write_image_to_file(grayscale_image, output_file_path)

    # convert the grayscale image to a numpy array
    image_array = PIL_to_np(grayscale_image)
    # print information on the shape of the array
    print("Array shape (grayscale): ", image_array.shape)
    # convert the numpy array back to a PIL image
    grayscale_image2 = np_to_PIL(image_array)
    # display the image
    grayscale_image2.show()

if __name__ == "__main__":
    demo()
