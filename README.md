NETPerfTrace
============
NetPerfTrace - an Internet Path Tracking system - is a tool capable of forecasting path changes and path latency variations.

More precisely, NETPerfTrace aims at predicting 3 metrics:
* **the residual life time of a route** (i.e. the remaining life time of the route before it actually changes)
* **the number of route changes in the next time-slot**: 
* **the average RTT of the next traceroute sample**

The current implementation of NETPerfTrace relies on a Random Forest with 10 trees for the prediction tasks.

###How to use NETPerfTrace
NETPerfTrace has been implemented using Python 2.7. For the machine-learning part, this tool bases on [scikit-learn](http://scikit-learn.org/stable/). 
To install scikit-learn, please follow [these instructions](http://scikit-learn.org/stable/install.html)

To launch NETPerfTrace, simply run the command

`python prediction.py -o <observationTime> -t <timeslotDuration>`

**_where:_**
* `-o <observationTime>`: Duration in hours of the observation time; i.e. the time spanned by the samples used as observation (training) data
* `-t <timeslotDuration>`: Duration in hours of a time-slot; i.e. the duration of the time windows in which the observation period will be subdivided.

#### Structure

NETPerfTrace is structured into 5 folders:
- **docs**: contains .rst files explaining how to use NETPerfTrace
- **input**: should include the files used as input for NETPerfTrace
- **logs**: includes log-files
- **output**: the result-files generated by NETPerfTrace are saved into this folder
- **scripts**: includes all the Python-scripts

#### List of scripts

- **prediction.py**: launches the prediction process 
- **feature_extraction.py**: extracts the features from the data for forecasting Internet path dynamics and performance

Acknowledgement
---------------
This work has been partially funded by the Vienna Science and Technology Fund (WWTF) through project ICT15-129, [“BigDAMA”.](https://bigdama.ait.ac.at/)

<a href="https://bigdama.ait.ac.at/"><img src="https://bigdama.ait.ac.at/wp-content/uploads/2016/06/bigdama_logo_jpg.jpg" width="200" alt="BigDAMA"></a>

Authors
-------

* Main author: **Sarah Wassermann** - [homepage](http://wassermann.lu)
* Contributors: 
    * **Pedro Casas** - [homepage](http://pcasas.info/)
    * **Thibaut Cuvelier** - [homepage](http://www.montefiore.ulg.ac.be/~tcuvelier/)