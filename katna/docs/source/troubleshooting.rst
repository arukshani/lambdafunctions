Tips and Troubleshooting
------------------------

1) If input image is of very large size ( larger than 2000x2000 ) it might take a
long time to perform Automatic smart cropping.If you encounter this issue, consider changing down_sample_factor
from default 8 to larger values ( like 16 or 32 ). This will decrease processing time 
significantly. 

2) If you get "AttributeError: module 'cv2.cv2' has no attribute 'saliency'" error. then try  
re-installing opencv-contrib

.. code-block:: shell

    python -m pip uninstall opencv-contrib-python 
    python -m pip install opencv-contrib-python

3) If you get "FileNotFoundError: frozen_east_text_detection.pb file not found". Open python shell 
and follow the below commands.

.. code-block:: python

    from Katna.image_filters.text_detector import TextDetector
    td = TextDetector()
    td.download_data()

4) If you are running the code on windows, make sure to create the main file in the 
below format.

.. code-block:: python

    from Katna.video import Video

    def main():
        vd = Video()
        # your code...

    if __name__ == "__main__":
        main()

OR

.. code-block:: python

    from Katna.video import Video

    if __name__ == "__main__":
    
        vd = Video()
        # your code


5) On windows, ensure that anaconda has admin rights if installing with anaconda as it fails with
the write permission while installing some modules.


6) If you get "RuntimeError: No ffmpeg exe could be found. Install ffmpeg on your system, or 
set the IMAGEIO_FFMPEG_EXE environment variable". Go to the **imageio-ffmpeg-*.egg** folder inside your
**site-packages** folder, there's ffmpeg file inside binaries folder set it's path to environment variable.

7) There is a known memory leak issue in Katna version 0.8.2 and less,
    when running video keyframe extraction on Python version 3.6 and 3.7, 
    This might be releated to some multiprocessing bug in Python 3.6 and 3.7 which is fixed in 3.8 and above. Take a look at 
    memory usage graph of python 3.6 and 3.7.

   .. figure:: images/python_3.6_Keyframe_on_30_videos.png
         :width: 100%
         :align: center
         :alt: Memory usage of Keyframe extraction on python 3.6

         Keyframe extraction on python 3.6

   .. figure:: images/python_3.7_Keyframe_on_30_videos.png
         :width: 100%
         :align: center
         :alt: Memory usage of Keyframe extraction on python 3.7
        
         Keyframe extraction on python 3.7     
   
   .. figure:: images/python_3.8_Keyframe_on_30_videos.png
         :width: 100%
         :align: center
         :alt: Memory usage of Keyframe extraction on python 3.8

         Keyframe extraction on python 3.8       
   
   .. figure:: images/python_3.9_Keyframe_on_30_videos.png
         :width: 100%
         :align: center
         :alt: Memory usage of Keyframe extraction on python 3.9       

         Keyframe extraction on python 3.9

If you are running Keyframe extraction code on large number of videos and facing memory issue, request you to upgrade
your katna version to version 0.9 or above. If you still want to use older version of
katna consider upgrading your python version to 3.8 or above.

**Mediapipe Build Issues**

1) If you are unable to run the "hello-world" example for MacOS, refer to the issue reported here: https://github.com/bazelbuild/bazel/issues/8053#issuecomment-490793705 . 
Sometimes the build doesnt work due to openCV version or dependencies on glog.

2) Mediaipie build can also give c++ compilations errors when building using Bazel.
In some situations, this happens due to prtotbuf installation on system wherein Bazel accidentally picks up header files from the system 
when compiling Bazel's checked in Protobuf C++ sources on macOS. The solution is to uninstall protobuf and is 
mentioned over here: https://github.com/bazelbuild/bazel/issues/8053#issuecomment-490793705
