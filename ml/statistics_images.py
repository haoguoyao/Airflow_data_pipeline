import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from db.db_models import AnnotationDB,Annotation_predictionDB
# from db.db_connections import get_db_session
from db.db_operations import get_objects_in_batches_from_db,get_random_objects_from_db,get_fields_from_db





def plot_areas_histogram():
    areas = get_fields_from_db(AnnotationDB.area)
    plt.figure(figsize=(10, 6))
    plt.hist(areas, bins=50, log=True)
    plt.title('Histogram of Annotation Areas')
    plt.xlabel('Area')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('ml_model/statistics_plots/annotation_areas_chart.png')
    plt.close()
def plot_prediction_confidence_histogram():
    areas = get_fields_from_db(Annotation_predictionDB.confidence)
    plt.figure(figsize=(10, 6))
    plt.hist(areas, bins=20, log=True)
    plt.title('Histogram of Prediction Confidence')
    plt.xlabel('confidence')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('ml_model/statistics_plots/annotation_prediction_confidence_chart.png')
    plt.close()
if __name__ == "__main__":

    plot_prediction_confidence_histogram()