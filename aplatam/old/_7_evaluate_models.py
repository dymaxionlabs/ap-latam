import csv
import glob
import os
from os.path import splitext

import fiona
import rtree


def evaluate(ground_truth, predictions, prob):

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    with fiona.open(ground_truth, 'r') as vya_layer:
        with fiona.open(predictions, 'r') as pred_vya_layer:
            # We copy schema and add the  new property for the new resulting shp
            index = rtree.index.Index()
            for feature_true in vya_layer:
                fid_true = int(feature_true['id'])
                geom_true = shape(feature_true['geometry'])
                index.insert(fid_true, geom_true.bounds)

            for feature_pred in pred_vya_layer:
                geom_pred = shape(feature_pred['geometry'])
                fid_pred_id = int(feature_pred['id'])
                ids_intersect = [
                    vya_layer[f_id]
                    for f_id in index.intersection(geom_pred.bounds)
                ]
                if any(ids_intersect):
                    if feature_pred['properties']['prob'] > prob:
                        tp += 1
                    else:
                        fn += 1
                else:
                    if feature_pred['properties']['prob'] > prob:
                        fp += 1
                    else:
                        tn += 1

    return {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn}


def evaluate_models(dir_model, output, ground_truth):
    d = {}
    probas = [0.3, 0.5, 0.7, 0.9]
    predictions_files = glob.glob(os.path.join(dir_model, '*.geojson'))
    for prediction in predictions_files:
        for prob in probas:
            file_name, extension = splitext(os.path.basename(prediction))
            model_name = file_name + '_{}'.format(str(prob))
            d[model_name] = evaluate(ground_truth, prediction, prob)
            print('OK {} with {} proba'.format(file_name, prob))
    import csv
    with open(output, "w") as csv_file:
        fields = ['model', 'tp', 'tn', 'fp', 'fn']
        writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerow(fields)
        for key in d.keys():
            values = list(d[key].values())
            values.insert(0, key)
            writer.writerow(values)
    print('Done with {} models'.format(len(d.keys())))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Evaluate a batch of models using confusion matrix',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('dir_models', help='Dir with geojson files')
    parser.add_argument(
        'output_file', help='Output filename with model evaluations')
    parser.add_argument('ground_truth', help='VyA dataset')
    args = parser.parse_args()

    evaluate_models(args.dir_models, args.output_file, args.ground_truth)
