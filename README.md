NETPerfTrace
============

NetPerfTrace — an Internet Path Tracking system — is a tool capable of forecasting path changes and path latency variations.

More precisely, NETPerfTrace aims at predicting 3 metrics:
* **the residual life time of a route** (i.e. the remaining life time of the route before it actually changes)
* **the number of route changes in the next time-slot**
* **the average RTT of the next traceroute sample**

The current implementation of NETPerfTrace relies on a random forest with 10 trees for the prediction tasks.

### How to use NETPerfTrace

NETPerfTrace has been implemented using Python 2.7. For the machine-learning part, this tool is based on [scikit-learn](http://scikit-learn.org/stable/). 
To install scikit-learn, please follow [the instructions on the official website](http://scikit-learn.org/stable/install.html). 

To launch NETPerfTrace, simply run the command: 

`python prediction.py -o <observationTime> -t <timeslotDuration>`

**_where:_**
* `-o <observationTime>`: Duration in hours of the observation time; i.e. the time spanned by the samples used as observation (training) data
* `-t <timeslotDuration>`: Duration in hours of a time slot; i.e. the duration of the time windows in which the observation period will be subdivided.

#### Structure

NETPerfTrace is structured into 5 folders:
- **docs**: contains .rst files explaining how to use NETPerfTrace
- **input**: should include the files used as input for NETPerfTrace
- **logs**: includes the log files
- **output**: the result files generated by NETPerfTrace are saved into this folder
- **scripts**: includes all the Python scripts

##### Format of input files for NETPerfTrace
The files serving as input for NETPerfTrace should meet the following requirements:
- Each file should contain the traceroutes for one path (i.e. for one (source, destination) tuple)
- Each traceroute in these files should be formatted as follows:
``SOURCE:<tab><IP>``

``DESTINATION:<tab><IP>``

``TIMESTAMP:<tab><timestamp in the format YYYYMMDDThh:mm:ss>``

``HOP:<tab><IP><tab><minRTT><tab><avgRTT><tab><maxRTT><tab><mdevRTT>``

``...``

``HOP:<tab><IP><tab><minRTT><tab><avgRTT><tab><maxRTT><tab><mdevRTT>``

``END``

#### List of scripts

- **prediction.py**: launches the prediction process 
- **feature_extraction.py**: extracts the features from the data for forecasting Internet path dynamics and performance


Acknowledgement
---------------

This work has been partially funded by the Vienna Science and Technology Fund (WWTF) through project ICT15-129, [“BigDAMA”](https://bigdama.ait.ac.at/).

 [![BigDAMA](docs/bigdama.png)](https://bigdama.ait.ac.at/)

Authors
-------

* Main author: **Sarah Wassermann** - [homepage](http://wassermann.lu)
* Contributors: 
    * **Pedro Casas** - [homepage](http://pcasas.info/)
    * **Thibaut Cuvelier** - [homepage](http://www.montefiore.ulg.ac.be/~tcuvelier/)
