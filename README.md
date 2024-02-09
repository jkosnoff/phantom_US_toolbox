# phantom_US_toolbox
A toolbox for analyzing code from phantom ultrasound experiments

To install, make sure that you have Python downloaded. I use Anaconda as my Python manager, but there are plenty of options out there. Once you have Python downloaded, download this code package. In terminal (on Macs; Anaconda Powershell or equivalent on Windows), navigate to this folder's directory (cd /path/to/folder). Install the needed packages by running:

**pip install -r requirements.txt**

Open the US_GUI.py program and hit run. You should see the following: 
<img width="216" alt="Screenshot 2024-02-09 at 4 12 07 PM" src="https://github.com/jkosnoff/phantom_US_toolbox/assets/70274595/a54806d8-37f4-4aac-a26b-ae24605c9d08">

Copy and paste the path to your tdms file into the box (on a Mac, you can get your file path by navigating to the file in Finder > option + right click > Copy __ as Path Name). **IMPORTANT: DO NOT CHANGE THE TDMS FILE NAME** This script has been designed to parse through the file name to extract the important information embedded into it. 

Click on "Parse File." You should see something similar to the following, where the values and names are replaced with your specific experimental parameters. The one exception (currently) is the input mV parameter may need to be manually input. I will look to resolve this bug in the future. Stay tuned for future updates 🙌.

