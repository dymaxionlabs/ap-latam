from glob import glob
import logging
import os

from keras import applications, optimizers
from keras.callbacks import EarlyStopping
from keras.layers import Dense, Dropout, Flatten
from keras.models import Model
from keras.preprocessing.image import ImageDataGenerator

RESNET_50_LAYERS = 174

_logger = logging.getLogger(__name__)


def train(output_model_file, dataset_dir, *, trainable_layers, batch_size,
          epochs, size):

    train_data_dir = os.path.join(dataset_dir, 'train')
    validation_data_dir = os.path.join(dataset_dir, 'validation')

    train_files = glob(os.path.join(train_data_dir, '**', '*.jpg'))
    validation_files = glob(os.path.join(validation_data_dir, '**', '*.jpg'))

    nb_train_samples = len(train_files)
    nb_validation_samples = len(validation_files)

    img_width, img_height = size, size

    assert size >= 197, \
        'image size must be at least 197x197, but was {size}x{size}'.format(size=size)

    # Build model using ResNet-50 as base input
    base_model = build_resnet50_model(img_width, img_height)
    freeze_layers(base_model, trainable_layers)
    outputs = add_custom_layers(base_model)
    model = Model(inputs=base_model.input, outputs=outputs)
    compile_model(model)

    # Prepare data generators for training and test sets
    train_datagen = ImageDataGenerator(rescale=1. / 255, horizontal_flip=True)
    test_datagen = ImageDataGenerator(rescale=1. / 255, horizontal_flip=True)

    train_generator = train_data_generator(train_datagen, train_data_dir,
                                           img_height, img_width, batch_size)
    validation_generator = validation_data_generator(
        test_datagen, validation_data_dir, img_height, img_width)

    # Configure early stopping to monitor validation accuracy
    early_stopping = EarlyStopping(
        monitor='val_acc', min_delta=0, patience=10, verbose=1, mode='auto')

    # Start training model
    train_model(
        model,
        train_generator=train_generator,
        train_samples=nb_train_samples,
        validation_generator=validation_generator,
        validation_samples=nb_validation_samples,
        batch_size=batch_size,
        epochs=epochs,
        early_stopping=early_stopping)
    _logger.info('Training completed')

    # Finally, save model to a file
    model.save(output_model_file)
    _logger.info('Model saved as %s', output_model_file)


def build_resnet50_model(img_width, img_height):
    """Build a ResNet-50 model"""
    return applications.resnet50.ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(img_width, img_height, 3))


def train_model(model, *, train_generator, validation_generator, train_samples,
                validation_samples, batch_size, epochs, early_stopping):
    """Train model"""
    model.fit_generator(
        train_generator,
        steps_per_epoch=train_samples // batch_size,
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=validation_samples // batch_size,
        callbacks=[early_stopping])


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


def compile_model(model):
    """Compile model by setting optimizer and loss function"""
    model.compile(
        loss='binary_crossentropy',
        optimizer=optimizers.SGD(lr=0.0001, momentum=0.9),
        metrics=['accuracy'])


def add_custom_layers(model):
    """Adding custom Layers"""
    model = model.output
    model = Flatten()(model)
    model = Dense(1024, activation='relu')(model)
    model = Dropout(0.5)(model)
    model = Dense(1, activation='sigmoid')(model)
    return model


def freeze_layers(model, trainable_layers):
    """Make the last +trainable_layers+ in model trainable by freezing the others"""
    assert trainable_layers < RESNET_50_LAYERS

    for layer in model.layers[:(RESNET_50_LAYERS - trainable_layers)]:
        layer.trainable = False
    for layer in model.layers:
        _logger.debug('Layer %s is trainable: %s', layer.name, layer.trainable)
    _logger.debug('Model summary: %s', model.summary())
