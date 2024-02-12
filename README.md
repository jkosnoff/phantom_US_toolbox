# phantom_US_toolbox
A toolbox for analyzing code from phantom ultrasound experiments. The equations are based off of the original Matlab code by Kai Yu.

To install, make sure that you have Python downloaded. I use Anaconda as my Python manager, but there are plenty of options out there. Once you have Python downloaded, download this code package. In terminal (on Macs; Anaconda Powershell or equivalent on Windows), navigate to this folder's directory (cd /path/to/phantom_US_toolbox-main). Install the needed packages by running:

**pip install -r requirements.txt**

Open the US_GUI.py program. You can either do this by opening the file in an IDE (such as Spyder, Visual Studio, etc) or through terminal (/Powershell). If you are doing it through terminal, navigate into the phantom_US_toolbox folder and type the following:

**python US_GUI.py**

You should see the following: 

<img width="216" alt="Screenshot 2024-02-09 at 4 12 07 PM" src="https://github.com/jkosnoff/phantom_US_toolbox/assets/70274595/a54806d8-37f4-4aac-a26b-ae24605c9d08">

Copy and paste the path to your tdms file into the box (on a Mac, you can get your file path by navigating to the file in Finder > option + right click > Copy __ as Path Name). **IMPORTANT: DO NOT CHANGE THE TDMS FILE NAME** This script has been designed to parse through the file name to extract the important information embedded into it. 

Click on "Parse File." You should see something similar to the following, where the values and names are replaced with your specific experimental parameters. The one exception (currently) is the input mV parameter may need to be manually input. I will look to resolve this bug in the future. Stay tuned for future updates 🙌.

<img width="222" alt="Screenshot 2024-02-09 at 4 18 39 PM" src="https://github.com/jkosnoff/phantom_US_toolbox/assets/70274595/880f96ae-3917-427b-bd70-82f7465a28dd">

Confirm that all the data in the boxes is correct and click on "Analyze Data." After a moment (maybe a few moments, depending on the size of the file and your computer), you should see a new window, similar to the following: 

<img width="741" alt="Screenshot 2024-02-09 at 4 26 35 PM" src="https://github.com/jkosnoff/phantom_US_toolbox/assets/70274595/d0240905-12c9-421d-b281-a016346227ce">

Here you have the option to plot different slices of the scan. Select "Pressure" to see a pressure map, and/or "Intensity" to see an intensity map. Select XY or XY to see the respective views. Selecting "Focal Point" will automatically show you the point of highest pressure/intensity, whereas all plotting locations will give you all the slices. Here's an example: 

![image](https://github.com/jkosnoff/phantom_US_toolbox/assets/70274595/472ef5bf-e8fb-4791-8577-4f915362748a)

If you want a little more freedom to play around with the data, the data extraction functions are all in phantom_US_toolbox.py. I am currently considering a function to automatically calculate the *derated* intensities (this is a bit tricky though because the transducer is not guaranteed to be the center of the scanning of the scanning field) or to plot a 3D shape of the US beam (see Legon 2014 for an example of this), but these are currently not supported. Please feel free to reach out and ask me for questions about making the plots a little more publication ready (changes in font style, resolution, different layouts, etc); I may include this automatically in the future. For now, though, these provide a quick way to visually inspect the data. 

**Other important note**: Do not change or modify the other .txt file. This is the hydrophone calibration file. If we get a new hydrophone or an updated calibration, we *should* just be able to replace the old file with the new, but this has not been tested so there may be some bugs to work out when the time comes.

Cheers!
