Module receipt_parser_core.enhancer
===================================

Functions
---------

    
`detect_orientation(image)`
:   

    
`enhance_image(img, high_contrast=True, gaussian_blur=True)`
:   

    
`find_images(folder)`
:   :param folder: str
        Path to folder to search
    :return: generator of str
        List of images in folder

    
`grayscale_image(img)`
:   

    
`main()`
:   

    
`prepare_folders()`
:   :return: void
        Creates necessary folders

    
`process_receipt(config, filename, rotate=True, grayscale=True, gaussian_blur=True)`
:   

    
`remove_noise(img)`
:   

    
`rescale_image(img)`
:   

    
`rotate_image(input_file, output_file, angle=90)`
:   :param input_file: str
        Path to image to rotate
    :param output_file: str
        Path to output image
    :param angle: float
        Angle to rotate
    :return: void
        Rotates image and saves result

    
`run_tesseract(input_file, output_file, language='deu')`
:   :param input_file: str
        Path to image to OCR
    :param output_file: str
        Path to output file
    :return: void
        Runs tesseract on image and saves result

    
`sharpen_image(input_file, output_file, rotate=True)`
:   :param input_file: str
        Path to image to prettify
    :param output_file: str
        Path to output image
    :return: void
        Prettifies image and saves result