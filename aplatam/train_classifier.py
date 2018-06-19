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

    true_train_files = glob(os.path.join(train_data_dir, 't', '*.jpg'))
    false_train_files = glob(os.path.join(train_data_dir, 'f', '*.jpg'))
    train_files = true_train_files + false_train_files
    validation_files = glob(os.path.join(validation_data_dir, '**', '*.jpg'))

    nb_true_train_samples = len(true_train_files)
    nb_false_train_samples = len(false_train_files)
    nb_train_samples = len(train_files)
    nb_validation_samples = len(validation_files)

    img_width, img_height = size, size

    assert size >= 197, \
        'image size must be at least 197x197, but was {size}x{size}'.format(size=size)

    class_weight = {
        0: 1.,
        1: round(nb_false_train_samples / nb_true_train_samples)
    }
    _logger.info('Class weight: %s', class_weight)

    # Build model using ResNet-50 as base input
    base_model = build_resnet50_model(img_width, img_height)
    freeze_layers(base_model, trainable_layers)
    outputs = add_custom_layers(base_model)
    model = Model(inputs=base_model.input, outputs=outputs)
    compile_model(model)

    # Prepare data generators for training and test sets
    opts = dict(horizontal_flip=True,
                preprocessing_function=applications.resnet50.preprocess_input)
    train_datagen = ImageDataGenerator(**opts)
    test_datagen = ImageDataGenerator(**opts)

    train_generator = train_data_generator(train_datagen, train_data_dir,
                                           img_height, img_width, batch_size)
    validation_generator = validation_data_generator(
        test_datagen, validation_data_dir, img_height, img_width, batch_size)

    # Start training model
    train_model(
        model,
        train_generator=train_generator,
        train_samples=nb_train_samples,
        validation_generator=validation_generator,
        validation_samples=nb_validation_samples,
        class_weight=class_weight,
        batch_size=batch_size,
        epochs=epochs)
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
                class_weight, validation_samples, batch_size, epochs):
    """Train model"""

    # Configure early stopping to monitor validation accuracy
    early_stopping = EarlyStopping(
        monitor='val_acc', min_delta=0, patience=10, verbose=1, mode='auto')

    model.fit_generator(
        train_generator,
        steps_per_epoch=train_samples // batch_size,
        epochs=epochs,
        class_weight=class_weight,
        validation_data=validation_generator,
        validation_steps=validation_samples // batch_size,
        callbacks=[early_stopping])


def validation_data_generator(test_datagen, validation_data_dir, img_height,
                              img_width, batch_size):
    """Initiate the test generators with data Augumentation"""
    validation_generator = test_datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_height, img_width),
        batch_size=batch_size,
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
    out = model.output
    out = Flatten()(out)
    out = Dense(1024, activation='relu')(out)
    out = Dropout(0.5)(out)
    out = Dense(1, activation='sigmoid')(out)
    return out


def freeze_layers(model, trainable_layers):
    """Make the last +trainable_layers+ in model trainable by freezing the others"""
    assert trainable_layers < RESNET_50_LAYERS

    for layer in model.layers[:(RESNET_50_LAYERS - trainable_layers)]:
        layer.trainable = False
    for layer in model.layers:
        _logger.debug('Layer %s is trainable: %s', layer.name, layer.trainable)
    _logger.debug('Model summary: %s', model.summary())
