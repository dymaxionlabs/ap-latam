import glob
import os
from keras import applications
from keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras.models import Sequential, Model
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
import logging

RESNET_50_LAYERS = 174

_logger = logging.getLogger(__name__)


def train(trainable_layers, output_model, batch_size, epochs, size,
          dataset_dir):

    train_data_dir = os.path.join(dataset_dir, "train")

    train_files = glob.glob(os.path.join(train_data_dir, "**", "*.jpg"))

    validation_data_dir = os.path.join(dataset_dir, "validation")

    validation_files = glob.glob(
        os.path.join(validation_data_dir, "**", "*.jpg"))

    nb_train_samples = len(train_files)

    nb_validation_samples = len(validation_files)

    img_width, img_height = size, size
    #nb_true_train_files = len(glob.glob(os.path.join('data_keras/','train_hires_balanced/vya', '*.jpg')))
    #class_weights = { 0: 1., 1: round((nb_train_samples - nb_true_train_files)/nb_true_train_files)}
    #print(class_weights)

    model = build_resnet50_model(img_width, img_height)

    freeze_layers(model, trainable_layers)

    predictions = adding_custom_ayers(model)

    # creating the final model
    model_final = Model(inputs=model.input, outputs=predictions)

    compile_model(model_final)

    train_datagen = ImageDataGenerator(rescale=1. / 255, horizontal_flip=True)

    test_datagen = ImageDataGenerator(rescale=1. / 255, horizontal_flip=True)

    train_generator = train_data_generator(train_datagen, train_data_dir,
                                           img_height, img_width, batch_size)

    validation_generator = validation_data_generator(
        test_datagen, validation_data_dir, img_height, img_width)

    # Save the model according to the conditions
    #checkpoint = ModelCheckpoint("vgg16_1.h5",
    #        monitor = 'val_acc',
    #        verbose = 1,
    #        save_best_only = True,
    #        save_weights_only = False,
    #        mode = 'auto',
    #        period = 1)
    early = EarlyStopping(
        monitor='val_acc', min_delta=0, patience=10, verbose=1, mode='auto')

    # Train the model
    train_model(model_final, train_generator, nb_train_samples, batch_size,
                epochs, validation_generator, nb_validation_samples, early,
                trainable_layers, output_model)


def build_resnet50_model(img_width, img_height):
    """Build a ResNet-50 model"""
    return applications.resnet50.ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(img_width, img_height, 3))


def train_model(model_final, train_generator, nb_train_samples, batch_size,
                epochs, validation_generator, nb_validation_samples, early,
                trainable_layers, output_model):
    """Train the model"""
    model_final.fit_generator(
        train_generator,
        steps_per_epoch=nb_train_samples // batch_size,
        epochs=epochs,
        #class_weight = class_weights,
        validation_data=validation_generator,
        validation_steps=nb_validation_samples // batch_size,
        callbacks=[early])

    # Finally, save model
    model_final.save(output_model)
    print('Done with {} layers'.format(trainable_layers))


def validation_data_generator(test_datagen, validation_data_dir, img_height,
                              img_width):
    """Initiate the test generators with data Augumentation"""
    validation_generator = test_datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_height, img_width),
        class_mode="binary")
    return validation_generator


def train_data_generator(train_datagen, train_data_dir, img_height, img_width,
                         batch_size):
    """Initiate the train generators with data Augumentation"""
    train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_height, img_width),
        batch_size=batch_size,
        class_mode="binary")
    return train_generator


def compile_model(model_final):
    """compile the model"""
    model_final.compile(
        loss='binary_crossentropy',
        optimizer=optimizers.SGD(lr=0.0001, momentum=0.9),
        metrics=['accuracy'])


def adding_custom_ayers(model):
    """Adding custom Layers"""
    x = model.output
    x = Flatten()(x)
    x = Dense(1024, activation="relu")(x)
    x = Dropout(0.5)(x)
    predictions = Dense(1, activation="sigmoid")(x)
    return predictions


def freeze_layers(model, trainable_layers):
    """Make the last +trainable_layers+ in model trainable by freezing the others"""
    assert trainable_layers < RESNET_50_LAYERS

    for layer in model.layers[:(RESNET_50_LAYERS - trainable_layers)]:
        layer.trainable = False
    for layer in model.layers:
        _logger.debug('Layer %s is trainable: %s', layer.name, layer.trainable)
    _logger.debug('Model summary: %s', model.summary())


def write_geojson(shapes, output_path):
    d = {'type': 'FeatureCollection', 'features': []}
    for shape in shapes:
        feat = {'type': 'Feature', 'geometry': mapping(shape)}
        d['features'].append(feat)
    with open(output_path, 'w') as f:
        f.write(json.dumps(d))
