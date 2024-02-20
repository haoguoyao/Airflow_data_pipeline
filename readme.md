pip install -r requirements.txt

Add this to Airflow.cfg
allowed_deserialization_classes = ['airflow.*','coco.coco_models.*']

To run Airflow
source path.sh


Installation / Prerequisites
## Install Airflow
```
pip install 'apache-airflow==2.8.1' \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.8.txt"
```
You may need to change the python version based on the python version you have.

# Start an airflow database
* First, export the current dir as the AIRFLOW_HOME variable:
```
export AIRFLOW_HOME=/path/to/your/airflow
```

* Then start the db:
```
airflow db init
```
* To start the server: 
```
airflow webserver -p 8080
```
To test, if you are using liux, just open a browser with 
```
http://0.0.0.0:8080
```
If you are using a WSL on windows, then use this command to find your IP and open it in a browser:
```
hostname -I
172.20.94.71 
```
```
http://172.20.94.71:8080/login/
```

* To start the schedular:
```
airflow scheduler
```

* To unpause a dag:
```
airflow dags unpause my_dag
```


# Login
* Create a user:
```
airflow users create --help
```
example:
```
airflow users create --username admin --firstname Guoyao --lastname Hao --role Admin --email ghao004@gmail.com
```

