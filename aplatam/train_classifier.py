import glob
import os
from keras import applications
from keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras.models import Sequential, Model
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping


def train(trainable_layers, output_model, batch_size, epochs):
    train_files = glob.glob(
        os.path.join('data_keras/', 'train_hires_balanced/**/', '*.jpg'))
    validation_files = glob.glob(
        os.path.join('data_keras/', 'validation_hires_balanced/**/', '*.jpg'))
    img_width, img_height = 256, 256
    train_data_dir = "data_keras/train_hires_balanced"
    validation_data_dir = "data_keras/validation_hires_balanced"
    nb_train_samples = len(train_files)
    nb_validation_samples = len(validation_files)
    #nb_true_train_files = len(glob.glob(os.path.join('data_keras/','train_hires_balanced/vya', '*.jpg')))
    #class_weights = { 0: 1., 1: round((nb_train_samples - nb_true_train_files)/nb_true_train_files)}
    #print(class_weights)

    model = model_width_height(img_width, img_height)

    model_layer(model, trainable_layers)

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
                trainable_layers)


def model_width_height(img_width, img_height):
    """model  """
    model = applications.resnet50.ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(img_width, img_height, 3))
    return model


def train_model(model_final, train_generator, nb_train_samples, batch_size,
                epochs, validation_generator, nb_validation_samples, early,
                trainable_layers):
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
    model_final.save('/models/hires_aug_1_{}.h5'.format(trainable_layers))
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
        save_to_dir='/tmp/keras',
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


def model_layer(model, trainable_layers):
    """Freeze the layers which you don't want to train. Here I am freezing the first 5 layers"""
    i = 0
    for layer in model.layers[:(174 - int(trainable_layers))]:
        layer.trainable = False
    for layer in model.layers:
        print(layer.name, layer.trainable)
        i += 1
    print(model.summary())
    print(i)
